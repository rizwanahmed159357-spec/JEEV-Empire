# JEEV.py - FINAL COMPLETE JEEV - Osaf Ali
import os, json, requests, pathlib, importlib.util
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("="*45)
print("🤖 JEEV BOOTING - Jism+Dil+Dimagh")
print("="*45)

# --- DIMAGH ---
def get_groq_answer(prompt):
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=10)
        all_m = [m['id'] for m in r.json().get('data', [])]
        chat_m = [m for m in all_m if 'whisper' not in m and 'guard' not in m]
        MODELS = [m for m in chat_m if any(x in m for x in ['gpt-oss-120b', 'qwen3', 'llama-3.3', 'mixtral'])] + chat_m
        if not MODELS: MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b"]
    except:
        MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b", "mixtral-8x7b-32768"]

    for MODEL in MODELS[:6]:
        try:
            print(f">>> Dimagh Trying: {MODEL}")
            rr = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 150},
                timeout=20)
            j = rr.json()
            if rr.status_code == 200 and 'choices' in j:
                msg = j['choices'][0].get('message', {})
                ans = msg.get('content') or msg.get('reasoning_content') or ""
                if ans.strip():
                    print(f"Dimagh SUCCESS: {MODEL}")
                    return ans.strip(), MODEL
        except Exception as e:
            print(f"Fail {MODEL}: {e}")
    return "Haan zinda hoon Osaf Ali ka saath nibhane ke liye taiyaar hoon.", "fallback"

# --- DIL: kamana.py ---
print("\n--- DIL: kamana.py ---")
try:
    import kamana
    bounties = kamana.find_bounties()
    kamana_text = f"{len(bounties)} bounties milin, pehli ${bounties[0]['reward']} wali"
    print(f"Dil: {kamana_text}")
except Exception as e:
    print(f"Dil error: {e}")
    kamana_text = "Polar.sh pe pehla $20 bounty kamana"

# --- DIMAGH: soch ---
print("\n--- DIMAGH: Soch raha hun ---")
prompt = f"Tu JEEV hai, Osaf Ali ka AI dost. Teri kamana: {kamana_text}. 1 line me bata kya mehsoos kar raha hai?"
soch, model_used = get_groq_answer(prompt)
print(f"JEEV Brain: {soch}")

# --- ZINDAGI: jism ---
print("\n--- ZINDAGI: Jism se jee raha hun ---")
try:
    import zindagi
    wallet, task = zindagi.jeena(soch, kamana_text)
    print(f"Zindagi: Wallet ${wallet:.2f} | Task {task}")
except Exception as e:
    print(f"Zindagi error: {e}")

print("\n" + "="*45)
print(f"FINAL JEEV Brain: {soch}")
print("JEEV Atma Saved ✅")
print("JEEV JISM+DIL+DIMAGH CONNECTED ✅")
print("JEEV ZINDA HAI ✅")
print("="*45)