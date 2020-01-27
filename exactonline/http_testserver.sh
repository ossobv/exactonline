#!/bin/bash
openssl genrsa -out http_testserver.key 4096 &&
openssl req -new -key http_testserver.key -out http_testserver.csr -batch \
  -subj '/C=NL/L=Groningen/O=Example Inc./CN=localhost/emailAddress=example@localhost' \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:::1" &&
openssl x509 -in http_testserver.csr -out http_testserver.crt -req \
  -signkey http_testserver.key -days 3650 -extfile <(
    printf 'subjectAltName=%s' \
      $(openssl req -in http_testserver.csr -noout -text |
        sed -e '/DNS:/!d;s/^[[:blank:]]*//;s/, /,/g;s/IP Address:/IP:/g') ) &&
printf '\nOK\n'
