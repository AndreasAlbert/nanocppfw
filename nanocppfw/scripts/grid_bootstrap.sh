load_replica() {
    local remote_base="$1"
    local bundle_re="$2"
    local arc_path="$3"

    local arc="$( gfal-ls "$remote_base" | grep -Po "$bundle_re" | shuf -n 1 )"
    if [ -z "$arc" ]; then
        >&2 echo "could not determine archive to load from $remote_base"
        return "1"
    fi

    gfal-copy "$remote_base/$arc" "$arc_path"
    if [ "$?" != "0" ]; then
        >&2 echo "could not load archive $arc from $remote_base"
        return "1"
    fi
}


export CMSSW_VERSION="CMSSW_10_2_13"
export ENVNAME=myenv

# Set up CMSSW
source /cvmfs/cms.cern.ch/cmsset_default.sh
scramv1 project CMSSW $CMSSW_VERSION
pushd $CMSSW_VERSION/src;
eval `scramv1 runtime -sh`
popd


# Virtual environment
python -m virtualenv "${ENVNAME}"
export ENVDIR=$(readlink -e "./${ENVNAME}/")
source ${ENVDIR}/bin/activate

# Install law
python -m pip install law

# Get software
mkdir -p software
pushd software
load_replica "srm://grid-srm.physik.rwth-aachen.de:8443/srm/managerv2?SFN=/pnfs/physik.rwth-aachen.de/cms/store/user/aalbert/testlaw/" "nanocppfw.*.tgz" "nanocppfw.tgz"

tar xf nanocppfw.tgz  || return "$?"
rm nanocppfw.tgz

pushd nanocppfw
make
source nanocppfw/setup.sh || return "$?"
popd

export LUIGI_CONFIG_PATH="$NANOCPPFW_BASE/nanocppfw/law.cfg)"

# Set up gfal
wget https://www.dropbox.com/s/3nylghi0xtqaiyy/gfal2.tgz
tar -xzf gfal2.tgz
rm gfal2.tgz

source "gfal2/setup.sh" || return "$?"
popd
ls -la software
ls -la .


echo $PYTHONPATH
