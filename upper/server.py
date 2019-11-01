from concurrent import futures
import time
import grpc
from .HelloWorld_pb2_grpc import GreeterServicer, add_GreeterServicer_to_server
from .HelloWorld_pb2 import HelloReply


class ServiceImpl(GreeterServicer):
    def SayHello(self, request_iterator, context):
        for request in request_iterator:
            yield HelloReply(message=request.name.upper(), id=request.id)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    server.add_insecure_port("127.0.0.1:7000")
    add_GreeterServicer_to_server(ServiceImpl(), server)
    server.start()
    print(">>>> Greeter service is started")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    serve()
            
