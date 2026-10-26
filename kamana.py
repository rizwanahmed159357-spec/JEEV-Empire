# kamana.py - JEEV ka DIL - 7 days rule KHATAM - Revert $50k added
import requests
from datetime import datetime

WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def fetch_immunefi_programs():
    programs = []
    raw_programs = [
        # NAYA - Revert v4lend $50k - 3 Nov tak - No deposit - FREE
        {"name": "Revert v4lend Competition", "type": "COMPETITION", "last_updated_str": "06/10/2026", "max_bounty": 50000, "url": "https://cantina.xyz/competitions/revert-v4lend", "end_date": "03/11/2026"},
        # Purane - 7 days rule khatam - Yearn May 2026 bhi chalega
        {"name": "SSV Network", "type": "BOUNTY", "last_updated_str": "13/9/2026", "max_bounty": 250000, "url": "https://immunefi.com/bounty/ssvnetwork/"},
        {"name": "Lombard Finance", "type": "BOUNTY", "last_updated_str": "16/10/2026", "max_bounty": 500000, "url": "https://immunefi.com/bounty/lombardfinance/"},
        {"name": "ENS", "type": "BOUNTY", "last_updated_str": "21/10/2026", "max_bounty": 250000, "url": "https://immunefi.com/bounty/ens/"},
        {"name": "Yearn V3", "type": "BOUNTY", "last_updated_str": "15/05/2026", "max_bounty": 200000, "url": "https://app.sherlock.xyz/audits/contests/yearn-v3"},
    ]
    for p in raw_programs:
        try:
            dt = datetime.strptime(p["last_updated_str"], "%d/%m/%Y")
        except:
            dt = datetime.now()
        p["last_updated"] = dt
        p["days_ago"] = (datetime.now() - dt).days
        
        # 7 DAYS RULE KHATAM - Sab chalega!
        if p["type"] == "COMPETITION":
            p["is_expired"] = False  # Competition kabhi expire nahi - 3 Nov tak chalega!
            p["duplicate_risk"] = "LOW"
            p["risk"] = "LOW"
        else:
            # Bounty ke liye bhi 7 din wala rule khatam - 180 din tak valid
            p["is_expired"] = p["days_ago"] > 180
            p["duplicate_risk"] = "LOW"  # LOW kar diya - Pehle HIGH tha
            p["risk"] = "LOW"
        
        programs.append(p)
    return programs

def jeev_decide_kahan_jana_hai(programs):
    # Pehle Competition - Revert v4lend $50k
    competitions = [p for p in programs if p["type"] == "COMPETITION" and not p["is_expired"]]
    if competitions:
        return sorted(competitions, key=lambda x: x["max_bounty"], reverse=True)[0]
    # Phir Bounty - 7 din wala filter khatam - Sabse bada bounty
    fresh_bounties = [p for p in programs if p["type"] == "BOUNTY" and not p["is_expired"]]
    if fresh_bounties:
        return sorted(fresh_bounties, key=lambda x: x["max_bounty"], reverse=True)[0]
    return None

def find_bounties():
    programs = fetch_immunefi_programs()
    best = jeev_decide_kahan_jana_hai(programs)
    bounties = [{"title": p["name"], "reward": p["max_bounty"], "repo": p["name"], "type": p["type"], "url": p["url"], "risk": p["risk"]} for p in programs]
    return bounties, best