export NANOCPPFW_BASE=$(readlink -e $(dirname "${BASH_SOURCE[0]}"))
export ANALYSIS_DATA_PATH="${NANOCPPFW_BASE}/data/"
export PYTHONPATH=${PYTHONPATH}:"$NANOCPPFW_BASE":"$NANOCPPFW_BASE/nanocppfw"
export LAW_CONFIG_FILE=${NANOCPPFW_BASE}/nanocppfw/law.cfg
