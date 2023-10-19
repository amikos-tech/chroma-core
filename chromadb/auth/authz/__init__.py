import logging
from typing import Any, Dict, cast
from overrides import override
import yaml
from chromadb.auth import (
    AuthorizationContext,
    ServerAuthorizationConfigurationProvider,
    ServerAuthorizationProvider,
)
from chromadb.auth.registry import register_provider, resolve_provider
from chromadb.config import System

logger = logging.getLogger(__name__)


@register_provider("local_authz_config")
class LocalUserConfigAuthorizationConfigurationProvider(
    ServerAuthorizationConfigurationProvider[Dict[str, Any]]
):
    _config_file: str
    _config: Dict[str, Any]

    def __init__(self, system: System) -> None:
        super().__init__(system)
        self._settings = system.settings
        system.settings.require("chroma_server_authz_config_file")
        self._config_file = str(
            system.settings.chroma_server_authz_config_file)
        with open(self._config_file, "r") as f:
            self._config = yaml.safe_load(f)

    @override
    def get_configuration(self) -> Dict[str, Any]:
        return self._config


@register_provider("simple_rbac")
class SimpleRBACAuthorizationProvider(ServerAuthorizationProvider):
    _authz_config_provider: ServerAuthorizationConfigurationProvider[Dict[str, Any]]

    def __init__(self, system: System) -> None:
        super().__init__(system)
        self._settings = system.settings
        system.settings.require("chroma_server_authz_config_provider")
        if self._settings.chroma_server_authz_config_provider:
            _cls = resolve_provider(
                self._settings.chroma_server_authz_config_provider,
                ServerAuthorizationConfigurationProvider
            )
            self._authz_config_provider = cast(
                ServerAuthorizationConfigurationProvider, self.require(_cls))
            _config = self._authz_config_provider.get_configuration()
            self._authz_tuples = []
            for u in _config["users"]:
                _actions = _config["roles_mapping"][u["role"]]["actions"]
                for a in _actions:
                    self._authz_tuples.append((u["id"], *a.split(":")))
            logger.debug(f"Loaded {len(self._authz_tuples)} permissions for "
                         f"({len(_config['users'])}) users")
        logger.info(
            "Authorization Provider SimpleRBACAuthorizationProvider initialized")

    @override
    def authorize(self, context: AuthorizationContext) \
            -> bool:
        _authz_tuple = (context.user.id,
                        context.resource.type,
                        context.action.id)

        policy_decision = False
        if _authz_tuple in self._authz_tuples:
            policy_decision = True
        logger.debug(f"Authorization decision: Access "
                     f"{'granted' if policy_decision else 'denied'} for "
                     f"user [{context.user.id}] attempting to [{context.action.id}]"
                     f" on [{context.resource}]")
        return policy_decision