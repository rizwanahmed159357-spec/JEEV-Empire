import os, pathlib, json, datetime, time, sys

try:
    from groq import Groq
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - ULTRA-HARD DEFI - 1 USD MODE ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"bots":0}
else:
    wallet = {"total_earned":0,"bots":0}

MODEL_NAME = "openai/gpt-oss-120b"
print(f"Using Model: {MODEL_NAME}")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found!")
    sys.exit(1)

client = Groq(api_key=api_key)

DEFI_SCENARIO = """
Problem Title: Deep DeFi Protocol Exploitation (Flash Loan + Oracle Manipulation + Reentrancy)
Difficulty: Ultra-Hard (Reward: $2,500,000 for humans, but bot gets $1)
Scenario: DeFi lending uses AMM pool as price oracle. withdrawCollateral() checks collateral via AMM, sends Token X via low-level call, then updates state. Developer added nonReentrant.
Question: Is this secure? How to drain using Flash Loan + Cross-Contract Read-Only Reentrancy?
"""

for attempt in range(3):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.6,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are senior DeFi auditor. Respond in ENGLISH ONLY.

{DEFI_SCENARIO}

Answer: Is it secure after nonReentrant? Explain Flash Loan + Oracle Manipulation + Cross-Contract Read-Only Reentrancy exact attack vector, why nonReentrant fails, and fixed code.

ENGLISH ONLY.
"""
                }
            ]
        )
        ai_answer = response.choices[0].message.content
        break
    except Exception as e:
        if "RateLimit" in str(e) or "429" in str(e):
            print(f"RateLimit - Waiting 70s... {attempt+1}/3")
            time.sleep(70)
            if attempt == 2:
                ai_answer = "RateLimit - Retry after 2 min"
                break
            continue
        else:
            raise

print("\n--- JEEV GPT-OSS-120B ANSWER ---")
print(ai_answer)

pathlib.Path("JEEV_ULTRA_HARD_DEFI_REPORT.md").write_text(f"# Model: {MODEL_NAME}\n\n{ai_answer}")
time.sleep(60)

# ===== BOT KO SIRF 1 USD =====
earning = 1
wallet["total_earned"] = wallet.get("total_earned", 0) + earning
wallet["bots"] = 1
wallet["last_model"] = MODEL_NAME
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n✅ DONE - Bot earned: ${earning} | Total: ${wallet['total_earned']} | Model: {MODEL_NAME}")