#!/usr/bin/env bash
action() {
    source "${NANOCPPFW_BASE}/setup.sh"
    export X509_USER_PROXY=$(readlink -e ./x509up*)
}
action