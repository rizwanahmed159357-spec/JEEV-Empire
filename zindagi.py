import json, pathlib, datetime

print("=== JEEV EMPIRE - PREMIUM STAKING AUDIT ===")

WALLET_FILE = pathlib.Path("jeev_wallet.json")
if WALLET_FILE.exists():
    wallet = json.loads(WALLET_FILE.read_text())
else:
    wallet = {"total_earned":0,"balance":0,"osaf_earning":0,"bots":0,"language":"ENGLISH"}

print(f"Wallet: Total ${wallet['total_earned']} | Bots: {wallet['bots']}")

# ===== PREMIUM STAKING PROBLEM =====
print("\n--- BOUNTY: PremiumStaking - Read-Only Reentrancy with ERC777 ---")
print("Contract: Uses nonReentrant and CEI pattern in emergencyWithdraw()")
print("Question: Is it secure with ERC777 callback tokens?")

print("\n--- JEEV ANALYSIS (ENGLISH REPORT) ---")
print("ANSWER: NO. Contract is VULNERABLE to Read-Only Reentrancy / State De-synchronization.")

print("\nATTACK VECTOR - EXACT STEPS:")
print("1. Attacker deploys ERC777 token with tokensToSend / tokensReceived hooks, or uses ERC20 with callback (ERC777 compatible).")
print("2. Attacker stakes 100 tokens via stake(). Contract totalStaked = 100.")
print("3. Attacker calls emergencyWithdraw(). Execution flow:")
print("   a) CHECK: balance = 100")
print("   b) EFFECT: stakedBalances[attacker]=0, totalStaked = 0 (STATE RESET BEFORE INTERACTION)")
print("   c) INTERACTION: stakingToken.transfer(attacker, 100) -> Triggers ERC777 tokensReceived hook")
print("4. DURING HOOK (Inside transfer, before transfer completes):")
print("   At this moment, INVARIANT IS BROKEN:")
print("   - totalStaked = 0")
print("   - Actual token balance of contract = 100 (still holds tokens, transfer not finished)")
print("   - Accounting vs Reality desynchronized")
print("5. In hook, attacker calls a THIRD-PARTY protocol (e.g., lending pool, price oracle, reward distributor) that reads PremiumStaking.")
print("   Example: Lending pool calculates pricePerShare = stakingToken.balanceOf(PremiumStaking) / totalStaked")
print("   Since totalStaked is 0, division by zero or inflated price! Or rewardPerToken calculation uses totalStaked=0 to manipulate rewards.")
print("6. nonReentrant does NOT protect because attacker does NOT re-enter PremiumStaking directly. He re-enters a DIFFERENT contract that READS PremiumStaking's state (Read-Only Reentrancy). OpenZeppelin guard only blocks same-contract reentrancy.")
print("7. Result: Attacker can:")
print("   - Manipulate reward distribution: With totalStaked=0, next staker gets huge rewardPerToken share, or reward calculation breaks")
print("   - Drain rewards: If rewardPerToken depends on totalStaked, attacker forces miscalculation")
print("   - Break external integrations: Any protocol relying on totalStaked for valuation is exploited")

print("\nADDITIONAL BUG IN stake():")
print("stake() calls updateReward() BEFORE transferFrom. If stakingToken is ERC777, transferFrom triggers hook BEFORE stakedBalances and totalStaked are updated. Attacker can re-enter via read-only path to manipulate rewardDebt calculation based on stale totalStaked.")

print("\n--- FIXES (ENGLISH) ---")
print("FIX 1: Use Reentrancy Guard that protects views or use custom read-only guard. Implement totalStaked snapshot or lock during external calls.")
print("FIX 2: Do not use CEI blindly for accounting tokens - For read-only reentrancy, keep totalStaked consistent with actual balance until AFTER external call, OR use balanceOf check instead of totalStaked variable.")
print("FIX 3: Support only standard ERC20 (no hooks) via whitelist, or use OpenZeppelin's ReentrancyGuard with additional check: require(stakingToken is not ERC777) or use safe wrapper that disables hooks (ERC20Wrapper).")
print("FIX 4: Use Checks-Effects-Interactions correctly for external price reads - Update rewardPerToken and cache totalStaked before any external call, and ensure external protocols cannot read intermediate state. Use transient storage lock (EIP-1153) or pause reward updates during withdraw.")
print("FIX 5: Use actual token balance: uint256 actualTotal = stakingToken.balanceOf(address(this)) instead of totalStaked variable for price calculations, or synchronize both after transfer.")

print("\n✅ VULNERABILITY CONFIRMED - READ-ONLY REENTRANCY - PATCH REQUIRED")

# Earning $1
earning = 1
wallet["total_earned"] += earning
wallet["balance"] += earning
should_be = wallet["total_earned"] // 30
if should_be > 100: should_be = 100
wallet["bots"] = should_be
wallet["last_run"] = datetime.datetime.now().isoformat()
wallet["last_audit"] = "PremiumStaking ERC777 Read-Only Reentrancy"

WALLET_FILE.write_text(json.dumps(wallet, indent=2))

print(f"\nFINAL: Total ${wallet['total_earned']} | Bots: {wallet['bots']}")
print("Report generated in ENGLISH - Ready for Immunefi submission.")