# zindagi.py - FINAL - Double Link System for Immunefi + All Sites - English Only
import os, glob, json, requests
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY")
WALLET_FILE = "JEEV-Empire/jeev_wallet.json"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def load_wallet():
    try:
        with open(WALLET_FILE, "r") as f: return json.load(f)
    except: return {"balance":74.0, "real_wallet": REAL_WALLET}

wallet = load_wallet()
REAL_WALLET = wallet.get("real_wallet", REAL_WALLET)

# Get target from kamana
try:
    from kamana import find_bounties
    bounties, best_target = find_bounties()
    if best_target:
        risk = best_target.get('risk','LOW')
        STRATEGY = f"{best_target.get('type')} - {best_target.get('title')} - Risk:{risk} - Days:{best_target.get('days_ago')} - ${best_target.get('reward')}"
        QUESTION_LINK_IMMUNEFI = best_target.get('url','https://immunefi.com/explore')
        QUESTION_CODE_PATH = best_target.get('title','Target')
    else:
        STRATEGY = "No fresh target (7-day rule)"
        QUESTION_LINK_IMMUNEFI = "https://immunefi.com/explore"
        QUESTION_CODE_PATH = "No target"
except Exception as e:
    STRATEGY = f"Error: {e}"
    QUESTION_LINK_IMMUNEFI = "https://immunefi.com/explore"
    QUESTION_CODE_PATH = "Demo"

# Fetch code
target_path = ""
code_data = ""
for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
    with open(f, "r", encoding="utf-8", errors="ignore") as file:
        target_path = f
        code_data = file.read()[:4000]
if not target_path:
    target_path = QUESTION_CODE_PATH

# MY ANSWER LINKS (Where JEEV wrote answer)
MY_REPORT_LINK = "https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/JEEV-Empire/JEEV_FINAL_REPORT.md"
MY_CODE_LINK = f"https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/{target_path}"

# --- OPENROUTER CALL (English) ---
prompt = f"ENGLISH ONLY. Audit {target_path} code: {code_data}. Wallet {REAL_WALLET}. Strategy {STRATEGY}. Write vulnerability report."
content = ""
if API_KEY:
    for MODEL in ["qwen/qwen3-coder:free", "openrouter/free"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"}, json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens":5000}, timeout=120)
            if "choices" in r.json():
                content = r.json()["choices"][0]["message"]["content"]
                break
        except: pass

if not content:
    content = f"# Report for {target_path}\nStrategy: {STRATEGY}\nWallet: {REAL_WALLET}\n\nManual review needed."

# --- DOUBLE LINK FILE - For EVERY website ---
LINKS_FILE = f"""
# 🔗 JEEV DOUBLE LINK SYSTEM - For Immunefi & All Sites

REAL WALLET (Payout): {REAL_WALLET}
VIRTUAL FAKE WALLET (Bot Test): ${wallet.get('balance',0)}
STRATEGY: {STRATEGY}

📍 FOR IMMUNEFI (And Every Site Same Logic)


❓ QUESTION LINK (Jahan ka sawal/code hai - Ispe click karo):
{QUESTION_LINK_IMMUNEFI}
File: {target_path} / {QUESTION_CODE_PATH}

📄 ANSWER LINK (Jahan JEEV ne jawab likha hai - Yahan se COPY karo):
{MY_REPORT_LINK}

👉 ACTION:
1. Question Link dabao -> Immunefi khulega
2. Answer Link dabao -> GitHub report khulega -> Wahan se report COPY karo
3. Wapas Question Link pe jao -> Submit Bug pe paste kardo

📍 FOR POLAR.SH

❓ QUESTION: https://github.com/polar-sh/polar/issues
📄 ANSWER: {MY_REPORT_LINK}

📍 FOR SHERLOCK

❓ QUESTION: https://app.sherlock.xyz/audits/contests
📄 ANSWER: {MY_REPORT_LINK}

CODE LOCATION: {MY_CODE_LINK}
"""

with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)

print(LINKS_FILE)
print("DONE - Email will be sent by workflow with GitHub Report Link")