FROM ubuntu:20.04

RUN apt-get update

# Install `tzdata` separately to avoid interactive input (see https://serverfault.com/questions/949991/how-to-install-tzdata-on-a-ubuntu-docker-image)
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

# Install dependencies.
RUN apt-get install -o Acquire::ForceIPv4=true -y \
    python3 \
    python3-pip \
    protobuf-compiler \
    wget

# Install a more recent version of Go (`apt-get install golang` yields 1.1 in this environment).
RUN wget https://storage.googleapis.com/golang/go1.17.5.linux-amd64.tar.gz
RUN tar -zxvf go1.17.5.linux-amd64.tar.gz -C /usr/local/
ENV PATH="/usr/local/go/bin:${PATH}"

# Install gRPC support in Python.
RUN pip install grpcio grpcio-tools
RUN pip install --upgrade protobuf

# Setup $GOBIN and add it to $PATH.
ENV GOBIN=/go/bin
RUN mkdir -p ${GOBIN}
ENV PATH="${GOBIN}:${PATH}"

# Setup code root directory.
ENV CODE_ROOT=/go/src/thiago.pub/grpc-example
RUN mkdir -p ${CODE_ROOT}

# Copy code.
COPY tools ${CODE_ROOT}/tools
COPY google ${CODE_ROOT}/google
COPY proto ${CODE_ROOT}/proto
COPY src ${CODE_ROOT}/src

# Install protoc-gen-go (see https://github.com/grpc-ecosystem/grpc-gateway/)
WORKDIR ${CODE_ROOT}/tools
RUN go mod init github.com/thiagorobert/grpc-example/go_proto_tools
RUN go mod tidy -compat=1.17
RUN go install \
  github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway \
  github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2 \
  google.golang.org/protobuf/cmd/protoc-gen-go \
  google.golang.org/grpc/cmd/protoc-gen-go-grpc

# Generate proto code, setup Go modules, and build Go code.
# See https://github.com/thiagorobert/grpc-example
WORKDIR ${CODE_ROOT}

RUN python3 -m grpc_tools.protoc \
  -I=. \
  --python_out=./src/python_grpc \
  --grpc_python_out=./src/python_grpc \
  ./google/api/http.proto ./google/api/annotations.proto \
  ./proto/unary.proto

RUN protoc \
  -I=. \
  --go_out ./src/go_rest_proxy/autogenerated/ --go_opt paths=source_relative \
  --go-grpc_out ./src/go_rest_proxy/autogenerated/ --go-grpc_opt paths=source_relative \
  --grpc-gateway_out ./src/go_rest_proxy/autogenerated/ \
  --grpc-gateway_opt logtostderr=true \
  --grpc-gateway_opt paths=source_relative \
  ./proto/unary.proto

# Setup required Go modules and build REST proxy.
WORKDIR ${CODE_ROOT}/src/go_rest_proxy/autogenerated/proto/
RUN go mod init github.com/thiagorobert/grpc-example/autogenerated_proto
RUN go mod tidy

WORKDIR ${CODE_ROOT}
RUN go mod init github.com/thiagorobert/grpc-example
RUN echo "replace github.com/thiagorobert/grpc-example/autogenerated_proto => ./src/go_rest_proxy/autogenerated/proto/" >> go.mod
RUN go mod tidy -compat=1.17

RUN go build src/go_rest_proxy/rest_reverse_proxy.go

# Expose requierd ports. This is not required, it's more of a documentation.
EXPOSE 8080
EXPOSE 8081

# Copy and run script that starts gRPC server and REST proxy.
COPY ./bootstrap.sh ${CODE_ROOT}/bootstrap.sh
CMD ["/go/src/thiago.pub/grpc-example/bootstrap.sh"]
