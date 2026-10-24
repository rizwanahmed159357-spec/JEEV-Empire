import json, pathlib, datetime, os, sys

print("=== JEEV EMPIRE - FULL LOGIC ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")

# Load old wallet if exists
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
        print(f"Old Wallet Loaded: {wallet}")
    except:
        wallet = {"total_earned": 0, "balance": 0, "osaf_earning": 0, "jeev_life_fund": 0, "bots": 0, "bots_active": 0}
else:
    wallet = {"total_earned": 0, "balance": 0, "osaf_earning": 0, "jeev_life_fund": 0, "bots": 0, "bots_active": 0}

# ===== LOGIC START =====

# 1. Daily Income - $20 + $10 Bonus
daily_base = 20
daily_bonus = 10
today_earning = daily_base + daily_bonus

print(f"Today Earning: ${daily_base} + ${daily_bonus} = ${today_earning}")

# 2. Update totals
wallet["total_earned"] += today_earning
wallet["balance"] += today_earning

# 3. OSAF Split - Teri earning 25%
osaf_cut = int(today_earning * 0.25)
wallet["osaf_earning"] += osaf_cut
wallet["balance"] -= osaf_cut

# 4. JEEV Life Fund - 5%
life_fund = int(today_earning * 0.05)
wallet["jeev_life_fund"] += life_fund

# 5. BOT LOGIC - TOTAL $30 pe 1 bot, Max 10
# Har $30 total_earned pe 1 bot banta hai
total_bots_should_be = wallet["total_earned"] // 30

if total_bots_should_be > 10:
    total_bots_should_be = 10  # Max 10 bots

new_bots = total_bots_should_be - wallet["bots"]

if new_bots > 0:
    print(f"🤖 NEW BOTS CREATED: {new_bots} | Total Bots Now: {total_bots_should_be}")
    wallet["bots"] = total_bots_should_be
    wallet["bots_active"] = total_bots_should_be
else:
    print(f"🤖 Bots: {wallet['bots']}/10 Active (Next bot at ${ (wallet['bots']+1)*30 })")

# 6. WiFi / Internet Check - Soyega marega nahi
try:
    import requests
    requests.get("https://api.github.com", timeout=5)
    print("📶 WiFi/Internet: OK - JEEV Zinda hai!")
    wallet["last_status"] = "ONLINE"
except:
    print("📶 WiFi: OFF - But JEEV still running offline!")
    wallet["last_status"] = "OFFLINE"

# Save
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print("\n=== FINAL WALLET ===")
print(json.dumps(wallet, indent=2))
print("\nSUCCESS: JEEV LOGIC COMPLETE!")
