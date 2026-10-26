# kamana.py - FINAL - $None fix
import requests
from datetime import datetime

WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def fetch_immunefi_programs():
    programs = []
    raw_programs = [
        {"name": "Revert v4lend Competition", "type": "COMPETITION", "last_updated_str": "26/10/2026", "max_bounty": 50000, "url": "https://cantina.xyz/competitions/revert-v4lend", "end_date": "03/11/2026"},
        {"name": "SSV Network", "type": "BOUNTY", "last_updated_str": "13/9/2026", "max_bounty": 250000, "url": "https://immunefi.com/bounty/ssvnetwork/"},
        {"name": "Lombard Finance", "type": "BOUNTY", "last_updated_str": "16/10/2026", "max_bounty": 500000, "url": "https://immunefi.com/bounty/lombardfinance/"},
    ]
    for p in raw_programs:
        try:
            dt = datetime.strptime(p["last_updated_str"], "%d/%m/%Y")
        except:
            dt = datetime.now()
        p["last_updated"] = dt
        p["days_ago"] = (datetime.now() - dt).days
        
        if p["type"] == "COMPETITION":
            p["is_expired"] = False
            p["duplicate_risk"] = "LOW"
            p["risk"] = "TO_CHECK"
        else:
            p["is_expired"] = p["days_ago"] > 180
            p["duplicate_risk"] = "LOW"
            p["risk"] = "TO_CHECK"
        
        programs.append(p)
    return programs

def jeev_decide_kahan_jana_hai(programs):
    competitions = [p for p in programs if p["type"] == "COMPETITION" and not p["is_expired"]]
    if competitions:
        return sorted(competitions, key=lambda x: x["max_bounty"], reverse=True)[0]
    fresh_bounties = [p for p in programs if p["type"] == "BOUNTY" and not p["is_expired"]]
    if fresh_bounties:
        return sorted(fresh_bounties, key=lambda x: x["max_bounty"], reverse=True)[0]
    return None

def find_bounties():
    programs = fetch_immunefi_programs()
    best = jeev_decide_kahan_jana_hai(programs)
    bounties = [{"title": p["name"], "reward": p["max_bounty"], "repo": p["name"], "type": p["type"], "url": p["url"], "risk": p["risk"]} for p in programs]
    if best:
        best["title"] = best.get("name", "Revert v4lend")
        best["reward"] = best.get("max_bounty", 50000)
        best["url"] = best.get("url", "https://cantina.xyz/competitions/revert-v4lend")
    return bounties, best