# Analysis base directory
export NANOCPPFW_BASE=$(readlink -e $(dirname "${BASH_SOURCE[0]}"))
export NANOCPPFW_DATABASE="${NANOCPPFW_BASE}/test.db"

# Path for data storage
export ANALYSIS_DATA_PATH="${NANOCPPFW_BASE}/data/"

# Python path
export PYTHONPATH=${PYTHONPATH}:"$NANOCPPFW_BASE":"$NANOCPPFW_BASE/nanocppfw"

# luigi
export LUIGI_CONFIG_FILE=${NANOCPPFW_BASE}/luigi.cfg

# law
export LAW_HOME="${NANOCPPFW_BASE}/.law"
mkdir -p ${LAW_HOME}
export LAW_CONFIG_FILE=${NANOCPPFW_BASE}/nanocppfw/law.cfg
