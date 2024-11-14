#!/bin/bash

#Generate root certificate
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.pem -subj "/C=CN/ST=Province/L=City/O=Varchive/OU=Varchive/CN=Varchive Root CA"
openssl req -new -sha256 -nodes -out server.csr -newkey rsa:2048 -keyout server.key -subj "/C=CN/ST=Province/L=City/O=Varchive/OU=Varchive/CN=Varchive Root CA"
openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256 -extfile v3.ext
if ! sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain rootCA.pem; then
    exit 1
fi
exit 0
