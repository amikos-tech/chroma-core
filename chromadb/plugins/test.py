import importlib

from chromadb import HttpClient
from chromadb.plugins import BasePlugin
from chromadb.utils import embedding_functions


class LoggingPlugin(BasePlugin):

    def should_run(self, method_name: str) -> bool:
        return method_name in ["heartbeat", "list_collections", "get_version"]

    def before_request(self, method_name: str, *args, **kwargs):
        print(f"Executing {method_name} with args: {args} and kwargs: {kwargs}")

    def after_request(self, method_name: str, result, *args, **kwargs):
        print(f"Executed {method_name} and received result: {result}")


class CollectionEmbeddingFunctionAnnotator(BasePlugin):
    def instantiate_class_from_name(self, full_name: str, *args, **kwargs):
        module_name, class_name = full_name.rsplit('.', 1)

        # Dynamically import the module
        module = importlib.import_module(module_name)

        # Fetch the class
        class_obj = getattr(module, class_name)

        # Instantiate and return the class
        return class_obj(*args, **kwargs)

    def should_run(self, method_name: str) -> bool:
        return method_name in ["create_collection", "get_collection"]

    def before_request(self, method_name: str, *args, **kwargs):
        if method_name == "create_collection":
            meta = kwargs.get("metadata", args[1])
            ef = kwargs.get("embedding_function")
            meta["embedding_function"] = f"{ef.__class__.__module__}.{ef.__class__.__name__}"
            meta["embedding_function_model"] = f"{list(ef.models.keys())[0]}"
        print(f"Executing {method_name} with args: {args} and kwargs: {kwargs}")

    def after_request(self, method_name: str, result, *args, **kwargs):
        if method_name == "get_collection":
            result._embedding_function = self.instantiate_class_from_name(result.metadata["embedding_function"],
                                                                          model_name=result.metadata[
                                                                              "embedding_function_model"])
        print(f"Executed {method_name} and received result: {result}")


class TextChunker(BasePlugin):

    def should_run(self, method_name: str) -> bool:
        return method_name in ["_add"]

    def before_request(self, method_name: str, *args, **kwargs):
        print(f"Executing {method_name} with args: {args} and kwargs: {kwargs}")

    def after_request(self, method_name: str, result, *args, **kwargs):
        print(f"Executed {method_name} and received result: {result}")


sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


def main():
    client = HttpClient(host="localhost", port="8000")
    client.plugin_manager.register_plugin(LoggingPlugin())
    client.plugin_manager.register_plugin(CollectionEmbeddingFunctionAnnotator())
    client.get_version()
    client.reset()

    collection = client.create_collection("test-collection", {"Test": "Test"},
                                          embedding_function=sentence_transformer_ef)
    updatedCol = client.get_collection("test-collection")
    print(updatedCol)


if __name__ == '__main__':
    main()
