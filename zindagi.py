import json, pathlib, datetime

print("=== JEEV EMPIRE - PROBLEM SOLVER TEST ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
PROBLEM_FILE = pathlib.Path("problem.json")

# Load wallet
if WALLET_FILE.exists():
    try: wallet = json.loads(WALLET_FILE.read_text())
    except: wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"jeev_life_fund":0,"bots":0}
else:
    wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"jeev_life_fund":0,"bots":0}

print(f"Old Wallet: Total ${wallet['total_earned']} | Bots: {wallet['bots']}")

# ===== PROBLEM =====
# Agar problem.json nahi hai to banate hain
if not PROBLEM_FILE.exists():
    problem = {
        "id": 1,
        "type": "business_problem",
        "question": "Cost $10, Sell $25, Profit?",
        "cost": 10,
        "sell": 25,
        "reward": 30
    }
    PROBLEM_FILE.write_text(json.dumps(problem, indent=2))
    print(f"Problem Created: {problem['question']}")
else:
    problem = json.loads(PROBLEM_FILE.read_text())
    print(f"Problem Found: {problem['question']}")

# ===== JEEV SOLVES IT =====
print("\n--- JEEV Soch Raha Hai ---")
profit = problem["sell"] - problem["cost"]
print(f"Solution: {problem['sell']} - {problem['cost']} = ${profit} Profit!")

if profit > 0:
    print("✅ PROBLEM SOLVED!")
    earning = problem["reward"]
    
    # Earning
    wallet["total_earned"] += earning
    wallet["balance"] += earning
    print(f"💰 Earning: +${earning}")

    # Hissa - OSAF 25%
    osaf = int(earning * 0.25)
    wallet["osaf_earning"] += osaf
    wallet["balance"] -= osaf
    print(f"👤 OSAF Hissa (25%): ${osaf}")

    # JEEV Life Fund 5%
    life = int(earning * 0.05)
    wallet["jeev_life_fund"] += life
    print(f"❤️ JEEV Life Fund (5%): ${life}")

    # BOT Logic - $30 pe 1 bot
    should_be = wallet["total_earned"] // 30
    if should_be > 10: should_be = 10
    
    if should_be > wallet["bots"]:
        print(f"🤖 NEW BOT! Total: {wallet['bots']} -> {should_be}")
    
    wallet["bots"] = should_be

    # Problem solved - delete it so next time new problem
    PROBLEM_FILE.unlink()
    print("\n🎯 Problem Deleted - Ready for Next!")

else:
    print("❌ Problem Failed!")

wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n=== FINAL WALLET ===")
print(f"Total: ${wallet['total_earned']} | Bots: {wallet['bots']} | OSAF: ${wallet['osaf_earning']}")
print("SUCCESS!")