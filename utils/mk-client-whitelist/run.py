#!/usr/bin/env python3

# Make a list of the current top 1,000 certs to whitelist from the
# Decentralized SSL Observatory's client submissions, to live in
# https-everywhere/src/chrome/content/code/X509ChainWhitelist.js

import dbconnect
import sys

db, dbc = dbconnect.dbconnect()

import time
few_days_ago = time.gmtime(time.time() - 3600 * 24 * 3)
cutoff = time.strftime("%Y-%m-%d", few_days_ago)

# This currently runs on the decentralized observatory server, but will also
# run on the published datasets and read-only SQL servers too...

q = """
SELECT hex(reports.chain_fp), count, `Validity:Not After`, Subject
FROM reports JOIN chains       ON reports.chain_fp = chains.chain_fp
             JOIN new_parsed_certs ON reports.cert_fp  = new_parsed_certs.cert_fp
WHERE count > 1000 AND
      `Validity:Not After` > "{}"
GROUP BY reports.chain_fp
ORDER BY count DESC
LIMIT 1000
""".format(cutoff)

dbc.execute(q)
results = dbc.fetchmany(1000)

sys.stderr.write("TOP 1000:\n")
for n in range(1000):
    sys.stderr.write(repr(results[n][1:4]) + results[n][0][:4]+ '\n')

header = """
// These are SHA256 fingerprints for the most common chains observed by the
// Decentralized SSL Observatory.  These should not be resubmitted.
// This file is automatically generated by utils/mk_client_whitelist.py

const X509ChainWhitelist = {"""

print(header)
for chain_fp in sorted([row[0] for row in results]):
  print("  '{}' : true,".format(chain_fp))

footer = "} ;"
print(footer)


