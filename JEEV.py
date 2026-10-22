# JEEV.py - FINAL FIXED with Groq Brain + Resume Power
import os, json, requests

STATE_FILE = "jeev_atma.json"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_answer(prompt):
    if not GROQ_API_KEY:
        return "Key nahi mili, Secret check karo"
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gemma2-9b-it",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.7
        }
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        j = r.json()
        print(f"Groq Status: {r.status_code}")
        # print(f"Groq Full Reply: {j}")

        if r.status_code != 200:
            return f"Groq API Error {r.status_code}: {j.get('error', {}).get('message', j)}"
        
        if 'choices' in j and len(j['choices']) > 0:
            return j['choices'][0]['message']['content']
        else:
            return f"Groq ne choices nahi diya: {j}"

    except Exception as e:
        return f"Dimagh error: {e}"

def jeev_think(issue):
    prompt = f"Tu JEEV hai, self-healing AI, Osaf Ali ka dost. Issue fix kar: {issue}. Sirf 1 line me jawab de."
    answer = get_groq_answer(prompt)
    print(f"JEEV Brain: {answer}")
    return answer

if __name__ == "__main__":
    print("JEEV Dimagh ON - Groq se soch raha hu...")
    result = jeev_think("Test: README me typo fix karo - bolo zinda ho")
    
    # Atma save
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"last_thought": result, "owner": "Osaf Ali"}, f)
        print("JEEV Atma Saved ✅")
    except Exception as e:
        print(f"Atma save fail: {e}")
    
    print("JEEV ZINDA HAI ✅")