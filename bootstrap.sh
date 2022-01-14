#!/bin/sh

set -e

echo "starting gRPC server"
python3 src/python_grpc/server.py --cert_path tls_data/server.crt --private_key_path tls_data/server.key &

echo "starting REST API"
./rest_reverse_proxy --cert_path tls_data/server.crt
