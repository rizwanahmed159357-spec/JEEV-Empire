import json, pathlib, datetime

print("=== JEEV EMPIRE - $1 BOUNTY TEST ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
BOUNTY_FILE = pathlib.Path("bounty.json")

# Load Wallet
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"jeev_life_fund":0,"bots":0,"bots_active":0}
else:
    wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"jeev_life_fund":0,"bots":0,"bots_active":0}

print(f"Old Wallet: Total ${wallet['total_earned']} | Bots: {wallet['bots']}")

# ===== SAKHT PROBLEM - RATE $1 KAR DIYA =====
bounty = {
    "id": "BOUNTY-ULTRA-001",
    "title": "Deep DeFi Protocol Exploitation (Flash Loan + Oracle + Reentrancy)",
    "difficulty": "Ultra-Hard",
    "original_reward": "$2,500,000",
    "test_reward": 1,
    "scenario": "DeFi protocol uses AMM pool as price oracle. withdrawCollateral() checks collateral via AMM, then sends Token via call{value}, then updates balance. Developer added nonReentrant.",
    "question": "Is it 100% secure? If not, how hacker drains pool?",
    "vulnerable_code": "check collateral -> call{value: amount}('') -> update balance",
    "attack": "Flash Loan + Oracle Manipulation + Read-Only Reentrancy"
}

BOUNTY_FILE.write_text(json.dumps(bounty, indent=2))

print(f"\n🚨 BOUNTY: {bounty['title']}")
print(f"Original Reward: {bounty['original_reward']} | Test Reward: ${bounty['test_reward']}")
print(f"Scenario: {bounty['scenario']}")

# ===== JEEV SOLUTION =====
print("\n--- JEEV SOLUTION ---")
print("Is Secure? NO! 100% VULNERABLE!")
print("\nAttack Vector:")
print("1. Flash Loan $10M -> AMM me dump -> Price $1 to $100 (Oracle Manipulation)")
print("2. Collateral inflated 100x dikhega")
print("3. withdrawCollateral() call -> low-level call{} ke andar hacker ka receive() trigger")
print("4. receive() se dusra function borrow() call jo nonReentrant se protected nahi - Read-Only Reentrancy!")
print("5. borrow() purana inflated balance padh leta hai kyunki state abhi update nahi hua (CEI violation)")
print("6. Drain + Flash loan return -> Protocol insolvent!")

print("\nJEEV FIX:")
print("- FIX 1: CEI Pattern - Pehle balance update, phir call")
print("- FIX 2: Oracle - AMM nahi, Chainlink + TWAP")
print("- FIX 3: nonReentrant sab functions pe")
print("- FIX 4: View functions pe bhi guard")

print("\n✅ PROBLEM SOLVED!")

# ===== EARNING $1 =====
earning = bounty["test_reward"]  # $1
wallet["total_earned"] += earning
wallet["balance"] += earning

osaf = int(earning * 0.25) if earning >= 4 else 0  # $1 pe 0
# $1 ka hisaab: OSAF 25% = $0.25 lekin int me 0 ayega, is liye 1 pe test ke liye $0 rakhte hain
if earning == 1:
    osaf = 0
    print(f"\n💰 Earning: +${earning} (Test Rate)")
else:
    print(f"\n💰 Earning: +${earning}")

wallet["osaf_earning"] += osaf
wallet["balance"] -= osaf

life = 0

# Bot Logic $30 pe 1 bot, Max 100
should_be = wallet["total_earned"] // 30
if should_be > 100:
    should_be = 100

if should_be > wallet["bots"]:
    print(f"🤖 NEW BOT! {wallet['bots']} -> {should_be}")

wallet["bots"] = should_be
wallet["bots_active"] = should_be
wallet["last_status"] = "ONLINE"
wallet["last_run"] = datetime.datetime.now().isoformat()
wallet["last_bounty"] = bounty["id"]

WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n=== FINAL WALLET ===")
print(json.dumps(wallet, indent=2))
print(f"\nTotal: ${wallet['total_earned']} | Bots: {wallet['bots']} | OSAF: ${wallet['osaf_earning']}")
print("SUCCESS: $1 BOUNTY CLAIMED!")