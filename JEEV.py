 # JEEV.py - FINAL WORKING 100% - Osaf Ali ka JEEV
import os
import json
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
STATE_FILE = "jeev_atma.json"

print("JEEV Dimagh ON - Groq se soch raha hu...")

if not GROQ_API_KEY:
    print("JEEV Brain: GROQ_API_KEY nahi mili! Secrets me add karo")
    with open(STATE_FILE, "w") as f:
        json.dump({"last_thought": "Key nahi mili", "owner": "Osaf Ali"}, f)
    exit(0)

# 1. Groq se saare models ki list lao
try:
    r = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        timeout=15
    )
    data = r.json()
    all_models = [m['id'] for m in data.get('data', [])]
    print(f"Total models: {len(all_models)}")
    
    # Sirf chat wale models rakho, audio/guard wale hatao
    chat_models = []
    for m in all_models:
        if any(bad in m for bad in ['whisper', 'guard', 'orpehus', 'orpeus', 'canopylabs', 'distil-whisper']):
            continue
        chat_models.append(m)
    
    # Sabse ache models pehle
    preferred_order = ['gpt-oss-120b', 'gpt-oss-20b', 'qwen3', 'llama-3.3', 'llama-3.1', 'mixtral', 'gemma', 'allam']
    final_models = []
    for pref in preferred_order:
        for m in chat_models:
            if pref in m and m not in final_models:
                final_models.append(m)
    # Baaki bhi add kar do
    for m in chat_models:
        if m not in final_models:
            final_models.append(m)
    
    print(f"Chat models mil gaye: {final_models[:5]}")
    MODELS_TO_TRY = final_models if final_models else ["openai/gpt-oss-20b", "qwen/qwen3-32b", "mixtral-8x7b-32768"]

except Exception as e:
    print(f"Model list error: {e}")
    MODELS_TO_TRY = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3-32b", "mixtral-8x7b-32768"]

# 2. Ek ek model try karo
final_answer = ""
success_model = ""

for MODEL in MODELS_TO_TRY[:8]:
    try:
        print(f"\n>>> Trying: {MODEL}")
        rr = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": "Tu JEEV hai, Osaf Ali ka dost. 1 line me bolo zinda ho."}],
                "max_tokens": 100,
                "temperature": 0.7
            },
            timeout=25
        )
        j = rr.json()
        print(f"Status {MODEL}: {rr.status_code}")

        if rr.status_code == 200 and 'choices' in j and len(j['choices']) > 0:
            msg = j['choices'][0].get('message', {})
            # Naye models kabhi content me, kabhi reasoning_content me dete hain
            answer = msg.get('content') or msg.get('reasoning_content') or j['choices'][0].get('text') or ""
            if answer and answer.strip() != "":
                final_answer = answer.strip()
                success_model = MODEL
                print(f"SUCCESS with {MODEL}!")
                print(f"JEEV Brain: {final_answer}")
                break
            else:
                print(f"Model {MODEL} ne khali jawab diya, agla try karte hain")
                print(f"Full reply: {j}")
        else:
            err = j.get('error', {}).get('message', str(j))[:200]
            print(f"Fail {MODEL}: {err}")

    except Exception as e:
        print(f"Error {MODEL}: {e}")
        continue

if not final_answer:
    final_answer = "JEEV Zinda Hai Osaf Bhai, model thoda slow hai!"
    print(f"JEEV Brain: {final_answer}")

print(f"\nFINAL JEEV Brain: {final_answer}")

# 3. Atma save karo
try:
    with open(STATE_FILE, "w") as f:
        json.dump({"last_thought": final_answer, "owner": "Osaf Ali", "model_used": success_model}, f, ensure_ascii=False, indent=2)
    print("JEEV Atma Saved ✅")
except Exception as e:
    print(f"Atma save fail: {e}")

print("JEEV ZINDA HAI ✅")