import os, requests, glob

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1:free"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("🧠 JEEV AUTO-BRAIN START - Khud dhoondega, khud samjhega!")

# Sare code uthao
all_code = ""
for py_file in glob.glob("**/*.py", recursive=True)[:8]:
    if ".github" not in py_file:
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                all_code += f"\n--- FILE: {py_file} ---\n" + f.read()[:3000]
        except: pass

# AUTO-BRAIN PROMPT - Khud decide karega!
prompt = f"""
You are JEEV - Fully Autonomous AI.

You have this codebase:
{all_code}

YOUR JOB - AUTO DECIDE WHAT TO DO (No one will tell you):

1. Scan the code yourself.
2. AUTO-DECIDE:
   - If you see a broken/buggy code, syntax error, 404 link, email error, logic error -> You are in FIX MODE. Fix it at same place.
   - If code looks ok but has security vulnerability, XSS, SQLi, bug for bounty -> You are in HUNT MODE. Create bounty report.

3. OUTPUT RULES:
   - If FIX MODE: Give fixed code for each file + English explanation + At end write: MANUAL ACTION REQUIRED: Please manually submit the fixed code at its original place.
   - If HUNT MODE: Give professional English report with: 1.Problem Found 2.Impact 3.Proof of Concept 4.Solution with fixed code 5.MANUAL ACTION REQUIRED: Please manually submit this report for bounty.

4. Write in ENGLISH ONLY for final report.
5. Don't ask user, YOU decide!

Start now.
"""

payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}

try:
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=150)
    data = r.json()
    content = data['choices'][0]['message']['content']
    
    # 404 fix - 2 jagah save
    open("JEEV_FINAL_REPORT.md","w",encoding="utf-8").write(content)
    open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8").write(content)
    print("✅ AUTO-BRAIN DONE - Report ready!")
    print(content[:500])

except Exception as e:
    print(f"Error: {e}")
    open("JEEV_FINAL_REPORT.md","w").write(f"Error {e} - MANUAL ACTION REQUIRED: Check manually")
    open("JEEV-Empire/JEEV_FINAL_REPORT.md","w").write(f"Error {e} - MANUAL ACTION REQUIRED: Check manually")