import argparse
import sys
import grpc
from grpc_reflection.v1alpha import reflection
from concurrent import futures
import time
import proto.unary_pb2_grpc as pb2_grpc
import proto.unary_pb2 as pb2


def inputFlags():
    parser = argparse.ArgumentParser(description='gRPC example server')
    parser.add_argument(
        '--server_port', dest='server_port', default='8080', help='server port')
    return parser.parse_args()


class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponse(self, request, context):

        # get the string from the incoming request
        message = request.message
        result = f'Hello I am up and running received "{message}" message from you'
        result = {'message': result, 'received': True}

        return pb2.MessageResponse(**result)


# See https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
def enableReflectionAPI(server):
    service_names = (
        pb2.DESCRIPTOR.services_by_name['Unary'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)


def serve(server_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    enableReflectionAPI(server)

    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)

    server.add_insecure_port('[::]:' + server_port)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    flags = inputFlags()

    print(f'Server listening at ":{flags.server_port}"')

    serve(flags.server_port)
