# FAST API code
from contextvars import ContextVar
from functools import wraps
import logging
from typing import Callable, Optional, Dict, List, Union, cast, Any

from overrides import override
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from chromadb.config import System
from chromadb.auth import (
    AuthorizationContext,
    AuthorizationError,
    AuthorizationRequestContext,
    AuthzAction,
    AuthzResource,
    AuthzUser,
    DynamicAuthzResource,
    ServerAuthenticationRequest,
    AuthInfoType,
    ServerAuthenticationResponse,
    ServerAuthProvider,
    ChromaAuthMiddleware,
    ChromaAuthzMiddleware,
    ServerAuthorizationProvider,
)
from chromadb.auth.registry import resolve_provider

logger = logging.getLogger(__name__)


class FastAPIServerAuthenticationRequest(ServerAuthenticationRequest[Optional[str]]):
    def __init__(self, request: Request) -> None:
        self._request = request

    @override
    def get_auth_info(
        self, auth_info_type: AuthInfoType, auth_info_id: str
    ) -> Optional[str]:
        if auth_info_type == AuthInfoType.HEADER:
            return str(self._request.headers[auth_info_id])
        elif auth_info_type == AuthInfoType.COOKIE:
            return str(self._request.cookies[auth_info_id])
        elif auth_info_type == AuthInfoType.URL:
            return str(self._request.query_params[auth_info_id])
        elif auth_info_type == AuthInfoType.METADATA:
            raise ValueError("Metadata not supported for FastAPI")
        else:
            raise ValueError(f"Unknown auth info type: {auth_info_type}")


class FastAPIServerAuthenticationResponse(ServerAuthenticationResponse):
    _auth_success: bool

    def __init__(self, auth_success: bool) -> None:
        self._auth_success = auth_success

    @override
    def success(self) -> bool:
        return self._auth_success


class FastAPIChromaAuthMiddleware(ChromaAuthMiddleware):
    _auth_provider: ServerAuthProvider

    def __init__(self, system: System) -> None:
        super().__init__(system)
        self._system = system
        self._settings = system.settings
        self._settings.require("chroma_server_auth_provider")
        self._ignore_auth_paths: Dict[
            str, List[str]
        ] = self._settings.chroma_server_auth_ignore_paths
        if self._settings.chroma_server_auth_provider:
            logger.debug(
                f"Server Auth Provider: {self._settings.chroma_server_auth_provider}"
            )
            _cls = resolve_provider(
                self._settings.chroma_server_auth_provider, ServerAuthProvider
            )
            self._auth_provider = cast(ServerAuthProvider, self.require(_cls))

    @override
    def authenticate(
        self, request: ServerAuthenticationRequest[Any]
    ) -> ServerAuthenticationResponse:
        return self._auth_provider.authenticate(request)

    @override
    def ignore_operation(self, verb: str, path: str) -> bool:
        if (
            path in self._ignore_auth_paths.keys()
            and verb.upper() in self._ignore_auth_paths[path]
        ):
            logger.debug(f"Skipping auth for path {path} and method {verb}")
            return True
        return False

    @override
    def instrument_server(self, app: ASGIApp) -> None:
        # We can potentially add an `/auth` endpoint to the server to allow for more
        # complex auth flows
        return


class FastAPIChromaAuthMiddlewareWrapper(BaseHTTPMiddleware):  # type: ignore
    def __init__(
        self, app: ASGIApp, auth_middleware: FastAPIChromaAuthMiddleware
    ) -> None:
        super().__init__(app)
        self._middleware = auth_middleware
        self._middleware.instrument_server(app)

    @override
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._middleware.ignore_operation(request.method, request.url.path):
            logger.debug(
                f"Skipping auth for path {request.url.path} and method {request.method}"
            )
            return await call_next(request)
        response = self._middleware.authenticate(
            FastAPIServerAuthenticationRequest(request)
        )
        if not response or not response.success():
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        request.state.user_identity = response.get_user_identity()
        return await call_next(request)

# AuthZ


request_var: ContextVar[Optional[Request]] = ContextVar(
    "request_var", default=None)
authz_provider: ContextVar[Optional[ServerAuthorizationProvider]] = ContextVar(
    "authz_provider", default=None)


def authz_context(action: Union[str, AuthzAction],
                  resource: Union[AuthzResource, DynamicAuthzResource]) \
        -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapped(*args, ** kwargs):
            _dynamic_kwargs = {"function": f,
                               "function_args": args, "function_kwargs": kwargs}
            # print(args[0]._authz_provider)
            # args[0]._authz_provider.authorize()
            request = request_var.get()
            if request:
                _action = action if isinstance(
                    action, AuthzAction) else AuthzAction(id=action)
                _resource = resource if isinstance(
                    resource, AuthzResource) else \
                    resource.to_authz_resource(**_dynamic_kwargs)
                _context = AuthorizationContext(
                    user=AuthzUser(
                        id=request.state.user_identity.get_user_id()
                        if hasattr(request.state, "user_identity") else "Anonymous"),
                    resource=_resource,
                    action=_action,
                )
                _provider = authz_provider.get()
                if _provider:
                    _response = _provider.authorize(_context)
                    if not _response:
                        raise AuthorizationError("Unauthorized")
            return f(*args, **kwargs)
        return wrapped
    return decorator


class FastAPIAuthorizationRequestContext(AuthorizationRequestContext[Request]):
    _request: Request

    def __init__(self, request: Request) -> None:
        self._request = request
        pass

    @override
    def get_request(self) -> Request:
        return self._request


class FastAPIChromaAuthzMiddleware(ChromaAuthzMiddleware[ASGIApp]):
    _authz_provider: ServerAuthorizationProvider

    def __init__(self, system: System) -> None:
        super().__init__(system)
        self._system = system
        self._settings = system.settings
        self._settings.require("chroma_server_authz_provider")
        self._ignore_auth_paths: Dict[
            str, List[str]
        ] = self._settings.chroma_server_authz_ignore_paths
        if self._settings.chroma_server_authz_provider:
            logger.debug(
                "Server Authorization Provider: "
                f"{self._settings.chroma_server_authz_provider}"
            )
            _cls = resolve_provider(
                self._settings.chroma_server_authz_provider, ServerAuthorizationProvider
            )
            self._authz_provider = cast(
                ServerAuthorizationProvider, self.require(_cls))

    @override
    def pre_process(
        self, request: AuthorizationRequestContext
    ) -> None:
        rest_request = request.get_request()
        request_var.set(rest_request)
        authz_provider.set(self._authz_provider)

    @override
    def ignore_operation(self, verb: str, path: str) -> bool:
        if (
            path in self._ignore_auth_paths.keys()
            and verb.upper() in self._ignore_auth_paths[path]
        ):
            logger.debug(f"Skipping authz for path {path} and method {verb}")
            return True
        return False

    @override
    def instrument_server(self, app: ASGIApp) -> None:
        # We can potentially add an `/auth` endpoint to the server to allow
        # for more complex auth flows
        return


class FastAPIChromaAuthzMiddlewareWrapper(BaseHTTPMiddleware):  # type: ignore
    def __init__(
        self, app: ASGIApp, authz_middleware: FastAPIChromaAuthzMiddleware
    ) -> None:
        super().__init__(app)
        self._middleware = authz_middleware
        self._middleware.instrument_server(app)

    @override
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self._middleware.ignore_operation(request.method, request.url.path):
            logger.debug(
                f"Skipping authz for path {request.url.path} "
                "and method {request.method}"
            )
            return await call_next(request)
        self._middleware.pre_process(
            FastAPIAuthorizationRequestContext(request)
        )
        return await call_next(request)
