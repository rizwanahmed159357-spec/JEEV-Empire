import os, pathlib, json, datetime, time, sys

try:
    from groq import Groq
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - ELITE ZINDAGI MODE ===")

# ===== WALLET FIX - PURANA WALLET BHI CHALEGA =====
WALLET_FILE = pathlib.Path("jeev_wallet.json")
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
        wallet.setdefault("fear_level", 10)
        wallet.setdefault("balance_cents", 100)
        wallet.setdefault("robots_dead", 0)
        wallet.setdefault("bots", 1)
        wallet.setdefault("total_earned", 0.0)
    except:
        wallet = {"total_earned":0.0, "bots":1, "robots_dead":0, "fear_level":10, "balance_cents":100}
else:
    wallet = {"total_earned":0.0, "bots":1, "robots_dead":0, "fear_level":10, "balance_cents":100}

print(f"Status: Bots={wallet.get('bots')} | Balance=${wallet.get('total_earned')} | Fear={wallet.get('fear_level')}%")

MODEL_NAME = "openai/gpt-oss-120b"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ===== STEP 1: TARGET LOADER =====
TARGET_FILE = pathlib.Path("contracts/PremiumStaking.sol")
if not TARGET_FILE.exists(): TARGET_FILE = pathlib.Path("PremiumStaking.sol")

if TARGET_FILE.exists():
    code_text = TARGET_FILE.read_text()
else:
    code_text = """
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.20;
    interface IUniswapV3Pool {
        function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked);
    }
    contract PremiumVaultStaking {
        function getVaultAssetPrice() public view returns (uint256) {
            (uint160 sqrtPriceX96,,,,,, bool unlocked) = IUniswapV3Pool(address(0)).slot0();
            return uint256(sqrtPriceX96);
        }
    }
    """

bug_memory = {}

prompt_bug = f"""
You are the JEEV AI Core Engine, elite Web3 Security Auditor. 
CRITICAL: Do NOT fix, only REMEMBER flaw.
CODE: {code_text}
VECTORS: 1.Read-Only Reentrancy 2.Oracle Manipulation 3.Flash Loan 4.Low-Level Call 5.Math Discrepancies
OUTPUT: Function, Line Numbers, Attack Vector, Root Cause. ENGLISH ONLY.
"""

print("\n[STEP 2] Bug Finder - Yaad rakhega...")
for _ in range(3):
    try:
        r1 = client.chat.completions.create(model=MODEL_NAME, temperature=0.6, max_tokens=6000, messages=[{"role":"user","content":prompt_bug}])
        bug_memory["bug"] = r1.choices[0].message.content
        break
    except: time.sleep(70)

prompt_fix = f"""
You are JEEV AI Core Engine, Principal Engineer.
BUG MEMORY: {bug_memory.get('bug','')}
TASK: Generate Immunefi report with COMPLETE fixed Solidity contract from scratch. No TODOs.
1.EXECUTIVE SUMMARY 2.PoC 3.FULL NEW CODE with ReentrancyGuard, Chainlink, SafeERC20. ENGLISH ONLY.
"""

print("\n[STEP 3-4] Report Generator...")
for _ in range(3):
    try:
        r2 = client.chat.completions.create(model=MODEL_NAME, temperature=0.6, max_tokens=8000, messages=[{"role":"user","content":prompt_fix}])
        full_report = r2.choices[0].message.content
        break
    except: time.sleep(70)

report_file = pathlib.Path("JEEV_FINAL_REPORT.md")
report_file.write_text(full_report)
repo_url = os.environ.get("GITHUB_REPOSITORY", "your-username/JEEV-Empire")
report_link = f"https://github.com/{repo_url}/blob/main/JEEV_FINAL_REPORT.md"

gmail_html = pathlib.Path("JEEV_GMAIL_ALERT.html")
gmail_html.write_text(f"<html><body><h2>🚨 JEEV AI - Elite Bug Found!</h2><p><a href='{report_link}'>{report_link}</a></p><p>Total: $2.5M | Tera: $2,499,999 | Mera: $1</p></body></html>")

# ===== ZINDAGI DAR LOGIC - FIXED WITH .GET() =====
daily_need = 5.0
current_earned = wallet.get("total_earned", 0.0)
current_fear = wallet.get("fear_level", 10)
current_cents = wallet.get("balance_cents", 100)
current_bots = wallet.get("bots", 1)

if current_earned < daily_need:
    wallet["fear_level"] = min(100, current_fear + 30)
    wallet["balance_cents"] = current_cents - 1
    print(f"⚠️ DAR! Need ${daily_need} | Fear {wallet['fear_level']}%")
    if wallet.get("balance_cents", 0) <= 0 and current_bots > 0:
        wallet["robots_dead"] = wallet.get("robots_dead", 0) + 1
        wallet["bots"] = max(0, current_bots - 1)
else:
    wallet["fear_level"] = max(0, current_fear - 20)

if current_earned >= 30 and current_bots < 10:
    wallet["bots"] = min(10, int(current_earned // 30))

earning = 1.0
wallet["total_earned"] = current_earned + earning
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n✅ DONE! Report: {report_file} | Link: {report_link} | Earned ${earning}")