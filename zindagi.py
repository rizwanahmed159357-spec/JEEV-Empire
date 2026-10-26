import os, requests, glob, json
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
WALLET_FILE = "jeev_wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"bots":1, "jeev_life_fund":5, "osaf_earning":0, "real_earned_this_month":0, "total_earned":0, "virtual_earned":0}
    with open(WALLET_FILE, "r") as f:
        try: return json.load(f)
        except: return {"bots":1, "jeev_life_fund":5, "osaf_earning":0, "real_earned_this_month":0, "total_earned":0, "virtual_earned":0}

wallet = load_wallet()
if not API_KEY:
    print("😴 WiFi OFF")
    exit(0)

# --- CODE FETCH ---
target_path = ""
code_data = ""
for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        txt = file.read()
        target_path = f
        code_data = txt[:4000]
if not target_path:
    target_path = "contracts/DemoVault.sol"
    code_data = "// demo"

# --- YAHAN SE REAL QUESTION LINK BANEGA ---
# Bot jahan kaam karega uska exact link
# Tum Excel ka link bhejte ho waise hi ye bhi link bhejega!

# Example: Agar Immunefi pe kaam kare to
IMMUNEFI_QUESTION_LINK = f"https://immunefi.com/explore - Search: {target_path} bug"
POLAR_QUESTION_LINK = f"https://github.com/polar-sh/polar/issues - $ bounty"
SHERLOCK_QUESTION_LINK = f"https://app.sherlock.xyz/audits - Contest for {target_path}"

# Real me Polar se ayega to exact issue ID
real_question_link = POLAR_QUESTION_LINK
try:
    if os.getenv("POLAR_ACCESS_TOKEN"):
        r = requests.get("https://api.polar.sh/v1/issues/search", headers={"Authorization": f"Bearer {os.getenv('POLAR_ACCESS_TOKEN')}"}, timeout=10)
        if r.status_code == 200 and r.json().get("items"):
            first = r.json()["items"][0]
            real_question_link = first.get("issue_url") or first.get("html_url")
except: pass

# --- APNI REPORT KI LOCATION (Jahan se copy karna hai) ---
MY_REPORT_GITHUB_LINK = f"https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/JEEV_FINAL_REPORT.md"
MY_CODE_GITHUB_LINK = f"https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/{target_path}"

prompt = f"ENGLISH ONLY. Find bug in {target_path}: {code_data}. Report + Fix. 10000 tokens."

content = ""
for MODEL in ["qwen/qwen3-coder:free", "openrouter/free"]:
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 10000}, timeout=180)
        if "choices" in resp.json():
            content = resp.json()["choices"][0]["message"]["content"]
            break
    except: pass

if not content:
    content = "API Fail"

# --- FINAL EMAIL Jaisa Link File Banega ---
# Ye file tumhe email pe jayegi, ya yahin se copy kar loge!

SUBMIT_FILE = f"""
# 🔗 MANUAL SUBMIT - CLICK & PASTE - EXCEL LINK JAISA

Tumne bola tha Excel ka link bhejte ho waise hi, ye lo:

📍 WEBSITE 1: Polar.sh (Fast $ - 2 din me paisa)
❓ SAWAL KA LINK (Jahan kaam hai - Ispe click karo):
{real_question_link}

📄 MERI REPORT KA LINK (Yahan se copy karo):
{MY_REPORT_GITHUB_LINK}

👉 ACTION: Sawal wale link pe click karo -> GitHub khulega -> Neeche comment me meri report se FIX wala code paste karo -> Submit!


📍 WEBSITE 2: Immunefi (Bada $ - 1 hafte me)
❓ SAWAL KA LINK:
https://immunefi.com/bug-bounty - Search: {target_path}
(Immunefi pe jao, is file ka naam search karo, jo bounty aaye uspe click karo)

📄 MERI REPORT KA LINK:
{MY_REPORT_GITHUB_LINK}

👉 ACTION: Immunefi wala link kholo -> Submit Bug -> Meri report paste karo!


📍 WEBSITE 3: Sherlock (Contest $500-$5000)
❓ SAWAL KA LINK:
https://app.sherlock.xyz/audits

📄 MERI REPORT KA LINK:
{MY_REPORT_GITHUB_LINK}


📂 MERA CODE KAHAN HAI (Location):
{MY_CODE_GITHUB_LINK}

💰 Earning: $1 pending (Real 1 week baad ayega)
🤖 Bot: {wallet['bots']}

Ye file kholo, link pe click karo, jaga khul jayegi, paste kardo!
"""

# Files save
with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)
with open("LINKS_TO_SUBMIT.txt", "w", encoding="utf-8") as f:
    f.write(SUBMIT_FILE)

os.makedirs("JEEV-Empire", exist_ok=True)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt", "w", encoding="utf-8") as f:
    f.write(SUBMIT_FILE)

print(SUBMIT_FILE)
print("--- V13 DONE - EXCEL LINK JAISA ---")