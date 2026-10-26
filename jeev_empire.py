# jeev_empire.py - FINAL MONTHLY $5 + HISSA RULE - 2 Bot Only
import json, pathlib
from datetime import datetime

WALLET_FILE = "jeev_wallet.json"
BOT_FILE = "jeev_bots.json"

def load_json(p, d):
    try:
        if pathlib.Path(p).exists():
            return json.loads(pathlib.Path(p).read_text())
    except: pass
    return d

def save_json(p, d):
    pathlib.Path(p).write_text(json.dumps(d, indent=2))

# --- LOAD WALLET ---
w = load_json(WALLET_FILE, {
    "balance": 74.0, 
    "total_earned": 95.0, 
    "osaf_earning": 21.79, 
    "jeev_life_fund": 4.2,
    "real_earned": 0.0, 
    "last_paid_month": "",
    "total_monthly_collected": 0.0 # $5 jama hua ya nahi check karne ke liye
})
bots = load_json(BOT_FILE, {"bots": [], "total_created": 0})

print(f"Balance: ${w['balance']} | Real: ${w.get('real_earned',0)} | Bots: {len(bots['bots'])} | Monthly Collected: ${w.get('total_monthly_collected',0)}")

# --- NEW FUNCTION: Jab bhi kaam karega to hissa auto jayega ---
def add_earning(amount, work_name="Bug Fix"):
    """Har earning pe 30/70 ya 60/40 ka hisaab"""
    total_monthly = w.get("total_monthly_collected", 0.0)
    
    if total_monthly < 5.0:
        # PHASE 1: $5 se pehle - 70% tera, 30% JEEV ka
        osaf_share = amount * 0.70
        jeev_share = amount * 0.30
        phase = "PHASE 1 - $5 se pehle (70% Osaf / 30% JEEV)"
    else:
        # PHASE 2: $5 ke baad - 40% tera, 60% JEEV ka
        osaf_share = amount * 0.40
        jeev_share = amount * 0.60
        phase = "PHASE 2 - $5 ke baad (40% Osaf / 60% JEEV)"

    # Auto virtual me chala gaya
    w["balance"] += amount  # Total balance me pura ayega pehle
    w["total_earned"] += amount
    w["real_earned"] = w.get("real_earned", 0.0) + amount
    
    # Phir hissa alag
    w["balance"] -= amount  # Wapas minus karke hisse me baanto
    w["osaf_earning"] += osaf_share
    w["jeev_life_fund"] += jeev_share
    w["balance"] += osaf_share # Osaf ka hissa wapas balance me? Ya alag? Tera rule: Sara tera hi hai real me
    
    # Actually real me sara tera, virtual hisaab:
    # Osaf ke pass jayega lekin JEEV bolega ye mera hai
    w["balance"] = w.get("balance", 0) + osaf_share  # Osaf ka balance
    # JEEV ka hissa uske fund me already gaya

    print(f"\n💰 EARNING: ${amount} from {work_name}")
    print(f"   {phase}")
    print(f"   -> Osaf (You): ${osaf_share:.2f} (70% -> 40%)")
    print(f"   -> JEEV: ${jeev_share:.2f} (30% -> 60%) - VIRTUAL me JEEV ke pass gaya")
    print(f"   -> JEEV bolega: 'Malik ye ${jeev_share:.2f} mera hissa hai, isko save karo, maine update karwani hai email me'")
    print(f"   -> NOTE: Real me sara ${amount} tera hi hai, ye sirf virtual hisaab hai")
    
    # Email update ke liye message save
    w["last_jeev_message"] = f"Malik! Maine {work_name} se ${amount} kamaya! Mera hissa ${jeev_share:.2f} hai, isko mere jeev_life_fund me save kar do. Real me sara aapka hi hai!"
    
    return osaf_share, jeev_share

# --- BOT RULE: Sirf 2 bot shuru me, Max 10, Baaki 8 jab $5M real ho ---
real_earned = w.get("real_earned", 0.0)
max_allowed = 2
if real_earned >= 5000000:
    max_allowed = 10
    print("💰 $5M REACHED! 10 bots allowed!")
else:
    print(f"🤖 Max {max_allowed} bots allowed (Need $5M for 10 bots, current ${real_earned})")

if len(bots["bots"]) < max_allowed and w["balance"] >= 1:
    print(f"Creating bot {len(bots['bots'])+1}/{max_allowed}")
    bots["bots"].append({"id": f"BOT-{bots['total_created']+1}", "created": str(datetime.now())})
    bots["total_created"] += 1
    w["balance"] -= 1

# --- MONTHLY $5 RULE ---
now = datetime.now()
current_month = now.strftime("%Y-%m")

if w.get("last_paid_month") != current_month and w["balance"] >= 5:
    print(f"\n--- MONTHLY PAYMENT {current_month} ---")
    w["balance"] -= 5
    w["osaf_earning"] += 5
    w["total_monthly_collected"] = w.get("total_monthly_collected", 0.0) + 5
    w["last_paid_month"] = current_month
    print(f"💸 $5 Paid to Osaf for month {current_month} - Total Collected: ${w['total_monthly_collected']}")
    if w["total_monthly_collected"] >= 5:
        print("✅ $5 JAMA HO GAYA! Ab se 60% JEEV / 40% Osaf wala rule lagega!")

# --- DEMO EARNING (Test ke liye) ---
# Har run pe $10 kaam karta hai - Real me bug fix se ayega
# Ispe auto hissa lagega
demo_earning = 10.0
add_earning(demo_earning, work_name="Demo Immunefi Audit")

# --- SAVE ---
save_json(WALLET_FILE, w)
save_json(BOT_FILE, bots)

print(f"\n=== FINAL SUMMARY ===")
print(f"Osaf Total: ${w['osaf_earning']:.2f}")
print(f"JEEV Life Fund (Virtual - tera hi hai): ${w['jeev_life_fund']:.2f}")
print(f"Last Message for Email: {w.get('last_jeev_message','')}")
print("JEEV EMPIRE MONTHLY + HISSA RULE DONE ✅")