import os, pathlib, json, datetime, time, sys

# Auto-install groq if not found (ye error khatam karega jo screenshot me aaya)
try:
    from groq import Groq
except ModuleNotFoundError:
    print("Groq not found, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - QWEN QWQ-32B DEEP REASONING + RATE LIMIT FIX ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
CONTRACT_FILE = pathlib.Path("contracts/PremiumStaking.sol")

if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"bots":0}
else:
    wallet = {"total_earned":0,"bots":0}

# ===== MODEL =====
MODEL_NAME = "qwen-qwq-32b"
print(f"Using Model: {MODEL_NAME} - Deep Reasoning")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found in Secrets! Add it in Settings > Secrets > Actions")
    sys.exit(1)

client = Groq(api_key=api_key)

# Contract file check
if not CONTRACT_FILE.exists():
    CONTRACT_FILE = pathlib.Path("PremiumStaking.sol")
if not CONTRACT_FILE.exists():
    print("ERROR: PremiumStaking.sol not found in contracts/ folder")
    sys.exit(1)

code = CONTRACT_FILE.read_text()
print(f"Analyzing: {CONTRACT_FILE.name} | Size: {len(code)} chars")
print("Qwen thinks deeply, will take 30-60 sec...")

# ===== REAL AI CALL WITH RATE LIMIT HANDLING =====
max_retries = 3
for attempt in range(max_retries):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.1,
            max_tokens=6000,
            messages=[
                {"role": "system", "content": "You are a senior smart contract auditor. You MUST always respond in ENGLISH ONLY. Provide vulnerability, attack vector, and fixed Solidity code."},
                {"role": "user", "content": f"""
Analyze this contract for Read-Only Reentrancy with ERC777:

{code}

Tasks:
1. Is it vulnerable? Explain totalStaked vs balanceOf desync during emergencyWithdraw hook.
2. Why nonReentrant fails for read-only?
3. Provide complete fixed Solidity code with _isWithdrawing lock and SafeERC20.

Answer in ENGLISH only.
"""}
            ]
        )
        ai_answer = response.choices[0].message.content
        break  # Success, break loop

    except Exception as e:
        err_str = str(e)
        if "RateLimit" in err_str or "429" in err_str or "rate_limit" in err_str.lower():
            wait_time = 70  # Groq free limit - 1 min wait
            print(f"⚠️ RateLimit Hit (Attempt {attempt+1}/{max_retries}) - Waiting {wait_time} sec...")
            time.sleep(wait_time)
            if attempt == max_retries - 1:
                print("Still RateLimited after retries. Saving placeholder and exiting.")
                ai_answer = "RateLimit Exceeded - Please wait 2 minutes and run again. Qwen Deep Thinking uses high tokens."
                break
            continue
        else:
            print(f"API Error: {e}")
            raise

print("\n--- JEEV QWEN-QWQ-32B ANSWER (ENGLISH) ---")
print(ai_answer)

# Save report
report_file = pathlib.Path("JEEV_AI_REPORT_QWEN.md")
report_file.write_text(f"# Model: {MODEL_NAME}\nDate: {datetime.datetime.now().isoformat()}\n\n{ai_answer}")

# ===== RATE LIMIT PROTECTION - Sleep before next run =====
# Yehi tujhe bola tha - 2 runs ke beech break
print("\n--- RATE LIMIT PROTECTION ---")
print("Sleeping 90 seconds to avoid Groq free limit block for next run...")
time.sleep(90)

# Earning
earning = 1
wallet["total_earned"] += earning
wallet["bots"] = min(wallet["total_earned"] // 30, 100)
wallet["last_model"] = MODEL_NAME
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n✅ DONE - Model: {MODEL_NAME} | Total: ${wallet['total_earned']} | Bots: {wallet['bots']}")
print("Report saved: JEEV_AI_REPORT_QWEN.md")