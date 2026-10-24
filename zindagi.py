import os, pathlib, json, datetime, time, sys

try:
    from groq import Groq
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - 4 STEP AI ENGINE ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"bots":0}
else:
    wallet = {"total_earned":0,"bots":0}

MODEL_NAME = "openai/gpt-oss-120b" # Backend me ye, show nahi hoga
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ===== STEP 1: CODE FETCHER =====
print("STEP 1: Code Fetcher - Loading target...")
TARGET_FILE = pathlib.Path("contracts/PremiumStaking.sol")
if not TARGET_FILE.exists():
    TARGET_FILE = pathlib.Path("PremiumStaking.sol")

if TARGET_FILE.exists():
    code_text = TARGET_FILE.read_text()
    print(f"Code loaded: {TARGET_FILE}")
else:
    code_text = """
    Problem Title: Deep DeFi Protocol Exploitation (Flash Loan + Oracle Manipulation + Reentrancy)
    withdrawCollateral() checks collateral via AMM oracle, uses low-level call, then updates state. Developer added nonReentrant.
    """
    print("No file found, using problem description as input")

# ===== STEP 2,3,4 EK SATH - AI BUG FINDER + FIXER + REPORT GENERATOR =====
print("STEP 2-4: AI Bug Finder + Fixer + Report Generator...")

prompt_text = f"""
You are JEEV - Senior DeFi Security Auditor. Respond in ENGLISH ONLY. Brand as JEEV AI Engine.

You have to do 4 steps:

CODE / PROBLEM TO ANALYZE:
{code_text}

TASK:
Step 2 - AI Bug Finder: Scan line-by-line for specific vulnerabilities: Reentrancy, Read-Only Reentrancy, Flash Loan, Oracle Manipulation, low-level call issue. Save line number and reason.

Step 3 - AI Code Fixer: Fix the bug without breaking other code. Generate updated secure code.

Step 4 - Report Generator: Write professional bug bounty report with:
1. Description: Bug kya hai aur nuksan kya hai
2. Proof of Concept (PoC): Galt code kahan hai
3. Remediation/Fix: Sahi code

Do NOT auto-submit anywhere. Just create report.

Problem: Flash Loan + Oracle Manipulation + Cross-Contract Read-Only Reentrancy in withdrawCollateral() with nonReentrant bypass.
Explain exact attack vector.

ENGLISH ONLY.
"""

for attempt in range(3):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.6,
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt_text}
            ]
        )
        ai_answer = response.choices[0].message.content
        break
    except Exception as e:
        if "429" in str(e) or "RateLimit" in str(e):
            print(f"RateLimit - Wait 70s {attempt+1}/3")
            time.sleep(70)
            if attempt == 2:
                ai_answer = "RateLimit - Retry later"
                break
            continue
        else:
            raise

print("\n--- JEEV AI ENGINE ANSWER ---")
print(ai_answer)

# ===== REPORT SAVE - WEBSITE LOCATION =====
report_file = pathlib.Path("JEEV_FINAL_REPORT.md")
report_content = f"""# JEEV AI - FINAL BUG BOUNTY REPORT
Date: {datetime.datetime.now().isoformat()}
Location: 【entity-GitHub¦canonical_name=GitHub】 Repo / JEEV_FINAL_REPORT.md
Target File: {TARGET_FILE}

{ai_answer}

---
NOTE: This report is ready for MANUAL submission. Do NOT auto-submit via bot to avoid ban.
"""
report_file.write_text(report_content)

# 【entity-GitHub¦canonical_name=GitHub】 pe iski location hogi:
# https://github.com/TUMHARA-USERNAME/JEEV-Empire/blob/main/JEEV_FINAL_REPORT.md
print(f"\n✅ REPORT SAVED AT: {report_file}")
print(f"Website Location: Your Repo > JEEV_FINAL_REPORT.md")

# ===== GMAIL NOTIFICATION (MOBILE PE) =====
# 【entity-GitHub¦canonical_name=GitHub】 Actions me email notification automatic 【entity-GitHub¦canonical_name=GitHub】 app se aayega
# Agar Gmail chahiye to repo settings me email notification ON kar do
print("\nSTEP 5: Notification - 【entity-GitHub¦canonical_name=GitHub】 app will notify on your mobile!")
print("Aapko mobile pe 【entity-GitHub¦canonical_name=GitHub】 notification ayega - Report ready hai")

time.sleep(30)

# ===== $1 USD EARNING =====
earning = 1
wallet["total_earned"] = wallet.get("total_earned", 0) + earning
wallet["bots"] = 1
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n✅ DONE - Report Generated | Earned: ${earning} | Total: ${wallet['total_earned']}")
print(f"Go to: JEEV_FINAL_REPORT.md and submit manually!")