import grpc
import chromadb.server.grpc.services.default_service_pb2 as default_service_pb2
import chromadb.server.grpc.services.default_service_pb2_grpc as default_service_pb2_grpc

def run_client():
    channel = grpc.insecure_channel('localhost:50051')
    stub = default_service_pb2_grpc.DefaultServiceStub(channel)

    response = stub.Version(default_service_pb2_grpc.DefaultService.Version())
    print(response)

if __name__ == "__main__":
    run_client()