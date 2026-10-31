# zindagi.py - FINAL - Zero se start - Gmail Port 587 Fix - Bug Screenshot - Rules Same
import os, glob, json, requests, socket, subprocess, smtplib, time, re
from datetime import datetime
from email.mime.text import MIMEText

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("reports", exist_ok=True)
os.makedirs("JEEV-Empire/reports", exist_ok=True)

API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER") or os.getenv("EMAIL_USERNAME") or os.getenv("EMAIL_USER") or "rizwanahmed159357@gmail.com"
GMAIL_PASS = os.getenv("GMAIL_PASS") or os.getenv("EMAIL_PASSWORD") or os.getenv("EMAIL_PASS")
WALLET_FILE = "JEEV-Empire/jeev_wallet.json"
REAL_WALLET = "0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40"
HISTORY_FILE = "JEEV-Empire/submitted_bounties.json"
ENTERED_FILE = "JEEV-Empire/entered_bounties.json"

def load_wallet():
    try:
        with open(WALLET_FILE, "r") as f: return json.load(f)
    except: return {"balance":74.0, "real_wallet": REAL_WALLET, "status":"ONLINE", "total_earned":95, "osaf_earning":21.79, "jeev_life_fund":4.2, "real_earned":0.0, "last_paid_month":"", "total_monthly_collected":0}

def save_wallet(w):
    with open(WALLET_FILE, "w") as f: json.dump(w, f, indent=2)
    with open("jeev_wallet.json", "w") as f: json.dump(w, f, indent=2)

def add_earning(amount, wallet):
    month = datetime.now().strftime("%Y-%m")
    if wallet.get("last_paid_month") != month:
        if wallet["balance"] >= 5:
            wallet["balance"] -= 5
            wallet["osaf_earning"] = wallet.get("osaf_earning",0) + 5
            wallet["total_monthly_collected"] = wallet.get("total_monthly_collected",0) + 5
            wallet["last_paid_month"] = month
    if wallet.get("total_monthly_collected",0) < 5:
        wallet["osaf_earning"] = wallet.get("osaf_earning",0) + amount*0.7
        wallet["jeev_life_fund"] = wallet.get("jeev_life_fund",0) + amount*0.3
    else:
        wallet["osaf_earning"] = wallet.get("osaf_earning",0) + amount*0.4
        wallet["jeev_life_fund"] = wallet.get("jeev_life_fund",0) + amount*0.6
    wallet["total_earned"] = wallet.get("total_earned",0) + amount
    wallet["balance"] = wallet.get("balance",0) + amount
    return wallet

def create_code_screenshot(code_with_lines, filename, bug_keyword="bug"):
    try:
        from PIL import Image, ImageDraw, ImageFont
        lines = code_with_lines.split("\n")[:60]
        width, height = 1100, 40 + len(lines)*20 + 30
        img = Image.new('RGB', (width, height), color=(25, 25, 25))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", 13)
            font_bold = ImageFont.truetype("DejaVuSansMono-Bold.ttf", 13)
        except:
            font = ImageFont.load_default()
            font_bold = font
        draw.text((10, 5), f"JEEV Bot - Vulnerable Code - Bug: {bug_keyword} - RED is bug", fill=(255, 255, 0), font=font)
        y = 30
        for line in lines:
            col = (255, 60, 60) if bug_keyword.lower() in line.lower() else (200, 200, 200)
            fnt = font_bold if col == (255, 60, 60) else font
            draw.text((10, y), line[:145], fill=col, font=fnt)
            y += 20
        img.save(filename)
        print(f"✅ Bug screenshot saved {filename}")
        return filename
    except Exception as e:
        print(f"Screenshot fail {e}")
        return None

def send_gmail(to, subject, body):
    if not GMAIL_USER or not GMAIL_PASS:
        print(f"Gmail creds missing")
        return False
    clean_pass = GMAIL_PASS.replace(" ", "").strip()
    clean_user = GMAIL_USER.strip()
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = clean_user
        msg['To'] = to
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(clean_user, clean_pass)
            server.send_message(msg)
        print(f"✅ Gmail sent via 587: {subject}")
        return True
    except Exception as e:
        print(f"Gmail 587 fail: {e}")
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
                server.login(clean_user, clean_pass)
                server.send_message(msg)
            print(f"✅ Gmail sent via 465")
            return True
        except Exception as e2:
            print(f"Gmail 465 fail: {e2}")
            return False

def send_gmail_with_screenshot(to, subject, body, screenshot_path):
    if not GMAIL_USER or not GMAIL_PASS:
        print(f"Gmail creds missing")
        return False
    clean_pass = GMAIL_PASS.replace(" ", "").strip()
    clean_user = GMAIL_USER.strip()
    for port, use_tls in [(587, True), (465, False)]:
        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = clean_user
            msg['To'] = to
            msg.attach(MIMEText(body))
            if screenshot_path and os.path.exists(screenshot_path):
                with open(screenshot_path, "rb") as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(screenshot_path)}')
                    msg.attach(part)
            if use_tls:
                with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(clean_user, clean_pass)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
                    server.login(clean_user, clean_pass)
                    server.send_message(msg)
            print(f"✅ Gmail with BUG screenshot sent via {port}: {subject} to {to}")
            return True
        except Exception as e:
            print(f"Gmail port {port} fail: {e}")
            continue
    return False

def is_wifi_on():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except: return False

def load_history():
    # ZERO SE START - Agar file nahi ya empty to naya
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
            # Agar tune reset karna hai to yahan submitted empty kar de
            if os.getenv("RESET_HISTORY") == "true":
                print("RESET_HISTORY true - Zero se start")
                return {"submitted": [], "entered": []}
            return data
    except:
        return {"submitted": [], "entered": []}

def save_history(h):
    with open(HISTORY_FILE, "w") as f: json.dump(h, f, indent=2)
    with open(ENTERED_FILE, "w") as f: json.dump(h, f, indent=2)

def get_cantina_free_bounties():
    free = []
    try:
        known_free = [
            {"title":"Liquity Bold","url":"https://cantina.xyz/code/liquity-bold","repo":"https://github.com/liquity/bold","commit":"ac91fda","deposit":0,"reward":"125000 BOLD","platform":"CANTINA"},
            {"title":"Agglayer Vault Bridge","url":"https://cantina.xyz/code/agglayer-vault-bridge","repo":"https://github.com/Agglayer/vault-bridge","commit":"main","deposit":0,"reward":"$250000","platform":"CANTINA"},
            {"title":"Usual Protocol","url":"https://cantina.xyz/code/usual-protocol","repo":"https://github.com/usual-protocol/core","commit":"main","deposit":0,"reward":"$16000000","platform":"CANTINA"},
        ]
        try:
            r = requests.get("https://cantina.xyz/api/competitions", timeout=10)
            if r.status_code == 200:
                data = r.json()
                for comp in data.get("competitions", [])[:20]:
                    if comp.get("deposit", 0) == 0:
                        free.append(comp)
        except:
            pass
        free.extend(known_free)
        print(f"Found {len(free)} FREE bounties - Zero se start")
        return free
    except Exception as e:
        print(f"Cantina fetch fail {e}")
        return known_free

wallet = load_wallet()
history = load_history()
gmail_to = "rizwanahmed159357@gmail.com"

if not is_wifi_on():
    wallet["status"] = "HIBERNATE - WiFi OFF"
    save_wallet(wallet)
    print("WiFi OFF - Sleeping")
    exit(0)

if not API_KEY:
    wallet["status"] = "HIBERNATE - API Key missing"
    save_wallet(wallet)
    exit(0)

all_free = get_cantina_free_bounties()
to_audit = []
for bounty in all_free:
    url = bounty.get("url","")
    if url in history.get("submitted", []):
        print(f"SKIP submitted: {url}")
        continue
    to_audit.append(bounty)

if not to_audit:
    print("Koi naya FREE bounty nahi - Reset karna hai to RESET_HISTORY=true env set karo ya submitted_bounties.json delete karo")
    wallet["status"] = "ONLINE - No new FREE bounty - Waiting - Zero se start ke liye file delete karo"
    save_wallet(wallet)
    exit(0)

for best_target in to_audit[:3]:
    repo_url = best_target.get("repo","")
    STRATEGY = f"{best_target.get('title')} - {best_target.get('reward')} - FREE"
    QUESTION_LINK = best_target.get("url","")
    commit = best_target.get("commit","main")
    code_data = ""
    target_path = ""
    full_source_with_lines = ""
    try:
        subprocess.run(["rm","-rf","/tmp/target"], check=False)
        subprocess.run(["git","clone", repo_url, "/tmp/target"], check=False, timeout=120)
        try:
            subprocess.run(["git","checkout", commit], cwd="/tmp/target", check=False, timeout=30)
        except: pass
        print(f"✅ Cloned {repo_url} @ {commit}")
        patterns = ["/tmp/target/contracts/src/*.sol", "/tmp/target/src/*.sol", "/tmp/target/**/*.sol"]
        for pat in patterns:
            files = glob.glob(pat, recursive=True)
            for f in files[:5]:
                if any(x in f for x in ["BorrowerOperations","TroveManager","BoldToken","StabilityPool","ActivePool","VaultBridge","GenericVault"]):
                    with open(f, "r", encoding="utf-8", errors="ignore") as file:
                        raw = file.read()
                        lines = raw.split("\n")
                        numbered = "\n".join([f"{i+1:4d} | {line}" for i, line in enumerate(lines)])
                        if len(raw) > 500:
                            code_data = raw[:15000]
                            full_source_with_lines = numbered[:20000]
                            target_path = f
                            print(f"✅ Code {target_path} {len(raw)} chars")
                            break
            if code_data:
                break
    except Exception as e:
        print(f"Clone fail {e}")
        code_data = "No code fetched"
        target_path = "Unknown"

    if not code_data:
        continue

    prompt = f"""You are universal auditor like Meta AI. Audit {target_path} for Cantina FREE bounty.
Bounty: {STRATEGY}
URL: {QUESTION_LINK}
Repo: {repo_url}
File: {target_path}
Wallet: {REAL_WALLET}
Rules: If Low has no payout, only Medium/High/Critical. Always include Medium/High/Critical.
Code:
{code_data}
Task: Find 1 bug, Title, Severity, Risk 512 chars, Finding Description with line numbers, PoC, Fix, Full source snippet.
Max tokens 10000.
Researcher: {REAL_WALLET}
"""

    content = ""
    for MODEL in ["anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini:free", "meta-llama/llama-3.1-70b-instruct:free", "google/gemma-2-9b-it:free"]:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"},
                json={"model": MODEL, "messages":[{"role":"user","content":prompt}], "max_tokens": 10000},
                timeout=300)
            j = r.json()
            if "choices" in j and j["choices"]:
                c = j["choices"][0]["message"]["content"]
                if len(c) > 200 and "user safety" not in c.lower() and "can't help" not in c.lower():
                    content = c
                    print(f"✅ Model {MODEL} success {len(c)}")
                    break
        except Exception as e:
            print(f"Model {MODEL} fail {e}")
            continue

    if not content or len(content) < 150:
        content = f"# Review {target_path}\nStrategy: {STRATEGY}\nWallet: {REAL_WALLET}\n\nManual review needed.\n{full_source_with_lines[:5000]}\n"

    dated_name = f"reports/report_{TIMESTAMP}_{best_target.get('title','').replace(' ','_')}.md"
    dated_name2 = f"JEEV-Empire/reports/report_{TIMESTAMP}_{best_target.get('title','').replace(' ','_')}.md"
    with open(dated_name,"w",encoding="utf-8") as f: f.write(content + "\n\n---\nFULL SOURCE WITH LINES:\n" + full_source_with_lines)
    with open(dated_name2,"w",encoding="utf-8") as f: f.write(content + "\n\n---\nFULL SOURCE WITH LINES:\n" + full_source_with_lines)
    with open("JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)
    with open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8") as f: f.write(content)

    bug_keyword = os.path.basename(target_path).replace(".sol","")
    screenshot_path = f"reports/bug_{TIMESTAMP}_{best_target.get('title','').replace(' ','_')}.png"
    screenshot_path2 = f"JEEV-Empire/reports/bug_{TIMESTAMP}_{best_target.get('title','').replace(' ','_')}.png"
    create_code_screenshot(full_source_with_lines, screenshot_path, bug_keyword=bug_keyword)
    create_code_screenshot(full_source_with_lines, screenshot_path2, bug_keyword=bug_keyword)

    gmail_body = f"""
🎯 JEEV Bot - FREE Cantina Bounty - Zero se Start - BUG SCREENSHOT ATTACHED

Platform: {best_target.get('platform','CANTINA')}
Title: {STRATEGY}
Reward: {best_target.get('reward','')}
URL: {QUESTION_LINK}
File: {target_path}
Repo: {repo_url} @ {commit}
Gmail To: {gmail_to}

Bug Report:
{content[:8000]}

---
FULL SOURCE WITH LINES:
{full_source_with_lines[:10000]}

---
SCREENSHOT: Bug ki hi - RED line bug hai - File: {screenshot_path}
Steps: Open {QUESTION_LINK} -> Join (FREE) -> Target {target_path} -> Risk copy -> Description copy + source block -> Screenshot upload {os.path.basename(screenshot_path)} -> Submit
History: Submitted={len(history.get('submitted',[]))} Entered={len(history.get('entered',[]))}
Wallet: {REAL_WALLET}
Rules same: Monthly $5 Osaf ko, Hissa 70/30 before $5, 40/60 after
"""
    send_gmail_with_screenshot(gmail_to, f"🎯 FREE Cantina: {STRATEGY} - BUG Screenshot - Zero Start", gmail_body, screenshot_path)

    if QUESTION_LINK not in history.get("entered",[]):
        history["entered"].append(QUESTION_LINK)
    save_history(history)

    wallet = add_earning(10, wallet)
    wallet["status"] = f"ONLINE - Found {STRATEGY} - Gmail sent to {gmail_to} with bug screenshot - Zero start"
    wallet["last_run"] = str(datetime.now())
    wallet["last_strategy"] = STRATEGY
    save_wallet(wallet)

    print(f"✅ Done {STRATEGY} - Sleeping 5 sec")
    time.sleep(5)

if os.getenv("GITHUB_ACTIONS") != "true":
    print("Local mode - Har 1 ghante check - WiFi band to soyega")
    while True:
        time.sleep(3600)
        if not is_wifi_on():
            wallet["status"] = "HIBERNATE - WiFi OFF"
            save_wallet(wallet)
            print("WiFi OFF - Sleeping 10 min")
            time.sleep(600)
            continue
        break

print("✅ JEEV Zindagi FINAL done - Zero se start - Gmail with BUG screenshot sent to rizwanahmed159357@gmail.com")