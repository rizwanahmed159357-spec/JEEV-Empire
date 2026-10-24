import os
import requests
import glob
import json

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-r1:free"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

print("🧠 JEEV AUTO-BRAIN START - Khud dhoondega, khud samjhega!")

# --- SIMULATION OF A HIGH-LEVEL SAKHT PROBLEM ---
# Ye wo file hai jo dunya ki sakht tareen vulnerability simulate kr rhi hai
simulation_code = """
# --- FILE: server_admin/immunify_sync.py ---
# WARNING: HIGH-LEVEL PRIVILEGED CORE BACKEND COMPONENT

import os
import pickle
import base64

class ImmunifySyncManager:
    def __init__(self, request_data):
        self.request_data = request_data

    def process_admin_update(self):
        # HIGH-LEVEL VULNERABILITY HERE:
        # 1. Path Traversal flaw via unsanitized input
        # 2. Insecure Deserialization (Pickle) leading to Remote Code Execution (RCE)
        
        config_path = self.request_data.get("config_path")
        if not config_path:
            return {"status": "error", "msg": "No path provided"}
            
        # Dangerous Path Traversal: User can bypass directory restrictions using ../../
        full_path = os.path.join("/var/www/immunify/safe_dir/", config_path)
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                # CRITICAL BUG: Untrusted data is directly passed to pickle.loads()
                # An attacker can inject a malicious serialized Python object here
                raw_data = f.read()
                decrypted_data = base64.b64decode(raw_data)
                parsed_config = pickle.loads(decrypted_data) 
                return {"status": "success", "data": str(parsed_config)}
        return {"status": "error", "msg": "Path not found"}
"""

# Demo k liye hum is simulation code ko scan list mein shamil kr rhy hain
all_code = "\n--- FILE: server_admin/immunify_sync.py ---\n" + simulation_code

# Baki files uthao (agr koi mojood hain)
for py_file in glob.glob("**/*.py", recursive=True)[:8]:
    if ".github" not in py_file and "jeev" not in py_file.lower():
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                all_code += f"\n--- FILE: {py_file} ---\n" + f.read()[:3000]
        except: pass

# AUTO-BRAIN PROMPT - AI khud decide kry ga
prompt = f"""
You are JEEV - Fully Autonomous AI Security Agent & Code Fixer.

You have been deployed inside a high-security server environment. Here is the codebase:
{all_code}

YOUR JOB - AUTO DECIDE WHAT TO DO (No human intervention):

1. Scan the code meticulously. Look for deep logical bugs or high-impact architectural/security flaws.
2. AUTO-DECIDE:
   - FIX MODE: If you see basic syntax errors, broken logic, 404 links, or normal coding mistakes. Fix it immediately.
   - HUNT MODE: If you spot a critical security vulnerability (like RCE, SQL Injection, Insecure Deserialization, Path Traversal) that can be weaponized or reported for a Bug Bounty.

3. OUTPUT RULES:
   - If FIX MODE: Give fixed code for each file + English explanation + At end write: MANUAL ACTION REQUIRED: Please manually submit the fixed code at its original place.
   - If HUNT MODE: Give a professional English Bug Bounty Report containing: 
     1. Vulnerability Type
     2. Threat Impact (Explain how devastating it is)
     3. Proof of Concept (PoC) Exploit Code (Show how an attacker can execute arbitrary OS commands using pickle payload)
     4. Remediation / Fixed Code
     5. MANUAL ACTION REQUIRED: Please manually submit this report for bounty.

4. Write in ENGLISH ONLY.
5. Do not ask for permissions. You are the brain. Act now.
"""

payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}

try:
    # Timeout 150 tak rakha hai kyun k DeepSeek-R1 deep thinking krta hai
    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=150)
    data = r.json()
    content = data['choices'][0]['message']['content']
    
    # Reports save krna
    os.makedirs("JEEV-Empire", exist_ok=True)
    open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8").write(content)
    open("JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8").write(content)
    
    print("✅ AUTO-BRAIN DONE - Report ready!")
    print("\n--- FIRST 500 CHARACTERS OF REPORT ---")
    print(content[:700])

except Exception as e:
    print(f"Error: {e}")
    os.makedirs("JEEV-Empire", exist_ok=True)
    open("JEEV_FINAL_REPORT.md", "w").write(f"Error {e} - MANUAL ACTION REQUIRED: Check manually")
    open("JEEV-Empire/JEEV_FINAL_REPORT.md", "w").write(f"Error {e} - MANUAL ACTION REQUIRED: Check manually")
