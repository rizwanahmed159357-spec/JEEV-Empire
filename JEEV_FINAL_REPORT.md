**Bug Report — `contracts/PremiumStaking.sol`**

| Field | Detail |
|-------|--------|
| **Contract** | `PremiumStaking` |
| **Severity** | Critical |
| **Component** | `emergencyWithdraw()` / missing staking logic |
| **Language** | Solidity ^0.8.20 |

---

### 1. Vulnerability

**Missing stake/deposit function and no custody of staked tokens.**

The contract tracks user balances in `stakedBalances` and a global `totalStaked`, but it never provides a function for users to actually deposit/stake tokens. Therefore:

* `stakedBalances[msg.sender]` is always `0` for every user.
* `emergencyWithdraw()` always reverts with `"No balance"`.
* Even if balances were manually set, the contract never calls `transferFrom` to take custody of the underlying ERC20 tokens, so it cannot pay out withdrawals.

**Secondary issue:** `stakingToken.transfer(msg.sender, balance)` does not check the return value. Non-standard ERC20 tokens may return `false` instead of reverting, causing the contract to record a withdrawal as successful when the tokens were never sent.

---

### 2. Root Cause

1. There is no `deposit()` / `stake()` function that:
   * pulls tokens from the user via `safeTransferFrom`, and
   * updates `stakedBalances` and `totalStaked`.
2. `emergencyWithdraw()` uses the raw `IERC20.transfer()` instead of `SafeERC20.safeTransfer()`, so a failing token transfer that returns `false` is ignored.
3. The constructor does not validate that `_stakingToken != address(0)`.

---

### 3. Impact

* The contract is non-functional: users can never stake 10,000 tokens (or any amount) and can never withdraw them.
* If a partial deployment relies on this code, users will be unable to exit their positions.
* Using raw `transfer` without checking the return value can result in state changes (balance zeroed, `totalStaked` reduced) without actual token delivery when interacting with non-compliant ERC20 tokens.

---

### 4. Fix

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract PremiumStaking {
    IERC20 public stakingToken;
    mapping(address => uint256) public stakedBalances;
    uint256 public totalStaked;

    using SafeERC20 for IERC20;

    constructor(address _stakingToken) {
        require(_stakingToken != address(0), "Invalid token address");
        stakingToken = IERC20(_stakingToken);
    }

    /// @notice Users must first `approve` this contract, then call deposit to stake tokens.
    function deposit(uint256 amount) external {
        require(amount > 0, "Amount must be greater than 0");
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);
        stakedBalances[msg.sender] += amount;
        totalStaked += amount;
    }

    function emergencyWithdraw() external {
        uint256 balance = stakedBalances[msg.sender];
        require(balance > 0, "No balance");

        // Update state before external interaction (checks-effects-interactions)
        stakedBalances[msg.sender] = 0;
        totalStaked -= balance;

        // safeTransfer reverts if the ERC20 transfer fails or returns false
        stakingToken.safeTransfer(msg.sender, balance);
    }
}
```

---

### 5. Summary of Changes

| Change | Reason |
|--------|--------|
| Added `deposit(uint256 amount)` | Allows users to stake tokens (e.g., 10,000 tokens). |
| `safeTransferFrom(msg.sender, address(this), amount)` | Takes custody of the user's ERC20 tokens after they `approve` the contract. |
| `using SafeERC20 for IERC20;` + `safeTransfer` | Guarantees revert on failed/false ERC20 transfers. |
| Constructor zero-address check | Prevents deployment with an invalid token address. |
| State updated before external call | Maintains checks-effects-interactions ordering. |

After this fix, users can:
1. Call `ERC20.approve(address(this), 10000)` on the staking token.
2. Call `premiumStaking.deposit(10000)` to stake.
3. Call `premiumStaking.emergencyWithdraw()` to withdraw their full balance safely.