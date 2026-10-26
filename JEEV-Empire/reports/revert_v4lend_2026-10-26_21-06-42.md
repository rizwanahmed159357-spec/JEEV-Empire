# Audit /tmp/v4lend/src/oracle/V4Oracle.sol
File: /tmp/v4lend/src/oracle/V4Oracle.sol
Strategy: COMPETITION - None - TO_CHECK - $None
Wallet: 0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40

Review: V4Oracle uses Chainlink + Uniswap v3 TWAP with maxDifference check. Need to verify TWAP window and staleness. No obvious reentrancy in oracle (view). Check V4Vault for CEI.

Status: Manual review needed - Auto model gave safety filter.