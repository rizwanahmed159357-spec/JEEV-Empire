# JEEV.py - AUTO MODEL FINDER - FINAL
import os, json, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("JEEV Dimagh ON - Groq se soch raha hu...")

if not GROQ_API_KEY:
    print("GROQ_API_KEY nahi mili!")
    exit(0)

# Pehle Groq se pucho kaunse models available hain
try:
    r = requests.get("https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=15)
    data = r.json()
    print(f"Available models list status: {r.status_code}")
    if r.status_code == 200:
        available = [m['id'] for m in data.get('data', [])][:5]
        print(f"Groq pe available models: {available}")
        # Pehla available model use karo
        MODEL = available[0] if available else "mixtral-8x7b-32768"
    else:
        print(f"Model list nahi mili: {data}")
        MODEL = "mixtral-8x7b-32768"
except Exception as e:
    print(f"Model list error: {e}")
    MODEL = "mixtral-8x7b-32768"

print(f"Using model: {MODEL}")

# Ab chat karo
try:
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": "Tu JEEV hai, Osaf Ali ka dost, 1 line me bolo zinda ho"}],
            "max_tokens": 80
        },
        timeout=25)
    j = r.json()
    print(f"Groq Status: {r.status_code}")
    print(f"Groq Reply: {j}")
    
    if r.status_code == 200 and 'choices' in j:
        ans = j['choices'][0]['message']['content']
        print(f"JEEV Brain: {ans}")
    else:
        print(f"JEEV Brain Error: {j}")
        ans = str(j)
except Exception as e:
    print(f"JEEV Brain: Dimagh error: {e}")
    ans = str(e)

with open("jeev_atma.json", "w") as f:
    json.dump({"last_thought": ans, "owner": "Osaf Ali"}, f)

print("JEEV ZINDA HAI ✅")