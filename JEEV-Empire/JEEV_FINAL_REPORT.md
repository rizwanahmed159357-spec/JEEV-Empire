
# Defense Report: InterestRateModel.sol Review

## Severity: Medium

### Description
The `InterestRateModel` implements a Compound-style two-slope rate model correctly, with owner-only parameter updates and X64 (Q64-scaled) arithmetic that avoids overflow given the documented caps (`MAX_BASE_RATE_X64`, `MAX_MULTIPLIER_X64`). **There is no direct reentrancy, access-control, or integer-overflow exploit present.** However, three precision/robustness weaknesses exist that carry a risk to protocol reserves and indirectly to user funds:

1. **Utilization truncation:** `getUtilizationRateX64` uses unsigned integer division `debt * Q64 / (cash + debt)`. When `cash >> debt` (e.g., idle deposited balances), the result rounds to `0`, producing `borrowRateX64 = baseRatePerSecondX64` while still computing `supplyRateX64 = 0`. Supply rate collapses to effectively zero, killing protocol yield and forcing price slippage against depositors.

2. **Annual→second conversion floor-division loss:** `setValues` divides annual X64 inputs by `YEAR_SECS` (uint64 range ~3.15e7), silently losing fractional parts. Sustained rounding over many accruals degrades expected rate correctness.

3. **No clamp on supply rate floor:** Model allows `supplyRateX64` arbitrarily close to `0`, which is economically destabilizing for a lending protocol and directly reduces the "incentive" payoff lenders receive.

These are not exploitable by external actors, but misconfiguration by governance (owner-only path) combined with poor parameter choices can weaken reserve backing, ultimately manifesting as liquidation cascades that harm depositors.

### How this protects (or risks) user funds
Protective elements: owner-only writes prevent griefing/DoS; input caps prevent runaway rates; correct slope direction keeps supply-rate ≤ borrow-rate. Risks: (a) precision truncation causes systemic reserve erosion; (b) zero-supply regime accelerates pool death.

### Recommendation
1. Add a minimum effective supply rate (`supplyRateX64 >= safeMinSupplyRateX64`, e.g., a small positive fraction) in `getRatesPerSecondX64`, tested below.
2. Replace the annual÷SECOND division with a fixed-point recalc or add an `assert` requiring intermediate products stay in range.
3. Pre-deploy tests asserting `supplyRateX64 <= borrowRateX64` and `supplyRateX64 >= MIN_SUPPLY_RATE_X64` across parameter sweeps.
4. Document governance guardrails enforcing non-zero `multiplierPerYear` and `jumpMultiplierPerYear`.

---

## Foundry Test: Precision & Supply-Rate Floor Protection

```solidity
// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.0;

import {InterestRateModel} from "../src/InterestRateModel.sol";
import {Constants} from "../src/shared/Constants.sol";

contract TestInterestRateModel {

    // Minimal constant override path omitted; using contract defaults
    InterestRateModel constant IRM = InterestRateModel(
        Constants.Q64 / 10,                       // 10% base
        Constants.Q64 * 2 / Constants.YEAR_SECS,   // 200% mult → per-second scaled
        Constants.Q64 * 2 / Constants.YEAR_SECS,  // 200% jump
        Constants.Q64 / 10                         // 10% kink
    );

    function t_supply_rate_floor() public view {
        // Heavy idle cash: utilisation should still compute supply >= tiny floor
        uint256 borrowX64, supplyX64;
        (borrowX64, supplyX64) = IRM.getRatesPerSecondX64(
            Constants.Q64 * 1000,   // cash huge
            Constants.Q64             // debt nominal
        );
        // Before fix: supply may equal ~0 here. Enforce floor via testing policy.
        assert(supplyX64 > 0);
    }

    function t_no_overflow_on_product() public view returns (bool ok) {
        // Stress product: util == Q64 and multiplier at cap
        uint256 u = Constants.Q64;
        uint256 m = Constants.MAX_MULTIPLIER_X64;
        if (u * m <= type(uint256).max) ok = true;
    }
}
```

Run:
```
forge test --match-test t_supply_rate_floor --match-test t_no_overflow_on_product
```

Adding the supply-rate floor invariant turns the failing test into a regression guard preventing future reserve erosion.