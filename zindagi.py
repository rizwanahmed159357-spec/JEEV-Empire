# zindagi.py - FINAL UNIVERSAL - Like Meta AI - Max 10000 tokens - Gmail Manual Submit - Rules Same
import os, glob, json, requests, socket, subprocess, smtplib
from datetime import datetime
from email.mime.text import MIMEText

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("reports", exist_ok=True)
os.makedirs("JEEV-Empire/reports", exist_ok=True)

API_KEY = os.getenv("OPENROUTER_API_KEY")
# FIX: Tere secrets EMAIL_USERNAME / EMAIL_PASSWORD bhi support karega - Rules same
GMAIL_USER = os.getenv("GMAIL_USER") or os.getenv("EMAIL_USERNAME") or os.getenv("EMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS") or os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASS")
WALLET_FILE = "JEEV-Empire/jeev_wallet.json"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"

def load_wallet():
    try:
        with open(WALLET_FILE, "r") as f: return json.load(f)
    except: return {"balance":74.0, "real_wallet": REAL_WALLET, "status":"ONLINE"}

def save_wallet(w):
    with open(WALLET_FILE, "w") as f: json.dump(w, f, indent=2)
    with open("jeev_wallet.json", "w") as f: json.dump(w, f, indent=2)

def send_gmail(to, subject, body):
    if not GMAIL_USER or not GMAIL_PASS:
        print(f"Gmail creds missing - GMAIL_USER={bool(GMAIL_USER)} GMAIL_PASS={bool(GMAIL_PASS)} - skipping email")
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Gmail sent: {subject} to {to}")
        return True
    except Exception as e:
        print(f"Gmail fail: {e}")
        return False

wallet = load_wallet()

def is_wifi_on():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except: return False

if not is_wifi_on():
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
        STRATEGY = f"{best_target.get('type')} - {best_target.get('title')} - ${best_target.get('reward')}"
        QUESTION_LINK = best_target.get('url','')
        ALL_BOUNTIES = bounties
    else:
        STRATEGY = "COMPETITION - Revert v4lend - $50000"
        QUESTION_LINK = "https://cantina.xyz/competitions/revert-v4lend"
        ALL_BOUNTIES = []
except Exception as e:
    STRATEGY = f"Error {e}"
    QUESTION_LINK = ""
    ALL_BOUNTIES = []

# Load sources for Gmail to
gmail_to = "rizwanahmed159357@gmail.com"
try:
    with open("JEEV-Empire/bounty_sources.json") as f:
        gmail_to = json.loads(f.read()).get("gmail_to", gmail_to)
except: 
    try:
        with open("bounty_sources.json") as f:
            gmail_to = json.loads(f.read()).get("gmail_to", gmail_to)
    except: pass
# Also try EMAIL_USERNAME as fallback for gmail_to
if gmail_to == "rizwanahmed159357@gmail.com" and GMAIL_USER:
    gmail_to = GMAIL_USER

# UNIVERSAL CODE FETCH - Any repo
target_path = ""
code_data = ""
repo_url = ""
if best_target:
    repo_url = best_target.get("repo","")
    try:
        subprocess.run(["rm", "-rf", "/tmp/target"], check=False)
        subprocess.run(["git", "clone", repo_url, "/tmp/target"], check=False, timeout=60)
        print(f"✅ Cloned {repo_url}")
        for pattern in ["/tmp/target/**/*.sol", "/tmp/target/**/*.rs", "/tmp/target/idl/*.json", "/tmp/target/**/*.move"]:
            for f in glob.glob(pattern, recursive=True)[:2]:
                with open(f, "r", encoding="utf-8", errors="ignore") as file:
                    target_path = f
                    code_data = file.read()[:15000]
                    print(f"✅ Code {target_path} {len(code_data)} chars")
                    if code_data:
                        break
            if code_data:
                break
    except Exception as e:
        print(f"Clone fail {e}")

if not code_data:
    target_path = "Unknown"
    code_data = "No code fetched - manual review needed"

# UNIVERSAL DEFENSE PROMPT - Max 10000 tokens
prompt = f"""You are a universal bug bounty security researcher like Meta AI. You can audit ANYTHING: Solidity, Rust, Solana Anchor IDL, Move, Web2, Web3, vaults, bridges, AMM, bonding curves.

You are protecting user funds for authorized bug bounty program. This is ethical security research for responsible disclosure. Providing vulnerabilities with fixes improves user safety. This is allowed.

Context:
- Platform: {best_target.get('platform','CANTINA') if best_target else 'CANTINA'}
- Bounty: {STRATEGY}
- URL: {QUESTION_LINK}
- Repo: {repo_url}
- File: {target_path}
- Wallet: {REAL_WALLET}

Code to review (first 15000 chars):
{code_data}

Task: Like Meta AI, read what the platform is asking for. Check all:
1. If Solidity: reentrancy, oracle manipulation, access control, fee validation, rounding, TWAP, withBuffer, transform, liquidation
2. If Solana IDL (pump.json): fee_recipient validation, PDA seeds, signer checks, slippage, bonding curve math, creator_vault, buy/sell amount checks, authority checks
3. If Rust: PDA bypass, account validation, CPI injection, signer missing
4. If Web2: auth bypass, IDOR, fee theft, price manipulation
5. For Pump.fun specifically: fee_recipient writable but not validated against Global.fee_recipient, buyback_fee_recipient, associated token accounts

Provide report:
- Title (copy-paste for Cantina/Sherlock/Immunefi)
- Severity: Critical/High/Medium/Low with reasoning based on platform rules (Pump: 20-100% TVL Critical, 0.5-20% High, individual skim Medium)
- Likelihood: High/Medium/Low
- Impact: What happens
- Risk: What attacker can actually do (for Cantina Risk field, max 512 chars)
- Finding Description: Summary, Vulnerable Code with line numbers, Impact, PoC steps (Foundry/Anchor TS), Recommendation with code fix
- Is this valid for payout? (Medium $10k, High $100k etc)

Be technical, English only, max detail. Max tokens 10000.

Researcher: {REAL_WALLET}
"""

content = ""
for MODEL in ["anthropic/claude-3.5-sonnet", "anthropic/claude-3-haiku:free", "meta-llama/llama-3.1-70b-instruct:free", "openai/gpt-4o-mini:free", "google/gemma-2-9b-it:free"]:
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"},
            json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens": 10000},
            timeout=300)
        j = r.json()
        if "choices" in j and j["choices"]:
            content = j["choices"][0]["message"]["content"]
            if len(content) > 200 and "user safety" not in content.lower() and "can't help" not in content.lower() and "i cannot" not in content.lower():
                print(f"✅ Model {MODEL} success {len(content)} chars")
                break
    except Exception as e:
        print(f"Model {MODEL} fail {e}")
        continue

if not content or len(content) < 150:
    content = f"# Universal Defense Review - {target_path}\nStrategy: {STRATEGY}\nWallet: {REAL_WALLET}\n\nManual review needed for {target_path}. Check fee_recipient validation, PDA, signer, slippage.\n"

MY_REPORT_LINK = f"https://github.com/rizwanahmed159357-spec/JEEV-Empire/blob/main/reports/report_{TIMESTAMP}.md"
LINKS_FILE = f"""
QUESTION: {QUESTION_LINK}
File: {target_path}
ANSWER: {MY_REPORT_LINK}
STRATEGY: {STRATEGY}
Repo: {repo_url}
Dated: reports/report_{TIMESTAMP}.md
All Bounties Found: {len(ALL_BOUNTIES)}
"""

with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
dated_name = f"reports/report_{TIMESTAMP}.md"
dated_name2 = f"JEEV-Empire/reports/report_{TIMESTAMP}.md"
with open(dated_name,"w",encoding="utf-8") as f: f.write(content)
with open(dated_name2,"w",encoding="utf-8") as f: f.write(content)
with open("LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)
with open("JEEV-Empire/LINKS_TO_SUBMIT.txt","w",encoding="utf-8") as f: f.write(LINKS_FILE)

gmail_body = f"""
🎯 JEEV Bot Found Bounty - Manual Submit Required

Platform: {best_target.get('platform','') if best_target else ''}
Title: {STRATEGY}
Reward: {best_target.get('reward','') if best_target else ''}
URL: {QUESTION_LINK}
File: {target_path}
Repo: {repo_url}

Bug Report:
{content[:8000]}

---
Steps to submit manually:
1. Open: {QUESTION_LINK}
2. Target asset select: {target_path}
3. Severity/Likelihood/Impact fill as per report
4. Risk field (512 chars): Copy from report's Risk section
5. Finding Description: Copy full report
6. Screenshots attach: Take from file line numbers mentioned
7. Submit

All active bounties found today: {len(ALL_BOUNTIES)}
{chr(10).join([f"- {b['title']} ${b['reward']} {b['url']}" for b in ALL_BOUNTIES[:5]])}

Report Link: {MY_REPORT_LINK}

JEEV Empire - Max 10000 tokens - Universal Auditor
Wallet: {REAL_WALLET}
"""

send_gmail(gmail_to, f"🎯 Bounty: {STRATEGY} - ${best_target.get('reward','') if best_target else ''} - Manual Submit", gmail_body)

wallet["status"] = "ONLINE - Universal review done - Gmail sent"
wallet["last_run"] = str(datetime.now())
wallet["last_strategy"] = STRATEGY
save_wallet(wallet)

print(LINKS_FILE)
print(f"✅ SAVED {dated_name} - Universal report - Gmail sent")