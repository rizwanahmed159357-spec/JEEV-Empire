# zindagi.py - Competition vs Bounty Link Generator
import os, requests, glob, json
from datetime import datetime

API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY")
WALLET_FILE = "jeev_wallet.json"

def load_wallet():
    if not os.path.exists(WALLET_FILE):
        return {"bots":1, "jeev_life_fund":5, "osaf_earning":0}
    try:
        with open(WALLET_FILE, "r") as f: return json.load(f)
    except: return {"bots":1}

wallet = load_wallet()

try:
    import kamana
    bounties, best_target = kamana.find_bounties()
except:
    bounties = []
    best_target = None

if not best_target:
    best_target = {"name": "No fresh target today", "type": "WAIT", "url": "https://immunefi.com/bug-bounties/", "risk": "HIGH", "max_bounty": 0, "days_ago": 999}

code_data = "// demo vault"
target_path = "contracts/DemoVault.sol"
for f in glob.glob("contracts/**/*.sol", recursive=True)[:1]:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            code_data = file.read()[:4000]
            target_path = f
    except: pass

if best_target["type"] == "COMPETITION":
    QUESTION_LINK = best_target["url"]
    STRATEGY = f"COMPETITION hai - Duplicate ka dar nahi! Risk: {best_target['risk']}"
elif best_target["type"] == "BOUNTY":
    QUESTION_LINK = best_target["url"]
    STRATEGY = f"BOUNTY hai par FRESH hai - {best_target.get('days_ago', 0)} din pehle update. Risk LOW!"
else:
    QUESTION_LINK = "https://immunefi.com/competitions/"
    STRATEGY = "Aaj koi fresh target nahi. Kal check karenge."

MY_REPORT_LINK = "https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/JEEV_FINAL_REPORT.md"
content = "Demo report - AI scan complete"

SUBMIT_FILE = f"""
# 🎯 JEEV - COMPETITION vs BOUNTY DECISION

🤖 DECISION: {best_target['type']} - {best_target['name']}
📊 STRATEGY: {STRATEGY}
⏰ Last Updated: {best_target.get('days_ago', 'N/A')} days ago
💰 Max Bounty: ${best_target.get('max_bounty', 0)}
🔗 URL: {best_target['url']}

📍 SAWAL KA LINK:
{QUESTION_LINK}

📄 MERI REPORT KA LINK:
{MY_REPORT_LINK}

📂 MERA CODE:
{target_path}
"""

with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)
with open("LINKS_TO_SUBMIT.txt", "w", encoding="utf-8") as f:
    f.write(SUBMIT_FILE)

print(SUBMIT_FILE)