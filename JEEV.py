# JEEV.py - FINAL with Groq Brain + Resume Power
import os, json, requests

STATE_FILE = "jeev_atma.json"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_groq_answer(prompt):
    if not GROQ_API_KEY:
        return "Key nahi mili, Secret check karo"
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]},
            timeout=15)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Dimagh error: {e}"

def jeev_think(issue):
    prompt = f"Tu JEEV hai, self-healing AI. Issue fix kar: {issue}. Sirf code de."
    answer = get_groq_answer(prompt)
    print(f"JEEV Brain: {answer}")
    return answer

if __name__ == "__main__":
    print("JEEV Dimagh ON - Groq se soch raha hu...")
    jeev_think("Test: README me typo fix karo")