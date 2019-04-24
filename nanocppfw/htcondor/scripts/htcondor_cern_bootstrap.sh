#!/usr/bin/env bash
action() {
    echo "Sourcing setup.sh"
    source "${NANOCPPFW_BASE}/setup.sh"

    echo "Initiating VOMS proxy."
    export X509_USER_PROXY=$(readlink -e ./x509up*)

    echo "Sourcing virtual environment"
    source "${VIRTUAL_ENV}/bin/activate"
}
action