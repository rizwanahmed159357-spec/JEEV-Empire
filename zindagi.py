import os, pathlib, json, datetime, time, sys

try:
    from groq import Groq
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - GPT-OSS-120B MODE ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
CONTRACT_FILE = pathlib.Path("contracts/PremiumStaking.sol")

if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"bots":0}
else:
    wallet = {"total_earned":0,"bots":0}

# ===== MODEL - Tera wala naya =====
MODEL_NAME = "openai/gpt-oss-120b"
print(f"Using Model: {MODEL_NAME}")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found!")
    sys.exit(1)

client = Groq(api_key=api_key)

if not CONTRACT_FILE.exists():
    CONTRACT_FILE = pathlib.Path("PremiumStaking.sol")

if not CONTRACT_FILE.exists():
    print("ERROR: PremiumStaking.sol not found")
    sys.exit(1)

code = CONTRACT_FILE.read_text()
print(f"Analyzing: {CONTRACT_FILE.name}")

# ===== SETTINGS - Jo tune bola =====
# 1. No system role - Sab user role me
# 2. Temperature 0.6 - Taake reasoning stuck na ho

max_retries = 3
for attempt in range(max_retries):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.6,
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a senior smart contract security auditor specializing in Read-Only Reentrancy. You MUST always respond in ENGLISH ONLY.

Analyze this Solidity contract:

{code}

Tasks:
1. Is PremiumStaking vulnerable to Read-Only Reentrancy with ERC777 tokens even with nonReentrant and CEI checks? Explain exact attack vector with totalStaked vs stakingToken.balanceOf() desync during emergencyWithdraw() hook.
2. Why does nonReentrant modifier fail to protect against read-only reentrancy?
3. Provide complete FIXED Solidity contract code with _isWithdrawing lock, SafeERC20, balanceBefore/After check, and view functions protection.

Respond in ENGLISH only. Provide detailed explanation and fixed code.
"""
                }
            ]
        )
        ai_answer = response.choices[0].message.content
        break

    except Exception as e:
        err_str = str(e)
        if "RateLimit" in err_str or "429" in err_str:
            wait = 70
            print(f"RateLimit Hit - Waiting {wait}s... Attempt {attempt+1}/{max_retries}")
            time.sleep(wait)
            if attempt == max_retries - 1:
                ai_answer = "RateLimit - Wait 2 min and retry"
                break
            continue
        else:
            print(f"API Error: {e}")
            raise

print("\n--- JEEV GPT-OSS-120B ANSWER (ENGLISH) ---")
print(ai_answer)

pathlib.Path("JEEV_AI_REPORT_GPT_OSS.md").write_text(f"# Model: {MODEL_NAME}\nDate: {datetime.datetime.now().isoformat()}\n\n{ai_answer}")

print("\nSleeping 60 sec to avoid RateLimit...")
time.sleep(60)

earning = 1
wallet["total_earned"] += earning
wallet["bots"] = min(wallet["total_earned"] // 30, 100)
wallet["last_model"] = MODEL_NAME
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\nDONE - Model: {MODEL_NAME} | Total: ${wallet['total_earned']}")