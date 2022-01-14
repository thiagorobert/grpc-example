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
    return parser.parse_args()


class UnaryClient(object):
    """gRPC client."""

    def __init__(self, server_host, server_port):
        host_port = '{}:{}'.format(server_host, server_port)

        # Instantiate channel.
        self.channel = grpc.insecure_channel(host_port)

        # Bind client and server.
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def Run(self, message):
        """Issues GetServerResponse RPC."""
        message = pb2.Message(message=message)
        return self.stub.GetServerResponse(message)


if __name__ == '__main__':
    flags = inputFlags()

    print(f'Client talking to "{flags.server_host}:{flags.server_port}"')

    client = UnaryClient(flags.server_host, flags.server_port)
    result = client.Run(message='Hello Server you there?')
    print(f'{result}')
