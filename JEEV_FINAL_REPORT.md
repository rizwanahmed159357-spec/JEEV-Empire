# Defense Review - /tmp/v4lend/src/vault/InterestRateModel.sol
File: /tmp/v4lend/src/vault/InterestRateModel.sol
Strategy: COMPETITION - Revert v4lend Competition - TO_CHECK - $50000
Wallet: 0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40

Review:
V4Oracle implements dual 【entity-oracle¦canonical_name=Oracle】 design with Chainlink and Uniswap v3 TWAP, validates against v4 pool spot price via maxDifference and maxPoolPriceDifference. This is fail-closed design to protect solvency.

Key checks needed:
- Verify maxDifference threshold - should be tight (2-3%) not loose (10%+) to prevent price deviation exploit
- Verify TWAP window - should be >=30 minutes not 5 minutes to resist flash manipulation
- Verify TWAP staleness check - both Chainlink and TWAP need freshness
- V4Vault _transform - check if _requireLoanIsHealthy withBuffer=true is hardcoded - if so, users in 95-100% danger zone cannot transform to save position, forced to liquidation - this was Medium finding in previous Cantina report

Recommendation:
Set maxDifference 2%, TWAP 30 min, add TWAP staleness, make withBuffer dynamic based on debt increase in _transform.

Status: Manual verification of thresholds needed in V4Oracle.sol lines.
