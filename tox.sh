#!/bin/bash

# homebrew is installed and so is a brewed openssl
if [[ $(uname) == "Darwin" ]] && command -v brew &>/dev/null && brew list openssl &>/dev/null; then
    env ARCHFLAGS="-arch x86_64" LDFLAGS="-L/usr/local/opt/openssl/lib" CFLAGS="-I/usr/local/opt/openssl/include" tox $*

else
    tox $*

fi