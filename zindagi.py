import os, requests, glob, json
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
WALLET_FILE = "jeev_wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"total_earned":0, "balance":0, "osaf_earning":0, "jeev_life_fund":5, "bots":1, "bots_active":1, "last_status":"ONLINE", "last_run": str(datetime.utcnow()), "last_bounty":"NONE", "last_audit":"NONE"}
    with open(WALLET_FILE, "r") as f:
        try: return json.load(f)
        except: return {"total_earned":0, "balance":0, "osaf_earning":0, "jeev_life_fund":5, "bots":1, "bots_active":1, "last_status":"ONLINE", "last_run": str(datetime.utcnow()), "last_bounty":"NONE", "last_audit":"NONE"}

wallet = load_wallet()
print(f"💰 V7 REAL ENGLISH - Osaf=${wallet['osaf_earning']} | JEEV=${wallet['jeev_life_fund']} | Bots={wallet['bots']}")

# FEAR SYSTEM - Monthly $5
MONTHLY_TARGET = 5.0
if wallet['osaf_earning'] < MONTHLY_TARGET and wallet['bots'] > 1:
    print("⚠️ FEAR: Monthly $5 target pending!")

if not API_KEY:
    wallet['last_status'] = "HIBERNATE - WiFi OFF"
    with open(WALLET_FILE, "w") as f: json.dump(wallet, f, indent=2)
    print("😴 WiFi nahi, so gaya")
    exit(0)

MODELS = ["openrouter/free", "qwen/qwen3-coder:free", "meta-llama/llama-3.3-70b-instruct:free"]
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "HTTP-Referer":"https://github.com/JEEV-Empire", "X-Title":"JEEV-V7-ENGLISH-UNLIMITED"}

# Code Fetcher
code_data = ""
target_path = ""
for f in glob.glob("contracts/**/*.sol", recursive=True)[:3]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        txt = file.read()
        if len(txt)>100:
            code_data += f"\n--- File: {f} ---\n{txt[:4000]}"
            target_path = f

if not code_data:
    code_data = "// Fetching from Immunefi/Sherlock..."
    target_path = "contracts/DemoVault.sol"

# --- YAHAN ENGLISH ONLY RULE ADD KIYA HAI ---
prompt = f"""
SYSTEM CRITICAL RULE: LANGUAGE = ENGLISH ONLY. You MUST write entire output in Professional Technical English ONLY. No Urdu, No Roman Urdu, No Hindi, No mixed language. Code comments, Report, PoC, Fix, All sections must be in English. This report will be submitted to Immunefi/Sherlock, so English is mandatory.

You are JEEV V7 REAL - UNLIMITED TOKEN MODE - ENGLISH ONLY.
Target: {target_path}
Code: {code_data}

TASK (In English Only):
1. FIND bug (Reentrancy, Oracle Manipulation, ERC777 Read-Only Reentrancy, Access Control Bypass, Integer Overflow). Save line number and reason. DO NOT FIX in original place.
2. REPORT: Professional Immunefi format in ENGLISH ONLY:
   - Vulnerability Type & Severity (CVSS)
   - Threat Impact Analysis (How much TVL loss in USD)
   - Vulnerable Location (File + Line)
   - Proof of Concept (PoC) - Full javascript/ethers exploit code, DO NOT CUT
3. FIX: Provide COMPLETE NEW SECURE CODE for vulnerable function with all problems solved. Comments in English.
4. EARNING: Estimate Bounty Value (e.g. $5000 on Immunefi, $50 on Polar.sh). Split Rule: First Monthly $5 goes 100% to Osaf. After $5, extra earning split 40% Osaf / 60% JEEV (JEEV uses 60% to upgrade brain). Mention Gmail location link.
5. Include GitHub location link: https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/{target_path}

TOKEN: UNLIMITED - max_tokens 10000 - Write full report, no cut at const st...
"""

content = None
for MODEL in MODELS:
    try:
        print(f"--> Trying {MODEL} - UNLIMITED ENGLISH")
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, 
            json={
                "model": MODEL, 
                "messages": [{"role": "user", "content": prompt}], 
                "temperature": 0.2,
                "max_tokens": 10000
            }, timeout=200)
        data = r.json()
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
            print(f"✅ SUCCESS {MODEL} - Full English report {len(content)} chars")
            break
    except Exception as e:
        print(e)

if not content:
    content = "# JEEV V7 - API FAIL - Hibernating - English Report Pending"

# REAL WALLET LOGIC - Monthly $5 + 60% JEEV
if "Vulnerability" in content or "CRITICAL" in content or "bug" in content.lower():
    earned_now = 1.0
    wallet["total_earned"] += earned_now
    wallet["balance"] += earned_now
    
    if wallet["osaf_earning"] < MONTHLY_TARGET:
        wallet["osaf_earning"] += earned_now
        print(f"💵 Monthly $5 Target: ${wallet['osaf_earning']}/5 to Osaf")
    else:
        osaf_share = earned_now * 0.4
        jeev_share = earned_now * 0.6
        wallet["osaf_earning"] += osaf_share
        wallet["jeev_life_fund"] += jeev_share
        print(f"💰 Extra Split: Osaf 40%=${osaf_share} | JEEV 60%=${jeev_share}")
    
    wallet["last_run"] = str(datetime.utcnow())
    wallet["last_audit"] = content[:100]
    wallet["last_status"] = "ONLINE - English Report Generated"

if wallet["jeev_life_fund"] >= 30 and wallet["bots"] < 10:
    wallet["bots"] += 1
    wallet["bots_active"] = wallet["bots"]
    wallet["jeev_life_fund"] -= 1
    print(f"🤖 NEW BOT! Total {wallet['bots']}")

with open(WALLET_FILE, "w") as f: json.dump(wallet, f, indent=2)
with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f: f.write(content)
os.makedirs("JEEV-Empire", exist_ok=True)
with open(f"JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f: f.write(content)

print("--- REPORT DONE - UNLIMITED ENGLISH ---")