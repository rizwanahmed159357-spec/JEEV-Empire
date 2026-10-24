import os, requests, glob
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1:free"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
desc = ""
if os.path.exists("DESCRIPTION.md"):
    with open("DESCRIPTION.md", "r", encoding="utf-8", errors="ignore") as f:
        desc = f.read()
if not desc:
    desc = "Find bug for bounty and give solution in English"
print(f"Task: {desc[:200]}")
code = ""
for py_file in glob.glob("**/*.py", recursive=True)[:5]:
    if "zindagi.py" not in py_file:
        try:
            with open(py_file, "r", errors="ignore") as f:
                code += f.read()[:2000]
        except: pass
prompt = f"TASK: {desc}\nCODE: {code}\n\nIf task says fix/sahi kro then FIX code and say MANUAL ACTION REQUIRED: Please manually submit fixed code. If task says find bug/bounty/bug dhondo then make English report with: 1.Problem Found 2.Impact 3.Solution with code 4.MANUAL ACTION REQUIRED: Please manually submit report. Write in ENGLISH ONLY."
payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=120)
data = r.json()
content = data['choices'][0]['message']['content']
open("JEEV_FINAL_REPORT.md","w",encoding="utf-8").write(content)
open("JEEV-Empire/JEEV_FINAL_REPORT.md","w",encoding="utf-8").write(content)
print("Done!")