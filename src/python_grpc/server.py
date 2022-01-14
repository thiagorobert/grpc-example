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
    parser.add_argument(
        '--cert_path', dest='cert_path', default=None, help='path to certificate file')
    parser.add_argument(
        '--private_key_path', dest='private_key_path', default=None,
        help='path to private key file')
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


# See https://www.sandtable.com/using-ssl-with-grpc-in-python/
# and https://grpc.io/docs/guides/auth/
def getCredentials(cert_path, private_key_path):
    # Read key and certificate.
    with open(private_key_path, 'rb') as f:
        private_key = f.read()
    with open(cert_path, 'rb') as f:
        certificate_chain = f.read()

    # Create credentials.
    creds = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)])
    return creds


# See https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
def enableReflectionAPI(server):
    service_names = (
        pb2.DESCRIPTOR.services_by_name['Unary'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)


def serve(server_port, cert_path, private_key_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    enableReflectionAPI(server)

    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)

    if cert_path:
        server.add_secure_port('[::]:' + server_port,
                               getCredentials(cert_path, private_key_path))
    else:
        server.add_insecure_port('[::]:' + server_port)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    flags = inputFlags()

    print(f'\nServer listening at ":{flags.server_port}"')
    if flags.cert_path:
        if not flags.private_key_path:
            print(f'--private_key_path required with --cert_path')
            sys.exit(-1)
        print(f'\tusing cert: {flags.cert_path}')
        print(f'\tusing private key: {flags.private_key_path}')

    serve(flags.server_port, flags.cert_path, flags.private_key_path)
