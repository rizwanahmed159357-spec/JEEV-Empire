import datetime
def fetch_immunefi_programs():
    raw=[{"name":"Wormhole","type":"COMPETITION","date":"25/10/2026","bounty":100000},{"name":"SSV","type":"BOUNTY","date":"13/9/2026","bounty":250000}]
    return raw
def jeev_decide_kahan_jana_hai(p):
    return p[0]
def find_bounties():
    prog=fetch_immunefi_programs()
    best=jeev_decide_kahan_jana_hai(prog)
    bount=[{"title":x["name"],"reward":x["bounty"]} for x in prog]
    return bount,best