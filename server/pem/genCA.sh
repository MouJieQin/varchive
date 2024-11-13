#!/bin/bash

#Generate root certificate
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.pem -subj "/C=CA/ST=Province/L=City/O=Varchive/CN=Varchive Root CA"
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=CA/ST=Province/L=City/O=Varchive/CN=Varchive Root CA"
openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 3650 -sha256 -extfile v3.ext
openssl x509 -in rootCA.pem -out rootCA.crt -outform DER
if ! sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain rootCA.crt; then
    exit 1
fi
exit 0
