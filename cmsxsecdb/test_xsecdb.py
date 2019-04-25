#!/usr/bin/env python

import json
from cmsxsecdb.request_wrapper import RequestWrapper


xsdb_req = RequestWrapper()

""" -- 1. SIMPLE QUERY - passing only search fields -- """

query = {'DAS': '.*DY.*'}
out = xsdb_req.simple_search(query)

data = json.loads(out)

for item in data:
    print item["DAS"], item["cross_section"]