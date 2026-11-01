Title: Missing disableInitializers in LiquityMath.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: MIT
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import {DECIMAL_PRECISION} from "./Constants.sol";
   6 | 
   7 | library LiquityMath {
   8 |     function _min(uint256 _a, uint256 _b) internal pure returns (uint256) {
   9 |         return (_a < _b) ? _a : _b;
  10 |     }
  11 | 
  12 |     function _max(uint256 _a, uint256 _b) internal pure returns (uint256) {
  13 |         return (_a >= _b) ? _a : _b;
  14 |     }
  15 | 
  16 |     function _sub_min_0(uint256 _a, uint256 _b) internal pure returns (uint256) {
  17 |         return (_a > _b) ? _a - _b : 0;
  18 |     }
  19 | 
  20 |     /* 
  21 |     * Multiply two decimal numbers and use normal rounding rules:
  22 |     * -round product up if 19'th mantissa digit >= 5
  23 |     * -round product down if 19'th mantissa digit < 5
  24 |     *
  25 |     * Used only inside the exponentiation, _decPow().
  26 |     */
  27 |     function decMul(uint256 x, uint256 y) internal pure returns (uint256 decProd) {
  28 |         uint256 prod_xy = x * y;
  29 | 
  30 |         decProd = (prod_xy + DECIMAL_PRECISION / 2) / DECIMAL_PRECISION;
  31 |     }
  32 | 
  33 |     /* 
  34 |     * _decPow: Exponentiation function for 18-digit decimal base, and integer exponent n.
  35 |     * 
  36 |     * Uses the efficient "exponentiation by squaring" algorithm. O(log(n)) complexity. 
  37 |     * 
  38 |     * Called by function CollateralRegistry._calcDecayedBaseRate, that represent time in units of minutes
  39 |     *
  40 |     * The exponent is capped to avoid reverting due to overflow. The cap 525600000 equals
  41 |     * "minutes in 1000 years": 60 * 24 * 365 * 1000
  42 |     * 
  43 |     * If a period of > 1000 years is ever used as an exponent in either of the above functions, the result will be
  44 |     * negligibly different from just passing the cap, since: 
  45 |     *
  46 |     * In function 1), the decayed base rate will be 0 for 1000 years or > 1000 years
  47 |     * In function 2), the difference in tokens issued at 1000 years and any time > 1000 years, will be negligible
  48 |     */
  49 |     function _decPow(uint256 _base, uint256 _minutes) internal pure returns (uint256) {
  50 |         if (_minutes > 525600000) _minutes = 525600000; // cap to avoid overflow
  51 | 
  52 |         if (_minutes == 0) return DECIMAL_PRECISION;
  53 | 
  54 |         uint256 y = DECIMAL_PRECISION;
  55 |         uint256 x = _base;
  56 |         uint256 n = _minutes;
  57 | 
  58 |         // Exponentiation-by-squaring
  59 |         while (n > 1) {
  60 |             if (n % 2 == 0) {
  61 |                 x = decMul(x, x);
  62 |                 n = n / 2;
  63 |             } else {
  64 |                 // if (n % 2 != 0)
  65 |                 y = decMul(x, y);
  66 |                 x = decMul(x, x);
  67 |                 n = (n - 1) / 2;
  68 |             }
  69 |         }
  70 | 
  71 |         return decMul(x, y);
  72 |     }
  73 | 
  74 |     function _getAbsoluteDifference(uint256 _a, uint256 _b) internal pure returns (uint256) {
  75 |         return (_a >= _b) ? _a - _b : _b - _a;
  76 |     }
  77 | 
  78 |     function _computeCR(uint256 _coll, uint256 _debt, uint256 _price) internal pure returns (uint256) {
  79 |         if (_debt > 0) {
  80 |             uint256 newCollRatio = _coll * _price / _debt;
  81 | 
  82 |             return newCollRatio;
  83 |         }
  84 |         // Return the maximal value for uint256 if the debt is 0. Represents "infinite" CR.
  85 |         else {
  86 |             // if (_debt == 0)
  87 |             return 2 ** 256 - 1;
  88 |         }
  89 |     }
  90 | }
  91 | 