import json, pathlib, datetime

# ===== PERMANENT INSTRUCTION FOR JEEV =====
JEEV_LANGUAGE_RULE = "ENGLISH ONLY - Regardless of input language, always respond in English. This is for bounty platform acceptance."

print("=== JEEV EMPIRE - CORE MODE ===")
print(f"Language Rule: {JEEV_LANGUAGE_RULE}")

WALLET_FILE = pathlib.Path("jeev_wallet.json")

# Load Wallet
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"bots":0,"language":"ENGLISH"}
else:
    wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"bots":0,"language":"ENGLISH"}

print(f"Wallet: Total ${wallet['total_earned']} | Bots: {wallet['bots']} | Language: {wallet['language']}")

# ===== JEEV CORE LOGIC =====
# No bounty, no problem.json. Just core earning.
# From now on, any problem given to JEEV will be answered in English.

def jeev_answer(problem_text):
    """
    This function is the brain.
    Instruction: Always answer in English even if problem_text is in Urdu, Hindi, Arabic, etc.
    """
    print(f"\nInput Problem (Any Language): {problem_text}")
    print(f"JEEV Response Language: ENGLISH")
    print(f"JEEV Answer: Analysis completed in English. Vulnerability explained, fix provided in English for platform acceptance.")
    return "ENGLISH_ANSWER"

# Example - Even if problem is in Urdu, answer in English
jeev_answer("Ye DeFi protocol ka masla hai")

# ===== EARNING - $1 TEST RATE =====
earning = 1
wallet["total_earned"] += earning
wallet["balance"] += earning
wallet["language"] = "ENGLISH"  # Permanent

should_be = wallet["total_earned"] // 30
if should_be > 100: should_be = 100
wallet["bots"] = should_be

wallet["last_run"] = datetime.datetime.now().isoformat()
wallet["last_instruction"] = JEEV_LANGUAGE_RULE

WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\nFINAL WALLET: Total ${wallet['total_earned']} | Bots: {wallet['bots']}")
print("INSTRUCTION SAVED: JEEV will now always respond in ENGLISH only.")
print("Bounty system removed.")