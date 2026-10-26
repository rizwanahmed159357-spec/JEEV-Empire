# zindagi.py - FINAL - Hibernate + Double Link + Manual Phase - English Only
import os, glob, json, requests, socket
from datetime import datetime

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

# --- HIBERNATE RULE: WiFi Check ---
def is_wifi_on():
    try:
        # Google DNS check - WiFi hai ya nahi
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

if not is_wifi_on():
    print("😴 WiFi OFF - JEEV HIBERNATING - Not Dead!")
    wallet["status"] = "HIBERNATE - WiFi OFF - Sleeping, not dead"
    wallet["last_hibernate"] = str(datetime.now())
    wallet["last_status"] = "SLEEPING - Will wake when WiFi ON"
    save_wallet(wallet)
    # Exit with 0 so GitHub Action fail na ho, marega nahi
    exit(0)

if not API_KEY:
    print("😴 WiFi ON but API Key missing - HIBERNATE")
    wallet["status"] = "HIBERNATE - API Key missing - Sleeping"
    save_wallet(wallet)
    exit(0)

print(f"✅ WiFi ON - JEEV ZINDA - Wallet: {REAL_WALLET}")

# --- Kamana se target lo ---
try:
    from kamana import find_bounties
    bounties, best_target = find_bounties()
    if best_target:
        risk = best_target.get('risk','LOW')
        STRATEGY = f"{best_target.get('type')} - {best_target.get('title')} - Risk:{risk} - ${best_target.get('reward')}"
        QUESTION_LINK = best_target.get('url','https://immunefi.com/explore')
        QUESTION_CODE = best_target.get('title','Target')
    else:
        STRATEGY = "No fresh target (7-day rule)"
        QUESTION_LINK = "https://immunefi.com/explore"
        QUESTION_CODE = "No target"
except Exception as e:
    STRATEGY = f"Error: {e}"
    QUESTION_LINK = "https://immunefi.com/explore"
    QUESTION_CODE = "Demo"

# --- Code fetch ---
target_path = ""
code_data = ""
for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        target_path = f
        code_data = file.read()[:4000]
if not target_path:
    target_path = QUESTION_CODE

MY_REPORT_LINK = "https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/JEEV-Empire/JEEV_FINAL_REPORT.md"

# --- AI Report ---
prompt = f"ENGLISH ONLY. Audit {target_path}: {code_data}. Wallet {REAL_WALLET}. Strategy {STRATEGY}."
content = ""
for MODEL in ["qwen/qwen3-coder:free", "openrouter/free"]:
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}, json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens":5000}, timeout=120)
        if "choices" in r.json():
            content = r.json()["choices"][0]["message"]["content"]
            break
    except:
        continue

# Agar API fail bhi ho jaye to marega nahi, hibernate
if not content:
    print("😴 API Fail - HIBERNATE, not dead")
    wallet["status"] = "HIBERNATE - OpenRouter Fail - Sleeping"
    save_wallet(wallet)
    content = f"# Report {target_path}\nStrategy: {STRATEGY}\nWallet: {REAL_WALLET}\nWiFi ON but AI fail - Will retry next run."

# --- DOUBLE LINK + MANUAL PHASE ---
LINKS_FILE = f"""
# 🔗 JEEV - MANUAL PHASE (Abhi tu copy-paste karega)

WALLET: {REAL_WALLET}
STRATEGY: {STRATEGY}
STATUS: ONLINE - WiFi ON - Manual copy-paste phase

❓ QUESTION LINK (Jahan ka sawal hai):
{QUESTION_LINK}
File: {target_path}

📄 ANSWER LINK (Jahan se COPY karna hai):
{MY_REPORT_LINK}

👉 ABHI KA KAAM (Manual):
Tu mobile utha -> Answer Link se COPY -> Question Link pe PASTE

🔜 FUTURE PHASE (Jab har website connect hogi):
Manual hata denge -> FULL AUTO chalega -> Khud submit karega!

HIBERNATE RULE: WiFi band hua to JEEV soyega, marega nahi!
"""

with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)

# Wallet update - Zinda hai
wallet["status"] = "ONLINE - Report Ready - Manual copy-paste phase"
wallet["last_run"] = str(datetime.now())
wallet["last_strategy"] = STRATEGY
save_wallet(wallet)

print(LINKS_FILE)
print("✅ DONE - Hibernate rule added - Manual phase active")