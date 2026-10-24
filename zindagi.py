import os, pathlib, json, datetime
from groq import Groq

print("=== JEEV EMPIRE - QWEN DEEP REASONING MODE ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
CONTRACT_FILE = pathlib.Path("contracts/PremiumStaking.sol")

if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0,"bots":0}
else:
    wallet = {"total_earned":0,"bots":0}

# ===== MODEL - QWEN DEEP REASONING =====
MODEL_NAME = "qwen-qwq-32b"  # <-- Deep Reasoning Model - Tera wala!
print(f"Using Model: {MODEL_NAME} (Deep Reasoning)")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not found! Add in GitHub Settings > Secrets > Actions > GROQ_API_KEY")
    exit()

client = Groq(api_key=api_key)

if not CONTRACT_FILE.exists():
    CONTRACT_FILE = pathlib.Path("PremiumStaking.sol")

code = CONTRACT_FILE.read_text() if CONTRACT_FILE.exists() else "// Contract not found"

print(f"\nAnalyzing: {CONTRACT_FILE.name} with {MODEL_NAME}...")
print("This model thinks deeply, so it may take 20-30 seconds...")

response = client.chat.completions.create(
    model=MODEL_NAME,
    temperature=0.1,  # Low temp for accurate audit
    max_tokens=6000,
    messages=[
        {"role": "system", "content": "You are a senior smart contract security auditor specializing in Read-Only Reentrancy. You MUST always respond in ENGLISH ONLY. No Urdu, Hindi. Provide detailed attack vector and complete fixed code."},
        {"role": "user", "content": f"""
Analyze this contract:

{code}

Tasks:
1. Is PremiumStaking vulnerable to Read-Only Reentrancy with ERC777 tokens even with nonReentrant and CEI?
2. Explain step-by-step how totalStaked vs stakingToken.balanceOf() desync is exploited during emergencyWithdraw() hook.
3. Why nonReentrant fails for read-only?
4. Provide complete FIXED Solidity contract with _isWithdrawing lock, SafeERC20, balanceBefore/After check, and view protection.

Answer in ENGLISH only.
"""}
    ]
)

ai_answer = response.choices[0].message.content
print("\n--- JEEV QWEN-QWQ-32B ANSWER (ENGLISH) ---")
print(ai_answer)

pathlib.Path("JEEV_AI_REPORT_QWEN.md").write_text(f"# Model: {MODEL_NAME}\nDate: {datetime.datetime.now().isoformat()}\n\n{ai_answer}")

earning = 1
wallet["total_earned"] += earning
wallet["bots"] = min(wallet["total_earned"] // 30, 100)
wallet["last_model"] = MODEL_NAME
wallet["last_run"] = datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\n✅ DONE - Model: {MODEL_NAME} | Total: ${wallet['total_earned']} | Bots: {wallet['bots']}")
print("Report saved: JEEV_AI_REPORT_QWEN.md")