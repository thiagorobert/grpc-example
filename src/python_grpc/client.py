import argparse
import sys
import grpc
import proto.unary_pb2_grpc as pb2_grpc
import proto.unary_pb2 as pb2


def inputFlags():
    parser = argparse.ArgumentParser(description='gRPC example client')
    parser.add_argument(
        '--server_host', dest='server_host', default='localhost', help='server host')
    parser.add_argument(
        '--server_port', dest='server_port', default='8080', help='server port')
    parser.add_argument(
        '--cert_path', dest='cert_path', default='', help='path to certificate file')
    return parser.parse_args()


class UnaryClient(object):
    """gRPC client."""

    def __init__(self, server_host, server_port, cert_path):
        host_port = '{}:{}'.format(server_host, server_port)

        # Instantiate channel.
        if cert_path:
            with open(cert_path, 'rb') as f:
                creds = grpc.ssl_channel_credentials(f.read())
            self.channel = grpc.secure_channel(host_port, creds)
        else:
            self.channel = grpc.insecure_channel(host_port)

        # Bind client and server.
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def Run(self, message):
        """Issues GetServerResponse RPC."""
        message = pb2.Message(message=message)
        return self.stub.GetServerResponse(message)


if __name__ == '__main__':
    flags = inputFlags()

    print(f'\nClient talking to "{flags.server_host}:{flags.server_port}"')
    if flags.cert_path:
        print(f'\tusing cert: {flags.cert_path}')

    client = UnaryClient(flags.server_host, flags.server_port, flags.cert_path)
    result = client.Run(message='Hello Server you there?')
    print(f'\n{result}')
