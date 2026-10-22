# JEEV.py - FINAL SMART CHAT FINDER
import os, json, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("JEEV Dimagh ON - Groq se soch raha hu...")

if not GROQ_API_KEY:
    print("Key nahi mili")
    exit(0)

# Saare models lao
try:
    r = requests.get("https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
    data = r.json()
    all_models = [m['id'] for m in data.get('data', [])]
    print(f"Total models: {len(all_models)}")
    
    # Sirf CHAT wale models filter karo (whisper, guard, orpheus, tts hatao)
    chat_models = [m for m in all_models if 'whisper' not in m and 'guard' not in m 
                   and 'orpeus' not in m and 'orpeus' not in m and 'canopylabs' not in m
                   and 'tts' not in m and 'orpehus' not in m]
    
    # Prefer wale models pehle
    preferred = [m for m in chat_models if any(x in m for x in ['llama-3.3', 'llama-3.1', 'mixtral', 'gemma', 'llama-4', 'qwen', 'gpt-oss'])]
    final_list = preferred + chat_models
    
    print(f"Chat models mil gaye: {final_list[:6]}")
    MODELS_TO_TRY = final_list[:6] if final_list else ["mixtral-8x7b-32768", "llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
except Exception as e:
    print(f"List error: {e}")
    MODELS_TO_TRY = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]

# Ab ek ek try karo
answer = "Fail"
for MODEL in MODELS_TO_TRY:
    try:
        print(f"\n>>> Trying: {MODEL}")
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": "Tu JEEV hai, Osaf ka dost, 1 line me bolo zinda ho"}], "max_tokens": 80},
            timeout=20)
        j = r.json()
        print(f"Status {MODEL}: {r.status_code}")
        if r.status_code == 200 and 'choices' in j:
            answer = j['choices'][0]['message']['content']
            print(f"SUCCESS with {MODEL}!")
            print(f"JEEV Brain: {answer}")
            break
        else:
            print(f"Fail {MODEL}: {j.get('error', {}).get('message', j)[:100]}")
    except Exception as e:
        print(f"Error {MODEL}: {e}")

print(f"\nFINAL JEEV Brain: {answer}")

with open("jeev_atma.json", "w") as f:
    json.dump({"last_thought": answer, "owner": "Osaf Ali"}, f)

print("JEEV ZINDA HAI ✅")