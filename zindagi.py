import os
import requests
import glob
import json

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY nahi mili! Pehle GitHub Secrets me set karo.")
    exit(1)

# 2026 ke active free models pipeline
MODELS = [
    "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-chat-v3-0324:free"
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/JEEV-Empire",
    "X-Title": "JEEV-Empire"
}

print("🧠 JEEV AUTO-BRAIN V3 - 2026 Hacking Engine Active")

# --- SIMULATION OF WORLD'S HARDEST BUG PROGRAM ---
hardest_problem_simulation = """
# --- FILE: financial_core/vault_oracle.py ---
# PRIVILEGED LIQUIDITY POOL & DYNAMIC PRICING ENGINE

class LiquidityVaultBridge:
    def __init__(self, token_balances, external_oracle):
        self.balances = token_balances
        self.oracle = external_oracle
        self.is_locked = False

    def withdraw_and_sync_yield(self, user, amount):
        # ⚠️ CRITICAL MEGA-VALUABLE EXPLOIT FOUND HERE:
        # Cross-Contract Reentrancy combined with Spot Price Manipulation Flaw.
        
        user_balance = self.balances.get(user, 0)
        if user_balance < amount:
            return False

        payment_status = self.oracle.trigger_external_transfer(user, amount)
        
        if payment_status:
            self.balances[user] -= amount
            current_pool_ratio = self.balances["token_a"] / self.balances["token_b"]
            self.oracle.update_spot_price_unsafe(current_pool_ratio)
            return True
            
        return False
"""

code_data = "\n--- File: financial_core/vault_oracle.py ---\n" + hardest_problem_simulation

files_found = 1
for f in glob.glob("**/*.py", recursive=True):
    if any(x in f for x in ["zindagi", ".github", "__pycache__"]) or "jeev" in f.lower():
        continue
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            txt = file.read()
            if len(txt) > 100:
                code_data += f"\n--- File: {f} ---\n{txt[:1500]}"
                files_found += 1
                if files_found >= 3: break
    except: pass

prompt = f"""
You are JEEV Security Expert. Meticulously analyze this target code architecture for severe logic bypasses, or high-value multi-million dollar exploit loops:
{code_data}

OPERATIONAL AUTOMATION RULES:
1. AUTO-DECIDE: If it's a routine syntax error, switch to FIX MODE. If it's a catastrophic economic/security vulnerability, switch to HUNT MODE.
2. Output structural format must be a highly technical professional English report containing:
   - Vulnerability Type & Execution Severity
   - Complete Threat Impact Analysis
   - Step-by-Step Proof of Concept (PoC) script logic
   - Corrected, secure remediation patch implementing industry standard security patterns.
3. Your absolute final output line MUST be exactly: MANUAL ACTION REQUIRED: Please submit manually to program.

Provide only the report in technical English language. Do not talk back or greet.
"""

content = None
last_err = None

for MODEL in MODELS:
    try:
        print(f"--> Trying: {MODEL}")
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": MODEL, 
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000
            },
            timeout=120)
        
        try:
            data = r.json()
        except Exception as json_err:
            last_err = f"Invalid JSON response structure: {json_err}"
            continue

        print(f"API says: {str(data)[:300]}")
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            print(f"✅ SUCCESS with {MODEL}")
            break
        else:
            err_msg = data.get("error", {}).get("message", "Pipeline structure failure")
            last_err = f"Model {MODEL} error response: {err_msg}"
    except Exception as e:
        print(f"Error executing model request: {e}")
        last_err = str(e)

if not content:
    content = f"""# JEEV SYSTEM AUDIT REPORT - API CHANNELS SATURATED

## Diagnostic Error State
{last_err}

## MANUAL ACTION REQUIRED
1. Verify OpenRouter API key permissions for external free endpoint tiers.
2. If OpenRouter restricts concurrent automated traffic, please allocate $5 to bypass request-per-minute limits.
"""

with open("JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
    f.write(content)

try:
    os.makedirs("JEEV-Empire", exist_ok=True)
    with open("JEEV-Empire/JEEV_FINAL_REPORT.md", "w", encoding="utf-8") as f:
        f.write(content)
except: pass
print("\n\n--- FINAL REPORT ---\n")
print(content)
print("\n--- END REPORT ---\n")
print("✅ PROCESS COMPLETE - Autonomous Report Compiled Successfully!")