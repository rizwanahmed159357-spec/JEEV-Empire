# kamana.py - JEEV ka DIL - Final with Real Wallet
import requests
from datetime import datetime

WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def fetch_immunefi_programs():
    programs = []
    raw_programs = [
        {"name": "SSV Network", "type": "BOUNTY", "last_updated_str": "13/9/2026", "max_bounty": 250000, "url": "https://immunefi.com/bounty/ssvnetwork/"},
        {"name": "Lombard Finance", "type": "BOUNTY", "last_updated_str": "16/10/2026", "max_bounty": 500000, "url": "https://immunefi.com/bounty/lombardfinance/"},
        {"name": "ENS", "type": "BOUNTY", "last_updated_str": "21/10/2026", "max_bounty": 250000, "url": "https://immunefi.com/bounty/ens/"},
        {"name": "The Graph", "type": "BOUNTY", "last_updated_str": "27/8/2026", "max_bounty": 50000, "url": "https://immunefi.com/bounty/thegraph/"},
        {"name": "Wormhole Competition", "type": "COMPETITION", "last_updated_str": "25/10/2026", "max_bounty": 100000, "url": "https://immunefi.com/competitions/wormhole"},
        {"name": "Chainlink CCIP Audit Comp", "type": "COMPETITION", "last_updated_str": "24/10/2026", "max_bounty": 75000, "url": "https://immunefi.com/competitions/chainlink"},
    ]
    for p in raw_programs:
        try:
            dt = datetime.strptime(p["last_updated_str"], "%d/%m/%Y")
        except:
            dt = datetime.now()
        p["last_updated"] = dt
        p["days_ago"] = (datetime.now() - dt).days
        p["is_expired"] = p["days_ago"] > 90 and p["type"] == "BOUNTY"
        if p["type"] == "COMPETITION":
            p["duplicate_risk"] = "LOW"
            p["risk"] = "LOW"
        elif p["days_ago"] <= 7:
            p["duplicate_risk"] = "LOW"
            p["risk"] = "LOW"
        else:
            p["duplicate_risk"] = "HIGH"
            p["risk"] = "HIGH"
        programs.append(p)
    return programs

def jeev_decide_kahan_jana_hai(programs):
    competitions = [p for p in programs if p["type"] == "COMPETITION" and not p["is_expired"]]
    if competitions:
        return sorted(competitions, key=lambda x: x["last_updated"], reverse=True)[0]
    fresh_bounties = [p for p in programs if p["type"] == "BOUNTY" and p["days_ago"] <= 7]
    if fresh_bounties:
        return sorted(fresh_bounties, key=lambda x: x["max_bounty"], reverse=True)[0]
    return None

def find_bounties():
    programs = fetch_immunefi_programs()
    best = jeev_decide_kahan_jana_hai(programs)
    bounties = [{"title": p["name"], "reward": p["max_bounty"], "repo": p["name"], "type": p["type"], "url": p["url"], "risk": p["risk"]} for p in programs]
    return bounties, best