import chromadb.server.grpc.services.default_service_pb2 as default_service_pb2
import chromadb.server.grpc.services.default_service_pb2_grpc as default_service_pb2_grpc

class YourService(default_service_pb2_grpc.DefaultServiceServicer):

    def Version(self, request, context):
        # implement your method
        return default_service_pb2_grpc.DefaultService.Version(request=request,target="test123")


if __name__ == '__main__':
    import grpc
    from concurrent import futures

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    default_service_pb2_grpc.add_DefaultServiceServicer_to_server(YourService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
