load_replica() {
    local remote_base="$1"
    local bundle_re="$2"
    local arc_path="$3"

    local arc="$( python $(which gfal-ls) "$remote_base" | grep -Po "$bundle_re" | shuf -n 1 )"
    if [ -z "$arc" ]; then
        >&2 echo "could not determine archive to load from $remote_base"
        return "1"
    fi

    python $(which gfal-copy) "$remote_base/$arc" "$arc_path"
    if [ "$?" != "0" ]; then
        >&2 echo "could not load archive $arc from $remote_base"
        return "1"
    fi
}


# export CMSSW_VERSION="CMSSW_10_5_0"
export ENVNAME=myenv

# ### Set up CMSSW
# source /cvmfs/cms.cern.ch/cmsset_default.sh
# scramv1 project CMSSW $CMSSW_VERSION
# pushd $CMSSW_VERSION/src;
# eval `scramv1 runtime -sh`
# popd


# source /cvmfs/sft.cern.ch/lcg/views/ROOT-latest/x86_64-slc6-gcc7-opt/setup.sh
# source /cvmfs/grid.cern.ch/centos7-wn-4.0.5-1_umd4v1/etc/profile.d/setup-c7-wn-example.sh

#### Virtual environment
python -m pip install --user virtualenv
python -m virtualenv "${ENVNAME}" -p $(which python)
export ENVDIR=$(readlink -e "./${ENVNAME}/")
source ${ENVDIR}/bin/activate

# Install law
python -m pip install law

### Get software
mkdir -p software
pushd software


# # Set up gfal
# wget https://www.dropbox.com/s/3nylghi0xtqaiyy/gfal2.tgz
# tar -xzf gfal2.tgz
# rm gfal2.tgz

# source "gfal2/setup.sh" || return "$?"

# The framework
load_replica "${GRIDPACK_PATH}" $(echo ${GRIDPACK_NAME} | sed "s|\.tgz|.*.tgz|") "nanocppfw.tgz"

tar xf nanocppfw.tgz  || return "$?"
rm nanocppfw.tgz

pushd nanocppfw
make
source nanocppfw/setup.sh || return "$?"
popd

export LUIGI_CONFIG_PATH="$NANOCPPFW_BASE/nanocppfw/law.cfg)"

popd
ls -la software
ls -la .


echo $PYTHONPATH

### Done