# zindagi.py - FINAL HONEST - Real audit - No fake
import os, glob, json, requests, socket, subprocess
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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

def is_wifi_on():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except: return False

if not is_wifi_on():
    print("😴 WiFi OFF")
    wallet["status"] = "HIBERNATE - WiFi OFF"
    save_wallet(wallet)
    exit(0)

if not API_KEY:
    wallet["status"] = "HIBERNATE - API Key missing"
    save_wallet(wallet)
    exit(0)

try:
    from kamana import find_bounties
    bounties, best_target = find_bounties()
    if best_target:
        STRATEGY = f"{best_target.get('type')} - {best_target.get('title')} - {best_target.get('risk')} - ${best_target.get('reward')}"
        QUESTION_LINK = best_target.get('url','https://cantina.xyz/competitions/revert-v4lend')
        QUESTION_CODE = best_target.get('title','Revert v4lend')
    else:
        STRATEGY = "COMPETITION - Revert v4lend - TO_CHECK - $50000"
        QUESTION_LINK = "https://cantina.xyz/competitions/revert-v4lend"
        QUESTION_CODE = "Revert v4lend"
except Exception as e:
    STRATEGY = f"Revert v4lend - TO_CHECK - {e}"
    QUESTION_LINK = "https://cantina.xyz/competitions/revert-v4lend"
    QUESTION_CODE = "Revert v4lend"

# --- CODE FETCH - 8000 chars - Real code ---
target_path = ""
code_data = ""

try:
    subprocess.run(["rm", "-rf", "/tmp/v4lend"], check=False)
    subprocess.run(["git", "clone", "https://github.com/revert-finance/v4lend.git", "/tmp/v4lend"], check=False)
    print("✅ Cloned revert")
except Exception as e:
    print(f"Clone fail {e}")

for f in glob.glob("/tmp/v4lend/src/oracle/*.sol", recursive=True)[:1]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        target_path = f
        code_data = file.read()[:8000]
        print(f"✅ Oracle {target_path}")

if not code_data:
    for f in glob.glob("/tmp/v4lend/src/vault/*.sol", recursive=True)[:1]:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            target_path = f
            code_data = file.read()[:8000]
            print(f"✅ Vault {target_path}")

if not code_data:
    for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            target_path = f
            code_data = file.read()[:8000]

if not target_path:
    target_path = QUESTION_CODE

# --- HONEST PROMPT - Fake nahi banayega ---
prompt = f"""You are a honest Cantina auditor. Audit this Solidity file honestly.

File: {target_path}
Code:
{code_data}

Wallet {REAL_WALLET} is reporter, not vulnerable.

Instructions:
- Read code carefully. Check maxDifference, TWAP window, staleness, reentrancy.
- If you find REAL bug, give Title, Severity High/Medium, Description, Impact, PoC with forge test.
- If NO bug found, clearly say "No critical bug found in this file - LOW risk" and explain why code is safe.
- DO NOT fabricate bug. DO NOT say "please provide full code". Work with given code.
- English only.

Output format:
# Finding - [Severity]
Description, Impact, PoC if bug exists, else No bug found.
Reporter: {REAL_WALLET}
"""

content = ""
for MODEL in ["qwen/qwen3-coder:free", "openrouter/free"]:
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}, json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens":6000}, timeout=180)
        j = r.json()
        if "choices" in j:
            content = j["choices"][0]["message"]["content"]
            break
    except Exception as e:
        print(f"Model fail {e}")
        continue

if not content:
    content = f"# Audit {target_path}\nNo response from AI. Strategy {STRATEGY}\nWallet {REAL_WALLET}\nWill retry next run."

MY_REPORT_LINK = f"https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/reports/revert_v4lend_{TIMESTAMP}.md"

LINKS_FILE = f"""
QUESTION: {QUESTION_LINK}
File: {target_path}
ANSWER: {MY_REPORT_LINK}
STRATEGY: {STRATEGY}
Dated: reports/revert_v4lend_{TIMESTAMP}.md - Real audit, no fake
"""

with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)

dated_name = f"reports/revert_v4lend_{TIMESTAMP}.md"
dated_name2 = f"JEEV-Empire/reports/revert_v4lend_{TIMESTAMP}.md"
with open(dated_name,"w",encoding="utf-8") as f: f.write(content)
with open(dated_name2,"w",encoding="utf-8") as f: f.write(content)

with open("LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)

wallet["status"] = "ONLINE - Real audit done"
wallet["last_run"] = str(datetime.now())
wallet["last_strategy"] = STRATEGY
save_wallet(wallet)

print(LINKS_FILE)
print(f"✅ SAVED {dated_name} - Honest report")