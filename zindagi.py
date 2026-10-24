import os
import requests
import glob
import json

# Key GitHub Secret se ayegi
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY nahi mili GitHub Secrets me!")
    exit(1)

# MODELS LIST - Priority Wise
MODELS = [
    "deepseek/deepseek-r1:free",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free"
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/JEEV-Empire",
    "X-Title": "JEEV-Empire"
}

print("🧠 JEEV AUTO-BRAIN START - Advanced Security Scanning Engine")

# --- DUNYA KI SAB SE MUSHKIL PROBLEM SIMULATION ---
# Yeh core logic memory corruption aur logical bypass ka combination hai
hardest_problem_simulation = """
# --- FILE: core/security_kernel.py ---
# SYSTEM ROOT PRIVILEGE LOGICAL KERNEL CONNECTOR

import ctypes
import struct

class AdvancedKernelBridge:
    def __init__(self, raw_buffer):
        self.buffer = raw_buffer  # User-controlled raw network packet bytes

    def process_system_packet(self):
        # ⚠️ CRITICAL WORLD-CLASS ZERO-DAY FLAW:
        # 1. Integer Underflow leads to Heap Buffer Overflow via ctypes manipulation.
        # 2. Arbitrary Memory Write (Write-What-Where primitive) via unsanitized header length.
        
        if len(self.buffer) < 8:
            return False
            
        # Packet format: [2-bytes Magic] [2-bytes Type] [4-bytes Length Indicator]
        magic, p_type, length_indicator = struct.unpack("<HHI", self.buffer[:8])
        
        if magic != 0x4A45: # 'JE'
            return False
            
        # HIGH LEVEL INTEGER UNDERFLOW Bypassing Boundary Check:
        # Attacker sends length_indicator = 4. 
        # 4 - 8 results in an underflow/negative wrapping in low-level memory calculation, 
        # bypassing the size restriction check but allocated as a huge unsigned integer!
        calculated_size = length_indicator - 8
        
        if calculated_size > 4096: # Logical check boundary
            return False
            
        # Memory Corruption Primitive
        # Creating a dynamic mutable buffer based on the underflowed size
        mem_allocation = (ctypes.c_char * calculated_size)()
        
        # This memmove executes an Out-of-Bounds Write directly into the process heap memory,
        # allowing an attacker to overwrite function pointers and execute arbitrary kernel payloads!
        ctypes.memmove(mem_allocation, self.buffer[8:], len(self.buffer) - 8)
        return True
"""

# Dynamic scanning simulation
code_data = "\n--- File: core/security_kernel.py ---\n" + hardest_problem_simulation

# Baki standard project files uthao (Max 2 mazeed)
files_found = 1
for f in glob.glob("**/*.py", recursive=True):
    if "zindagi" in f or ".github" in f or "__pycache__" in f or "jeev" in f.lower():
        continue
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            txt = file.read()
            if len(txt) > 100:
                code_data += f"\n--- File: {f} ---\n{txt[:2000]}"
                files_found += 1
                if files_found >= 3: break
    except:
        pass

# STRICT AGENT PROMPT - AI ko majboor karega HUNT ya FIX decide karne par
prompt = f"""
You are JEEV - An Elite Autonomous Cyber Security AI Core Operating Globally.

CRITICAL CODEBASE FOR AUDIT:
{code_data}

OPERATIONAL MANDATE (YOU MUST AUTO-DECIDE INTENT):
1. Deeply analyze the code architecture for elite architectural flaws, logic bypasses, or low-level memory vulnerabilities (like Integer Underflows, Heap Corruption, RCE).
2. AUTO-DECIDE YOUR MODE:
   - FIX MODE: Activate ONLY if the bugs are trivial, syntax-based, or non-exploitable logic mistakes.
   - HUNT MODE: Activate MANDATORILY if you discover high-impact vulnerabilities capable of full machine/process takeover (Bug Bounty Target).

OUTPUT STRUCTURAL RULES:
- IF FIX MODE: Provide the patched secure code + Technical analysis + End exactly with: MANUAL ACTION REQUIRED: Please submit manually to program.
- IF HUNT MODE: Generate a world-class cryptographic/exploit bug bounty report containing:
  1. Executive Summary & Flaw Classification (e.g., Integer Underflow to Out-of-Bounds Write)
  2. Attack Vector & Deep Technical Impact
  3. Mathematical Proof of Concept (PoC) illustrating buffer corruption calculation
  4. Complete Remediation (The fully refactored secure Python/ctypes code)
  5. The exact final line: MANUAL ACTION REQUIRED: Please submit manually to program.

Strictly write the response in ENGLISH ONLY. No conversational greetings or filler text.
"""

content = None
last_error = None

for MODEL in MODELS:
    try:
        print(f"--> Trying MODEL: {MODEL}")
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000
        }
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=120)
        
        if r.status_code != 200:
            print(f"❌ {MODEL} HTTP Error: {r.status_code}")
            last_error = f"HTTP {r.status_code}: {r.text}"
            continue
            
        data = r.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            print(f"✅ SUCCESS with {MODEL}")
            break
        else:
            print(f"❌ {MODEL} FAILED - Bad response structure")
            last_error = json.dumps(data)
            continue
            
    except Exception as e:
        print(f"❌ Exception with {MODEL}: {e}")
        last_error = str(e)
        continue

# Fallback Report Generation
if not content:
    content = f"""# JEEV AUTO-REPORT - API PIPELINE FAILED

All models exhausted without success. 

## Technical Error State
{last_error}

## MANUAL ACTION REQUIRED
1. Verify OpenRouter Account Balance & Credits.
2. Ensure the API key has access permissions for deepseek-r1.
3. Review target codebase manually.
"""

# Reports ko safe directories me save krna
os.makedirs("JEEV-Empire", exist_ok=True)

with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)

with open("JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ DONE - Autonomous Report successfully compiled!")
if content:
    print("\n--- REPORT PREVIEW ---")
    print(content[:600])
