# zindagi.py - FINAL - Hibernate + Dated + Revert Clone - English Only
import os, glob, json, requests, socket, subprocess
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DATE = datetime.now().strftime("%Y-%m-%d")

os.makedirs("reports", exist_ok=True)
os.makedirs("JEEV-Empire/reports", exist_ok=True)

API_KEY = os.getenv("OPENROUTER_API_KEY")
WALLET_FILE = "JEEV-Empire/jeev_wallet.json"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def load_wallet():
    try:
        with open(WALLET_FILE, "r") as f: return json.load(f)
    except: return {"balance":74.0, "real_wallet": REAL_WALLET, "status":"ONLINE"}

def save_wallet(w):
    with open(WALLET_FILE, "w") as f: json.dump(w, f, indent=2)
    with open("jeev_wallet.json", "w") as f: json.dump(w, f, indent=2)

wallet = load_wallet()
REAL_WALLET = wallet.get("real_wallet", REAL_WALLET)

def is_wifi_on():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

if not is_wifi_on():
    print("😴 WiFi OFF - HIBERNATING")
    wallet["status"] = "HIBERNATE - WiFi OFF"
    save_wallet(wallet)
    exit(0)

if not API_KEY:
    print("😴 API Key missing - HIBERNATE")
    wallet["status"] = "HIBERNATE - API Key missing"
    save_wallet(wallet)
    exit(0)

print(f"✅ WiFi ON - JEEV ZINDA - {REAL_WALLET}")

try:
    from kamana import find_bounties
    bounties, best_target = find_bounties()
    if best_target:
        risk = best_target.get('risk','LOW')
        STRATEGY = f"{best_target.get('type')} - {best_target.get('title')} - Risk:{risk} - ${best_target.get('reward')}"
        QUESTION_LINK = best_target.get('url','https://cantina.xyz/competitions/revert-v4lend')
        QUESTION_CODE = best_target.get('title','Revert v4lend')
    else:
        STRATEGY = "Revert v4lend - $50k - LOW"
        QUESTION_LINK = "https://cantina.xyz/competitions/revert-v4lend"
        QUESTION_CODE = "Revert v4lend"
except Exception as e:
    STRATEGY = f"Revert v4lend - $50k - {e}"
    QUESTION_LINK = "https://cantina.xyz/competitions/revert-v4lend"
    QUESTION_CODE = "Revert v4lend"

# --- CODE FETCH - NAYA - Revert repo clone! ---
target_path = ""
code_data = ""

try:
    subprocess.run(["rm", "-rf", "/tmp/v4lend"], check=False)
    subprocess.run(["git", "clone", "https://github.com/revert-finance/v4lend.git", "/tmp/v4lend"], check=False)
    print("✅ Revert repo cloned!")
except Exception as e:
    print(f"Clone fail: {e}")

# 1. V4Oracle.sol - Tera 2-min wala Oracle skill!
for f in glob.glob("/tmp/v4lend/src/oracle/*.sol", recursive=True)[:1]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        target_path = f
        code_data = file.read()[:4000]
        print(f"✅ Found Oracle: {target_path}")

# 2. V4Vault.sol - Reentrancy
if not code_data:
    for f in glob.glob("/tmp/v4lend/src/vault/*.sol", recursive=True)[:1]:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            target_path = f
            code_data = file.read()[:4000]
            print(f"✅ Found Vault: {target_path}")

# 3. Fallback - Premium wala
if not code_data:
    for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            target_path = f
            code_data = file.read()[:4000]
            print(f"⚠️ Fallback: {target_path}")

if not target_path:
    target_path = QUESTION_CODE

MY_REPORT_LINK = "https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/JEEV-Empire/JEEV_FINAL_REPORT.md"

prompt = f"ENGLISH ONLY. Audit {target_path}: {code_data}. Wallet {REAL_WALLET}. Strategy {STRATEGY}. Check for Oracle Manipulation in V4Oracle.sol using Chainlink+TWAP and Reentrancy in V4Vault.sol."
content = ""
for MODEL in ["qwen/qwen3-coder:free", "openrouter/free"]:
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}, json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens":5000}, timeout=120)
        if "choices" in r.json():
            content = r.json()["choices"][0]["message"]["content"]
            break
    except:
        continue

if not content:
    content = f"# Report {target_path}\nStrategy: {STRATEGY}\nWallet: {REAL_WALLET}\nAPI fail - Will retry."

LINKS_FILE = f"""
# 🔗 JEEV - Revert v4lend $50k - {TIMESTAMP}
WALLET: {REAL_WALLET}
STRATEGY: {STRATEGY}
QUESTION: {QUESTION_LINK}
File: {target_path}
ANSWER: {MY_REPORT_LINK}
Dated: reports/revert_v4lend_{TIMESTAMP}.md - Kabhi nahi urega!
"""

with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)

dated_name = f"reports/revert_v4lend_{TIMESTAMP}.md"
dated_name2 = f"JEEV-Empire/reports/revert_v4lend_{TIMESTAMP}.md"
with open(dated_name,"w",encoding="utf-8") as f: f.write(content)
with open(dated_name2,"w",encoding="utf-8") as f: f.write(content)

if "## Bug" in content or "### Bug" in content:
    bugs = content.split("## Bug")
    for i, bug in enumerate(bugs[1:], 1):
        bf = f"reports/revert_v4lend_BUG{i}_{TIMESTAMP}.md"
        bf2 = f"JEEV-Empire/reports/revert_v4lend_BUG{i}_{TIMESTAMP}.md"
        with open(bf,"w",encoding="utf-8") as f: f.write(f"# Bug {i}\n" + bug)
        with open(bf2,"w",encoding="utf-8") as f: f.write(f"# Bug {i}\n" + bug)

with open("LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)

wallet["status"] = "ONLINE - Report Ready"
wallet["last_run"] = str(datetime.now())
wallet["last_strategy"] = STRATEGY
save_wallet(wallet)

print(LINKS_FILE)
print(f"✅ SAVED {dated_name} - Never delete!")