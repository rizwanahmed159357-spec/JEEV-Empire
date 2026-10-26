**Bug Report:**

The main bug in `PremiumStaking.sol` is that the contract has **no staking function**, and the accounting logic is incomplete.

- There is no function to actually stake tokens, so `stakedBalances` never gets updated.
- The global `totalStaked` is never increased when tokens are staked.
- The `emergencyWithdraw` function relies on `stakedBalances[msg.sender]`, but since users cannot stake through this contract, the mapping remains `0` for everyone.

This means users cannot withdraw their staked funds, and the contract’s accounting is broken.

**For the amount of 10,000 tokens:**

If a user tries to stake 10,000 tokens, the contract should:

1. Pull 10,000 tokens from the user.
2. Update `stakedBalances[msg.sender] += 10_000`.
3. Update `totalStaked += 10_000`.

Without that, the 10,000 tokens cannot be properly tracked, and the user cannot withdraw them later via `emergencyWithdraw`.

---

**Fix:**

Add a `stake` function and update the accounting.

```solidity
function stake(uint256 amount) external {
    require(stakingToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
    stakedBalances[msg.sender] += amount;
    totalStaked += amount;
}

function emergencyWithdraw() external {
    uint256 balance = stakedBalances[msg.sender];
    require(balance > 0, "No balance");
    stakedBalances[msg.sender] = 0;
    totalStaked -= balance;
    require(stakingToken.transfer(msg.sender, balance), "Transfer failed");
}
```

After the fix, if a user stakes **10,000 tokens**:

- `stakedBalances[msg.sender] = 10_000`
- `totalStaked = 10_000`

Then if they call `emergencyWithdraw`:

- `balance = 10_000`
- `stakedBalances[msg.sender] = 0`
- `totalStaked -= 10_000` → becomes `0`
- `stakingToken.transfer(msg.sender, 10_000)` → sends 10,000 back

So the funds can be withdrawn correctly.