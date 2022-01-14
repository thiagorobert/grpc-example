# TLS data

This directory contains TLS data to support secure connections.

See https://www.sandtable.com/using-ssl-with-grpc-in-python/ for
additional details.

File in this directory where generated with command below.

```
> openssl req \
    -newkey rsa:2048 \
    -addext "subjectAltName = DNS:localhost" \
    -nodes \
    -x509 \
    -days 365 \
    -keyout server.key \
    -out server.crt

Generating a RSA private key
.........................+++++
..........+++++
writing new private key to 'server.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:
```
