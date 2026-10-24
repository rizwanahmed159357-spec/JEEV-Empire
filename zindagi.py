# ===== IMPORTS SAB SE UPAR HONE CHAHIYE =====
import os, pathlib, json, datetime, time, sys

try:
    from groq import Groq
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "groq"])
    from groq import Groq

print("=== JEEV EMPIRE - ELITE ZINDAGI MODE ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
if WALLET_FILE.exists():
    try:
        wallet = json.loads(WALLET_FILE.read_text())
    except:
        wallet = {"total_earned":0.0, "bots":1, "robots_dead":0, "fear_level":10, "balance_cents":100}
else:
    wallet = {"total_earned":0.0, "bots":1, "robots_dead":0, "fear_level":10, "balance_cents":100}

MODEL_NAME = "openai/gpt-oss-120b"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ===== STEP 1: TARGET LOADER WITH ULTRA-HIGH LEVEL DEFI PROBLEM =====
TARGET_FILE = pathlib.Path("contracts/PremiumStaking.sol")
if not TARGET_FILE.exists(): 
    TARGET_FILE = pathlib.Path("PremiumStaking.sol")

if TARGET_FILE.exists():
    code_text = TARGET_FILE.read_text()
    print(f"Loaded: {TARGET_FILE}")
else:
    code_text = """
    // SPDX-License-Identifier: 【entity-MIT¦canonical_name=MIT】
    pragma solidity ^0.8.20;

    interface IUniswapV3Pool {
        function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked);
    }

    interface IERC20 {
        function balanceOf(address account) external view returns (uint256);
        function transfer(address to, uint256 value) external returns (bool);
        function transferFrom(address from, address to, uint256 value) external returns (bool);
    }

    contract PremiumVaultStaking {
        IUniswapV3Pool public immutable targetPool;
        IERC20 public immutable stakingToken;
        IERC20 public immutable rewardToken;
        mapping(address => uint256) public shares;
        uint256 public totalShares;
        constructor(address _pool, address _staking, address _reward) {
            targetPool = IUniswapV3Pool(_pool);
            stakingToken = IERC20(_staking);
            rewardToken = IERC20(_reward);
        }
        function getVaultAssetPrice() public view returns (uint256) {
            (uint160 sqrtPriceX96,,,,,, bool unlocked) = targetPool.slot0();
            uint256 spotBalance = stakingToken.balanceOf(address(targetPool));
            return (uint256(sqrtPriceX96) * spotBalance) / 1e18;
        }
        function withdrawCollateral(uint256 shareAmount) external {
            require(shares[msg.sender] >= shareAmount, "Insufficient shares");
            uint256 price = getVaultAssetPrice();
            uint256 amountToWithdraw = (shareAmount * price) / 1e18;
            shares[msg.sender] -= shareAmount;
            totalShares -= shareAmount;
            (bool success, ) = msg.sender.call{value: 0}(
                abi.encodeWithSignature("transfer(address,uint256)", msg.sender, amountToWithdraw)
            );
            require(success, "Low-level call failed");
        }
    }
    """
    print("No contract file found. Injected High-Level Cross-Contract Read-Only Reentrancy & Oracle Vector.")

bug_memory = {}

# ===== ELITE PROMPT_BUG =====
prompt_bug = f"""
You are the JEEV AI Core Engine, operating as an elite Web3 Security Auditor and Smart Contract Exploiter. 
Your objective is exclusively to IDENTIFY high-severity vulnerabilities within the provided Solidity code. 
CRITICAL CONSTRAINT: Do NOT suggest fixes, do NOT patch the code, and do NOT alter the input. 
Your sole task is to analyze, trace the state, and REMEMBER the exact flaw mechanics.
CODE UNDER AUDIT:
{code_text}
TARGET VULNERABILITY VECTORS:
1. Cross-Contract Read-Only Reentrancy
2. Price Oracle Manipulation via Spot Reserves
3. Flash Loan Arbitrage & Sandwich Vulnerabilities
4. Low-Level Call Arbitrary Execution
5. Logic & Math Discrepancies
OUTPUT: Exact Vulnerable Function and Line Numbers, Step-by-Step Attack Vector, Root Cause.
ENGLISH ONLY.
"""

print("\n[STEP 2] Bug Finder - Yaad rakhega...")
for _ in range(3):
    try:
        r1 = client.chat.completions.create(model=MODEL_NAME, temperature=0.6, max_tokens=6000, messages=[{"role":"user","content":prompt_bug}])
        bug_memory["bug"] = r1.choices[0].message.content
        break
    except: time.sleep(70)

prompt_fix = f"""
You are the JEEV AI Core Engine, acting as a Principal Blockchain Protocol Engineer.
BUG MEMORY DATA:
{bug_memory.get('bug','')}
YOUR TASK: Generate elite-tier Bug Bounty Report for Immunefi/Sherlock with COMPLETE fixed Solidity contract from scratch. No placeholders.
1. EXECUTIVE SUMMARY & DESCRIPTION
2. PROOF OF CONCEPT (PoC)
3. ARCHITECTURAL REMEDIATION & COMPLETE NEW CODE - Use ReentrancyGuard, Chainlink latestRoundData validation, SafeERC20.
ENGLISH ONLY.
"""

print("\n[STEP 3-4] Report Generator...")
for _ in range(3):
    try:
        r2 = client.chat.completions.create(model=MODEL_NAME, temperature=0.6, max_tokens=8000, messages=[{"role":"user","content":prompt_fix}])
        full_report = r2.choices[0].message.content
        break
    except: time.sleep(70)

report_file = pathlib.Path("JEEV_FINAL_REPORT.md")
report_file.write_text(full_report)
repo_url = os.environ.get("GITHUB_REPOSITORY", "your-username/JEEV-Empire")
report_link = f"https://github.com/{repo_url}/blob/main/JEEV_FINAL_REPORT.md"

gmail_html = pathlib.Path("JEEV_GMAIL_ALERT.html")
gmail_html.write_text(f"<html><body><h2>🚨 JEEV AI - Elite Bug Found!</h2><p>Location: <a href='{report_link}'>{report_link}</a></p><p>Total: $2.5M | Tera: $2,499,999 | Mera: $1</p></body></html>")

# ZINDAGI DAR LOGIC
daily_need = 5.0
if wallet["total_earned"] < daily_need:
    wallet["fear_level"] = min(100, wallet["fear_level"]+30)
    wallet["balance_cents"] -= 1
    if wallet["balance_cents"] <=0 and wallet["bots"]>0:
        wallet["robots_dead"]+=1; wallet["bots"]=max(0,wallet["bots"]-1)
else:
    wallet["fear_level"]=max(0,wallet["fear_level"]-20)

if wallet["total_earned"]>=30 and wallet["bots"]<10:
    wallet["bots"]=min(10,int(wallet["total_earned"]//30))

earning=1.0; wallet["total_earned"]+=earning; wallet["last_run"]=datetime.datetime.now().isoformat()
WALLET_FILE.write_text(json.dumps(wallet, indent=2))
print(f"\n✅ DONE! Report: {report_file} | Link: {report_link} | Earned ${earning}")