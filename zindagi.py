import os, requests, glob, json
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
POLAR_TOKEN = os.getenv("POLAR_ACCESS_TOKEN") # Naya - Polar link ke liye
WALLET_FILE = "jeev_wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"total_earned":0, "balance":0, "osaf_earning":0, "jeev_life_fund":5, "bots":1, "bots_active":1, "last_status":"ONLINE", "last_run": str(datetime.utcnow()), "last_bounty":"NONE", "last_audit":"NONE"}
    with open(WALLET_FILE, "r") as f:
        try: return json.load(f)
        except: return {"total_earned":0, "balance":0, "osaf_earning":0, "jeev_life_fund":5, "bots":1, "bots_active":1, "last_status":"ONLINE", "last_run": str(datetime.utcnow()), "last_bounty":"NONE", "last_audit":"NONE"}

wallet = load_wallet()
print(f"💰 V8 REAL LINK - Osaf=${wallet['osaf_earning']} | JEEV=${wallet['jeev_life_fund']} | Bots={wallet['bots']}")

# --- NAYA: REAL BOUNTY LINK FINDER ---
real_bounty_links = []
real_bounty_info = "No Polar Token - Demo Mode"
if POLAR_TOKEN:
    try:
        print("🔍 Polar.sh pe asal $ wale issues dhoond raha hun...")
        # Polar ki public API se real issues la raha hai
        headers_polar = {"Authorization": f"Bearer {POLAR_TOKEN}"}
        # Ye API GitHub ke wo issues deti hai jin pe $ laga hai
        resp = requests.get("https://api.polar.sh/v1/issues/search?is:open", headers=headers_polar, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # 3 real links nikal lete hain
            for item in data.get("items", [])[:3]:
                link = item.get("issue_url") or item.get("html_url")
                reward = item.get("reward", "$50")
                if link:
                    real_bounty_links.append(f"{link} - Reward {reward}")
            real_bounty_info = "\n".join(real_bounty_links) if real_bounty_links else "No open bounty found"
            print(f"✅ REAL LINKS MIL GAYE: {real_bounty_info}")
        else:
            real_bounty_info = "Polar API Error - Using GitHub Search Fallback"
            # Fallback: GitHub pe polar label wale issues dhoondo
            gh = requests.get("https://api.github.com/search/issues?q=label:polar+is:open&per_page=3", timeout=15).json()
            for i in gh.get("items", [])[:3]:
                real_bounty_links.append(f"{i['html_url']} - Check Polar Badge")
            real_bounty_info = "\n".join(real_bounty_links)
    except Exception as e:
        print(f"Polar fetch error: {e}")
        real_bounty_info = "Error fetching, demo link: https://github.com/polar-sh/examples/issues"
else:
    print("⚠️ POLAR_ACCESS_TOKEN nahi mila - Demo link use kar raha hun")
    real_bounty_info = "Demo: https://github.com/polar-sh/polar/issues - Yahan $ wale issues hain (Token lagao to real link ayega)"
    real_bounty_links = [real_bounty_info]
# --- LINK FINDER KHATAM ---

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
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "HTTP-Referer":"https://github.com/JEEV-Empire", "X-Title":"JEEV-V8-REAL-LINK"}

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

prompt = f"""
SYSTEM CRITICAL RULE: LANGUAGE = ENGLISH ONLY. You MUST write entire output in Professional Technical English ONLY. No Urdu, No Roman Urdu, No Hindi, No mixed language. Code comments, Report, PoC, Fix, All sections must be in English. This report will be submitted to Immunefi/Sherlock, so English is mandatory.

You are JEEV V8 REAL - REAL LINK MODE - ENGLISH ONLY.
Target: {target_path}
Code: {code_data}

REAL BOUNTY CONTEXT (User wants to submit to these real links):
{real_bounty_info}

TASK (In English Only):
1. FIND bug (Reentrancy, Oracle Manipulation, ERC777 Read-Only Reentrancy, Access Control Bypass, Integer Overflow). Save line number and reason. DO NOT FIX in original place.
2. REPORT: Professional Immunefi format in ENGLISH ONLY:
   - Vulnerability Type & Severity (CVSS)
   - Threat Impact Analysis (How much TVL loss in USD)
   - Vulnerable Location (File + Line)
   - Proof of Concept (PoC) - Full javascript/ethers exploit code, DO NOT CUT
3. FIX: Provide COMPLETE NEW SECURE CODE for vulnerable function with all problems solved. Comments in English.
4. EARNING: Estimate Bounty Value (e.g. $5000 on Immunefi, $50 on Polar.sh). Split Rule: First Monthly $5 goes 100% to Osaf. After $5, extra earning split 40% Osaf / 60% JEEV (JEEV uses 60% to upgrade brain).
5. FINAL SECTION MUST BE: 
   REAL SUBMISSION LINKS:
   {real_bounty_info}
   Instruction: Go to above link, paste the FIX code in comment, click Submit. This is manual and 100% safe, no ban.
6. Include GitHub location link: https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/{target_path}

TOKEN: UNLIMITED - max_tokens 10000 - Write full report, no cut.
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
    content = "# JEEV V8 - API FAIL - Hibernating - English Report Pending"

# Add Real Links at top of report manually too
final_report = f"# REAL BOUNTY LINKS FOR MANUAL SUBMIT (100% SAFE - NO BAN)\n{real_bounty_info}\n\n---\n\n" + content

# REAL WALLET LOGIC
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
    wallet["last_status"] = "ONLINE - Real Link Mode"
    wallet["last_bounty"] = real_bounty_info[:200]

if wallet["jeev_life_fund"] >= 30 and wallet["bots"] < 10:
    wallet["bots"] += 1
    wallet["bots_active"] = wallet["bots"]
    wallet["jeev_life_fund"] -= 1
    print(f"🤖 NEW BOT! Total {wallet['bots']}")

with open(WALLET_FILE, "w") as f: json.dump(wallet, f, indent=2)
with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f: f.write(final_report)
os.makedirs("JEEV-Empire", exist_ok=True)
with open(f"JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f: f.write(final_report)

print("--- REPORT DONE - REAL LINKS INCLUDED ---")
print(f"LINKS: {real_bounty_info}")