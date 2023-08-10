import inspect
import traceback
from abc import ABC, abstractmethod


class BasePlugin(ABC):

    @abstractmethod
    def should_run(self, method_name: str) -> bool:
        """Determine if the plugin should be executed for the given method name."""
        pass

    @abstractmethod
    def before_request(self, method_name: str, *args, **kwargs):
        """Logic to run before the API method call"""
        pass

    @abstractmethod
    def after_request(self, method_name: str, result, *args, **kwargs):
        """Logic to run after the API method call"""
        pass


class PluginManager:
    def __init__(self):
        self.plugins = []

    def register_plugin(self, plugin: BasePlugin):
        """Registers a plugin with the API"""
        self.plugins.append(plugin)

    def execute_before_request(self, method_name: str, *args, **kwargs):
        """Execute registered plugins' before_request hook."""
        for plugin in self.plugins:
            if plugin.should_run(method_name):
                try:
                    plugin.before_request(method_name, *args, **kwargs)
                except Exception as e:
                    traceback.print_exc()
                    print(f"Error executing before_request hook for plugin {plugin.__class__.__name__}: {e}")

    def execute_after_request(self, method_name: str, result, *args, **kwargs):
        """Execute registered plugins' after_request hook."""
        for plugin in self.plugins:
            if plugin.should_run(method_name):
                try:
                    plugin.after_request(method_name, result, *args, **kwargs)
                except Exception as e:
                    traceback.print_exc()
                    print(f"Error executing after_request hook for plugin {plugin.__class__.__name__}: {e}")


from functools import wraps


def has_args_kwargs(func):
    sig = inspect.signature(func)
    has_args = False
    has_kwargs = False
    print(sig)
    for param in sig.parameters.values():
        print(param.kind)
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            has_args = True
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            has_kwargs = True

    return has_args, has_kwargs

def with_plugins(method):
    """Decorator to execute plugins before and after the method call"""

    @wraps(method)  # This ensures the decorated function retains its metadata
    def wrapper(api_instance, *args, **kwargs):
        if len(kwargs) ==0:
            kwargs = {}
        api_instance.plugin_manager.execute_before_request(method.__name__, *args, **kwargs)
        result = method(api_instance, *args, **kwargs)
        api_instance.plugin_manager.execute_after_request(method.__name__, result, *args, **kwargs)
        return result

    return wrapper
