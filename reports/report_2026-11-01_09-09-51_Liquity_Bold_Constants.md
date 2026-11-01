Title: Missing disableInitializers in Constants.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | pragma solidity 0.8.24;
   3 | 
   4 | address constant ZERO_ADDRESS = address(0);
   5 | 
   6 | uint256 constant MAX_UINT256 = type(uint256).max;
   7 | 
   8 | uint256 constant DECIMAL_PRECISION = 1e18;
   9 | uint256 constant _100pct = DECIMAL_PRECISION;
  10 | uint256 constant _1pct = DECIMAL_PRECISION / 100;
  11 | 
  12 | // Amount of ETH to be locked in gas pool on opening troves
  13 | uint256 constant ETH_GAS_COMPENSATION = 0.0375 ether;
  14 | 
  15 | // Liquidation
  16 | uint256 constant MIN_LIQUIDATION_PENALTY_SP = 5e16; // 5%
  17 | uint256 constant MAX_LIQUIDATION_PENALTY_REDISTRIBUTION = 20e16; // 20%
  18 | 
  19 | // Collateral branch parameters (SETH = staked ETH, i.e. wstETH / rETH)
  20 | uint256 constant CCR_WETH = 150 * _1pct;
  21 | uint256 constant CCR_SETH = 160 * _1pct;
  22 | 
  23 | uint256 constant MCR_WETH = 110 * _1pct;
  24 | uint256 constant MCR_SETH = 120 * _1pct;
  25 | 
  26 | uint256 constant SCR_WETH = 110 * _1pct;
  27 | uint256 constant SCR_SETH = 120 * _1pct;
  28 | 
  29 | // Batch CR buffer (same for all branches for now)
  30 | // On top of MCR to join a batch, or adjust inside a batch
  31 | uint256 constant BCR_ALL = 10 * _1pct;
  32 | 
  33 | uint256 constant LIQUIDATION_PENALTY_SP_WETH = 5 * _1pct;
  34 | uint256 constant LIQUIDATION_PENALTY_SP_SETH = 5 * _1pct;
  35 | 
  36 | uint256 constant LIQUIDATION_PENALTY_REDISTRIBUTION_WETH = 10 * _1pct;
  37 | uint256 constant LIQUIDATION_PENALTY_REDISTRIBUTION_SETH = 20 * _1pct;
  38 | 
  39 | // Fraction of collateral awarded to liquidator
  40 | uint256 constant COLL_GAS_COMPENSATION_DIVISOR = 200; // dividing by 200 yields 0.5%
  41 | uint256 constant COLL_GAS_COMPENSATION_CAP = 2 ether; // Max coll gas compensation capped at 2 ETH
  42 | 
  43 | // Minimum amount of net Bold debt a trove must have
  44 | uint256 constant MIN_DEBT = 2000e18;
  45 | 
  46 | uint256 constant MIN_ANNUAL_INTEREST_RATE = _1pct / 2; // 0.5%
  47 | uint256 constant MAX_ANNUAL_INTEREST_RATE = 250 * _1pct;
  48 | 
  49 | // Batch management params
  50 | uint128 constant MAX_ANNUAL_BATCH_MANAGEMENT_FEE = uint128(_100pct / 10); // 10%
  51 | uint128 constant MIN_INTEREST_RATE_CHANGE_PERIOD = 1 hours; // only applies to batch managers / batched Troves
  52 | 
  53 | uint256 constant REDEMPTION_FEE_FLOOR = _1pct / 2; // 0.5%
  54 | 
  55 | // For the debt / shares ratio to increase by a factor 1e9
  56 | // at a average annual debt increase (compounded interest + fees) of 10%, it would take more than 217 years (log(1e9)/log(1.1))
  57 | // at a average annual debt increase (compounded interest + fees) of 50%, it would take more than 51 years (log(1e9)/log(1.5))
  58 | // The increase pace could be forced to be higher through an inflation attack,
  59 | // but precisely the fact that we have this max value now prevents the attack
  60 | uint256 constant MAX_BATCH_SHARES_RATIO = 1e9;
  61 | 
  62 | // Half-life of 6h. 6h = 360 min
  63 | // (1/2) = d^360 => d = (1/2)^(1/360)
  64 | uint256 constant REDEMPTION_MINUTE_DECAY_FACTOR = 998076443575628800;
  65 | 
  66 | // BETA: 18 digit decimal. Parameter by which to divide the redeemed fraction, in order to calc the new base rate from a redemption.
  67 | // Corresponds to (1 / ALPHA) in the white paper.
  68 | uint256 constant REDEMPTION_BETA = 1;
  69 | 
  70 | // To prevent redemptions unless Bold depegs below 0.95 and allow the system to take off
  71 | uint256 constant INITIAL_BASE_RATE = _100pct; // 100% initial redemption rate
  72 | 
  73 | // Discount to be used once the shutdown thas been triggered
  74 | uint256 constant URGENT_REDEMPTION_BONUS = 2e16; // 2%
  75 | 
  76 | uint256 constant ONE_MINUTE = 1 minutes;
  77 | uint256 constant ONE_YEAR = 365 days;
  78 | uint256 constant UPFRONT_INTEREST_PERIOD = 7 days;
  79 | uint256 constant INTEREST_RATE_ADJ_COOLDOWN = 7 days;
  80 | 
  81 | uint256 constant SP_YIELD_SPLIT = 75 * _1pct; // 75%
  82 | 
  83 | uint256 constant MIN_BOLD_IN_SP = 1e18;
  84 | 
  85 | // Dummy contract that lets legacy Hardhat tests query some of the constants
  86 | contract Constants {
  87 |     uint256 public constant _ETH_GAS_COMPENSATION = ETH_GAS_COMPENSATION;
  88 |     uint256 public constant _MIN_DEBT = MIN_DEBT;
  89 | }
  90 | 