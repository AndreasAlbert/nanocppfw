export NANOCPPFW_BASE=$(readlink -e $(dirname "${BASH_SOURCE[0]}"))
export PYTHONPATH=${PYTHONPATH}:"$NANOCPPFW_BASE"
export LAW_CONFIG_FILE=${NANOCPPFW_BASE}/nanocppfw/law.cfg