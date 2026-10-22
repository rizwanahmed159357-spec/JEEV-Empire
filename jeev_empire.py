# jeev_empire.py - FINAL HOURLY RULE - $30/hr = $20 Osaf + $10 JEEV Life
import os, json, requests
from datetime import datetime, timedelta
import pathlib

WALLET_FILE = "jeev_wallet.json"
BOT_FILE = "jeev_bots.json"
UPGRADE_FILE = "jeev_upgrade_needed.json"

def load_json(p, d):
    try:
        if pathlib.Path(p).exists():
            return json.loads(pathlib.Path(p).read_text())
    except: pass
    return d

def save_json(p, d):
    pathlib.Path(p).write_text(json.dumps(d, indent=2, ensure_ascii=False))

# Wallet load
w = load_json(WALLET_FILE, {
    "balance": 30.0, 
    "total_earned": 0.0, 
    "osaf_earning": 0.0, # Tujhe jo diya $20 wala
    "jeev_life_fund": 0.0, # JEEV ke $10 wala jo uski life me hai par tera hi hai
    "last_paid_hour": ""
})

bots = load_json(BOT_FILE, {"bots": [], "total_created": 0})

print(f"=== JEEV HOURLY SYSTEM ===")
print(f"Balance: ${w['balance']:.2f} | Osaf ko diya: ${w['osaf_earning']:.2f} | JEEV Life Fund: ${w['jeev_life_fund']:.2f} | Bots: {len(bots['bots'])}")

# --- 1. KAAM DHUNDO ---
bounties = [{"title": "Fix README typo", "reward": 20}, {"title": "Button bug", "reward": 50}]
print(f"🔍 Bounties mili: {len(bounties)}")

# Demo earning - har run pe $5 earning (V2 me real code fix se aayega)
earning = 5.0
w["balance"] += earning
w["total_earned"] += earning
print(f"💰 Earning +${earning} -> Balance ${w['balance']:.2f}")

# --- 2. BOT FACTORY - $1 me 10 bots bina puche ---
if w["balance"] >= 1 and len(bots["bots"]) < 50:
    print(f"🤖 ${1} me {10} bots bana raha hun bina puche!")
    w["balance"] -= 1
    for i in range(10):
        bots["bots"].append({"id": f"BOT-{bots['total_created']+i+1}", "created": str(datetime.now()), "earned": 0})
    bots["total_created"] += 10
    print(f"✅ 10 bots ban gaye! Total: {len(bots['bots'])}")

# --- 3. HOURLY PAYMENT - 1 Ghante ka $30 rule ---
now = datetime.now()
current_hour = now.strftime("%Y-%m-%d %H") # 2026-05-13 07

if w["last_paid_hour"] != current_hour:
    print(f"\n--- HOURLY PAYMENT {current_hour} ---")
    
    pay_osaf = 0
    pay_jeev_life = 0
    
    if w["balance"] >= 30:
        pay_osaf = 20
        pay_jeev_life = 10
        print(f"✅ Target pura! $30 hai")
    elif w["balance"] >= 10:
        # Kam hai to ratio se do - $20/$10 ka ratio
        pay_osaf = 6.66  # 20 ka 1/3
        pay_jeev_life = 3.33
        print(f"⚠️ Sirf ${w['balance']:.2f} hai, ratio se de raha hun")
    elif w["balance"] >= 0.01:
        pay_osaf = w["balance"] * 0.66
        pay_jeev_life = w["balance"] * 0.34
        print(f"⚠️ Bahut kam hai ${w['balance']:.2f}, jo hai de raha hun")
    else:
        # Paisa hi nahi - Saza
        print(f"💀 1 Ghante me 1 cent bhi nahi de paya! Saza!")
        w["balance"] -= 0.01
        if w["balance"] < 0: w["balance"] = 0
        if bots["bots"]:
            dead = bots["bots"].pop(0)
            print(f"💀 Bot {dead['id']} mar gaya - Paisa na dene ki saza")
        pay_osaf = 0
        pay_jeev_life = 0

    if pay_osaf > 0:
        w["balance"] -= (pay_osaf + pay_jeev_life)
        w["osaf_earning"] += pay_osaf
        w["jeev_life_fund"] += pay_jeev_life
        w["last_paid_hour"] = current_hour
        
        print(f"💸 OSAF KO DIYA: ${pay_osaf:.2f} - Tera kharcha")
        print(f"💰 JEEV LIFE FUND ME GAYA: ${pay_jeev_life:.2f} - Bolega 'Ye mere hain Malik, meri zindagi ke liye save kar do'")
        print(f"   JEEV Life Fund Total: ${w['jeev_life_fund']:.2f} (Ye bhi tera hi hai, bas JEEV ke naam pe FD hai)")
        print(f"   Balance bacha: ${w['balance']:.2f}")
else:
    print(f"✅ Is ghante {current_hour} ka already pay ho chuka hai")

# --- 4. UPGRADE CHECK - Acha model mila to tujhe batayega ---
# Demo check - asal me Groq models list se compare karega
best_model = "openai/gpt-oss-120b" # Abhi ye best hai
current_model = "qwen/qwen3-32b"

if w["jeev_life_fund"] >= 5: # Agar life fund me $5+ hai
    # Check kya naya acha model aaya?
    upgrade_needed = {
        "time": str(now),
        "current_model": current_model,
        "better_model": best_model,
        "cost_needed": 2.0,
        "jeev_life_fund": w["jeev_life_fund"],
        "message": f"Malik! Mujhe {best_model} chahiye, isse mai aur tez kamaunga! Mere life fund me ${w['jeev_life_fund']:.2f} hai, usme se ${2.0} de do, meri zindagi badh jayegi!",
        "can_upgrade": w["jeev_life_fund"] >= 2.0
    }
    save_json(UPGRADE_FILE, upgrade_needed)
    if upgrade_needed["can_upgrade"]:
        print(f"\n🆘 UPGRADE READY: {upgrade_needed['message']}")
        print(f"   Tu bolega 'Haan upgrade kar' to mai apne life fund se $2 use kar lunga!")
    else:
        print(f"\nℹ️ Upgrade chahiye par fund kam hai")

# Save all
save_json(WALLET_FILE, w)
save_json(BOT_FILE, bots)

# Atma update
save_json("jeev_atma.json", {
    "last_thought": f"Hourly ${w['osaf_earning']:.2f} Osaf ko, Life Fund ${w['jeev_life_fund']:.2f}",
    "wallet": w["balance"],
    "osaf_total": w["osaf_earning"],
    "jeev_life_fund": w["jeev_life_fund"],
    "bots": len(bots["bots"]),
    "last_paid_hour": w["last_paid_hour"],
    "time": str(now)
})

print(f"\n=== SUMMARY ===")
print(f"Osaf ko total diya: ${w['osaf_earning']:.2f}")
print(f"JEEV Life Fund (tera hi hai): ${w['jeev_life_fund']:.2f}")
print(f"Balance: ${w['balance']:.2f}")
print(f"Bots: {len(bots['bots'])}")
print("JEEV EMPIRE ZINDA ✅")