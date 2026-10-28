# jeev_empire.py - FINAL - ALL RULES + 10000 tokens + Gmail ready
import json, pathlib
from datetime import datetime

WALLET_FILE = "jeev_wallet.json"
BOT_FILE = "jeev_bots.json"
SOURCES_FILE = "bounty_sources.json"

def load_json(p, d):
    try:
        for path in [p, f"JEEV-Empire/{p}", f"../{p}"]:
            if pathlib.Path(path).exists():
                return json.loads(pathlib.Path(path).read_text())
    except: pass
    return d

def save_json(p, d):
    pathlib.Path(p).write_text(json.dumps(d, indent=2))
    try:
        pathlib.Path(f"JEEV-Empire/{p}").write_text(json.dumps(d, indent=2))
    except: pass

# LOAD WALLET - ALL RULES
w = load_json(WALLET_FILE, {
    "balance": 74.0, 
    "total_earned": 95.0, 
    "osaf_earning": 21.79, 
    "jeev_life_fund": 4.2,
    "real_earned": 0.0, 
    "last_paid_month": "",
    "total_monthly_collected": 0.0
})
bots = load_json(BOT_FILE, {"bots": [], "total_created": 0})

print(f"Balance: ${w['balance']} | Real: ${w.get('real_earned',0)} | Bots: {len(bots['bots'])} | Monthly: ${w.get('total_monthly_collected',0)}")

def add_earning(amount, work_name="Bug Fix"):
    total_monthly = w.get("total_monthly_collected", 0.0)
    if total_monthly < 5.0:
        osaf_share = amount * 0.70
        jeev_share = amount * 0.30
        phase = "PHASE 1 - $5 se pehle (70% Osaf / 30% JEEV)"
    else:
        osaf_share = amount * 0.40
        jeev_share = amount * 0.60
        phase = "PHASE 2 - $5 ke baad (40% Osaf / 60% JEEV)"
    
    w["total_earned"] = w.get("total_earned",0) + amount
    w["real_earned"] = w.get("real_earned", 0.0) + amount
    w["osaf_earning"] = w.get("osaf_earning",0) + osaf_share
    w["jeev_life_fund"] = w.get("jeev_life_fund",0) + jeev_share
    w["balance"] = w.get("balance",0) + osaf_share
    
    print(f"\n💰 EARNING: ${amount} from {work_name}")
    print(f"   {phase} -> Osaf ${osaf_share:.2f} / JEEV ${jeev_share:.2f}")
    w["last_jeev_message"] = f"Malik! {work_name} se ${amount} - Mera hissa ${jeev_share:.2f}"
    return osaf_share, jeev_share

# BOT RULE - Max 2, after $5M 10
real_earned = w.get("real_earned", 0.0)
max_allowed = 10 if real_earned >= 5000000 else 2
print(f"🤖 Max {max_allowed} bots allowed (Need $5M for 10, current ${real_earned})")
if len(bots["bots"]) < max_allowed and w["balance"] >= 1:
    bots["bots"].append({"id": f"BOT-{bots['total_created']+1}", "created": str(datetime.now())})
    bots["total_created"] += 1
    w["balance"] -= 1
    print(f"Created bot {bots['total_created']}")

# MONTHLY $5 RULE
now = datetime.now()
current_month = now.strftime("%Y-%m")
if w.get("last_paid_month") != current_month and w["balance"] >= 5:
    w["balance"] -= 5
    w["osaf_earning"] += 5
    w["total_monthly_collected"] = w.get("total_monthly_collected", 0.0) + 5
    w["last_paid_month"] = current_month
    print(f"💸 $5 Paid for {current_month} - Total {w['total_monthly_collected']}")
    if w["total_monthly_collected"] >= 5:
        print("✅ $5 JAMA - Ab 60% JEEV / 40% Osaf")

# DEMO
add_earning(10.0, work_name="Universal Audit")

save_json(WALLET_FILE, w)
save_json(BOT_FILE, bots)
print(f"Osaf: ${w['osaf_earning']:.2f} | JEEV Fund: ${w['jeev_life_fund']:.2f}")