Title: Missing disableInitializers in CollateralRegistry.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "openzeppelin-contracts/contracts/token/ERC20/extensions/IERC20Metadata.sol";
   6 | 
   7 | import "./Interfaces/ITroveManager.sol";
   8 | import "./Interfaces/IBoldToken.sol";
   9 | import "./Dependencies/Constants.sol";
  10 | import "./Dependencies/LiquityMath.sol";
  11 | 
  12 | import "./Interfaces/ICollateralRegistry.sol";
  13 | 
  14 | contract CollateralRegistry is ICollateralRegistry {
  15 |     // See: https://github.com/ethereum/solidity/issues/12587
  16 |     uint256 public immutable totalCollaterals;
  17 | 
  18 |     IERC20Metadata internal immutable token0;
  19 |     IERC20Metadata internal immutable token1;
  20 |     IERC20Metadata internal immutable token2;
  21 |     IERC20Metadata internal immutable token3;
  22 |     IERC20Metadata internal immutable token4;
  23 |     IERC20Metadata internal immutable token5;
  24 |     IERC20Metadata internal immutable token6;
  25 |     IERC20Metadata internal immutable token7;
  26 |     IERC20Metadata internal immutable token8;
  27 |     IERC20Metadata internal immutable token9;
  28 | 
  29 |     ITroveManager internal immutable troveManager0;
  30 |     ITroveManager internal immutable troveManager1;
  31 |     ITroveManager internal immutable troveManager2;
  32 |     ITroveManager internal immutable troveManager3;
  33 |     ITroveManager internal immutable troveManager4;
  34 |     ITroveManager internal immutable troveManager5;
  35 |     ITroveManager internal immutable troveManager6;
  36 |     ITroveManager internal immutable troveManager7;
  37 |     ITroveManager internal immutable troveManager8;
  38 |     ITroveManager internal immutable troveManager9;
  39 | 
  40 |     IBoldToken public immutable boldToken;
  41 | 
  42 |     uint256 public baseRate;
  43 | 
  44 |     // The timestamp of the latest fee operation (redemption or new Bold issuance)
  45 |     uint256 public lastFeeOperationTime = block.timestamp;
  46 | 
  47 |     event BaseRateUpdated(uint256 _baseRate);
  48 |     event LastFeeOpTimeUpdated(uint256 _lastFeeOpTime);
  49 | 
  50 |     constructor(IBoldToken _boldToken, IERC20Metadata[] memory _tokens, ITroveManager[] memory _troveManagers) {
  51 |         uint256 numTokens = _tokens.length;
  52 |         require(numTokens > 0, "Collateral list cannot be empty");
  53 |         require(numTokens <= 10, "Collateral list too long");
  54 |         totalCollaterals = numTokens;
  55 | 
  56 |         boldToken = _boldToken;
  57 | 
  58 |         token0 = _tokens[0];
  59 |         token1 = numTokens > 1 ? _tokens[1] : IERC20Metadata(address(0));
  60 |         token2 = numTokens > 2 ? _tokens[2] : IERC20Metadata(address(0));
  61 |         token3 = numTokens > 3 ? _tokens[3] : IERC20Metadata(address(0));
  62 |         token4 = numTokens > 4 ? _tokens[4] : IERC20Metadata(address(0));
  63 |         token5 = numTokens > 5 ? _tokens[5] : IERC20Metadata(address(0));
  64 |         token6 = numTokens > 6 ? _tokens[6] : IERC20Metadata(address(0));
  65 |         token7 = numTokens > 7 ? _tokens[7] : IERC20Metadata(address(0));
  66 |         token8 = numTokens > 8 ? _tokens[8] : IERC20Metadata(address(0));
  67 |         token9 = numTokens > 9 ? _tokens[9] : IERC20Metadata(address(0));
  68 | 
  69 |         troveManager0 = _troveManagers[0];
  70 |         troveManager1 = numTokens > 1 ? _troveManagers[1] : ITroveManager(address(0));
  71 |         troveManager2 = numTokens > 2 ? _troveManagers[2] : ITroveManager(address(0));
  72 |         troveManager3 = numTokens > 3 ? _troveManagers[3] : ITroveManager(address(0));
  73 |         troveManager4 = numTokens > 4 ? _troveManagers[4] : ITroveManager(address(0));
  74 |         troveManager5 = numTokens > 5 ? _troveManagers[5] : ITroveManager(address(0));
  75 |         troveManager6 = numTokens > 6 ? _troveManagers[6] : ITroveManager(address(0));
  76 |         troveManager7 = numTokens > 7 ? _troveManagers[7] : ITroveManager(address(0));
  77 |         troveManager8 = numTokens > 8 ? _troveManagers[8] : ITroveManager(address(0));
  78 |         troveManager9 = numTokens > 9 ? _troveManagers[9] : ITroveManager(address(0));
  79 | 
  80 |         // Initialize the baseRate state variable
  81 |         baseRate = INITIAL_BASE_RATE;
  82 |         emit BaseRateUpdated(INITIAL_BASE_RATE);
  83 |     }
  84 | 
  85 |     struct RedemptionTotals {
  86 |         uint256 numCollaterals;
  87 |         uint256 boldSupplyAtStart;
  88 |         uint256 unbacked;
  89 |         uint256 redeemedAmount;
  90 |     }
  91 | 
  92 |     function redeemCollateral(uint256 _boldAmount, uint256 _maxIterationsPerCollateral, uint256 _maxFeePercentage)
  93 |         external
  94 |     {
  95 |         _requireValidMaxFeePercentage(_maxFeePercentage);
  96 |         _requireAmountGreaterThanZero(_boldAmount);
  97 | 
  98 |         RedemptionTotals memory totals;
  99 | 
 100 |         totals.numCollaterals = totalCollaterals;
 101 |         uint256[] memory unbackedPortions = new uint256[](totals.numCollaterals);
 102 |         uint256[] memory prices = new uint256[](totals.numCollaterals);
 103 | 
 104 |         // Gather and accumulate unbacked portions
 105 |         for (uint256 index = 0; index < totals.numCollaterals; index++) {
 106 |             ITroveManager troveManager = getTroveManager(index);
 107 |             (uint256 unbackedPortion, uint256 price, bool redeemable) =
 108 |                 troveManager.getUnbackedPortionPriceAndRedeemability();
 109 |             prices[index] = price;
 110 |             if (redeemable) {
 111 |                 totals.unbacked += unbackedPortion;
 112 |                 unbackedPortions[index] = unbackedPortion;
 113 |             }
 114 |         }
 115 | 
 116 |         // There’s an unlikely scenario where all the normally redeemable branches (i.e. having TCR > SCR) have 0 unbacked
 117 |         // In that case, we redeem proportionally to branch size
 118 |         if (totals.unbacked == 0) {
 119 |             unbackedPortions = new uint256[](totals.numCollaterals);
 120 |             for (uint256 index = 0; index < totals.numCollaterals; index++) {
 121 |                 ITroveManager troveManager = getTroveManager(index);
 122 |                 (,, bool redeemable) = troveManager.getUnbackedPortionPriceAndRedeemability();
 123 |                 if (redeemable) {
 124 |                     uint256 unbackedPortion = troveManager.getEntireBranchDebt();
 125 |                     totals.unbacked += unbackedPortion;
 126 |                     unbackedPortions[index] = unbackedPortion;
 127 |                 }
 128 |             }
 129 |         } else {
 130 |             // Don't allow redeeming more than the total unbacked in one go, as that would result in a disproportionate
 131 |             // redemption (see CS-BOLD-013). Instead, truncate the redemption to total unbacked. If this happens, the
 132 |             // redeemer can call `redeemCollateral()` a second time to redeem the remainder of their BOLD.
 133 |             if (_boldAmount > totals.unbacked) {
 134 |                 _boldAmount = totals.unbacked;
 135 |             }
 136 |         }
 137 | 
 138 |         totals.boldSupplyAtStart = boldToken.totalSupply();
 139 |         // Decay the baseRate due to time passed, and then increase it according to the size of this redemption.
 140 |         // Use the saved total Bold supply value, from before it was reduced by the redemption.
 141 |         // We only compute it here, and update it at the end,
 142 |         // because the final redeemed amount may be less than the requested amount
 143 |         // Redeemers should take this into account in order to request the optimal amount to not overpay
 144 |         uint256 redemptionRate =
 145 |             _calcRedemptionRate(_getUpdatedBaseRateFromRedemption(_boldAmount, totals.boldSupplyAtStart));
 146 |         require(redemptionRate <= _maxFeePercentage, "CR: Fee exceeded provided maximum");
 147 |         // Implicit by the above and the _requireValidMaxFeePercentage checks
 148 |         //require(newBaseRate < DECIMAL_PRECISION, "CR: Fee would eat up all collateral");
 149 | 
 150 |         // Compute redemption amount for each collateral and redeem against the corresponding TroveManager
 151 |         for (uint256 index = 0; index < totals.numCollaterals; index++) {
 152 |             //uint256 unbackedPortion = unbackedPortions[index];
 153 |             if (unbackedPortions[index] > 0) {
 154 |                 uint256 redeemAmount = _boldAmount * unbackedPortions[index] / totals.unbacked;
 155 |                 if (redeemAmount > 0) {
 156 |                     ITroveManager troveManager = getTroveManager(index);
 157 |                     uint256 redeemedAmount = troveManager.redeemCollateral(
 158 |                         msg.sender, redeemAmount, prices[index], redemptionRate, _maxIterationsPerCollateral
 159 |                     );
 160 |                     totals.redeemedAmount += redeemedAmount;
 161 |                 }
 162 | 
 163 |                 // Ensure that per-branch redeems add up to `_boldAmount` exactly
 164 |                 _boldAmount -= redeemAmount;
 165 |                 totals.unbacked -= unbackedPortions[index];
 166 |             }
 167 |         }
 168 | 
 169 |         _updateBaseRateAndGetRedemptionRate(totals.redeemedAmount, totals.boldSupplyAtStart);
 170 | 
 171 |         // Burn the total Bold that is cancelled with debt
 172 |         if (totals.redeemedAmount > 0) {
 173 |             boldToken.burn(msg.sender, totals.redeemedAmount);
 174 |         }
 175 |     }
 176 | 
 177 |     // --- Internal fee functions ---
 178 | 
 179 |     // Update the last fee operation time only if time passed >= decay interval. This prevents base rate griefing.
 180 |     function _updateLastFeeOpTime() internal {
 181 |         uint256 minutesPassed = _minutesPassedSinceLastFeeOp();
 182 | 
 183 |         if (minutesPassed > 0) {
 184 |             lastFeeOperationTime += ONE_MINUTE * minutesPassed;
 185 |             emit LastFeeOpTimeUpdated(lastFeeOperationTime);
 186 |         }
 187 |     }
 188 | 
 189 |     function _minutesPassedSinceLastFeeOp() internal view returns (uint256) {
 190 |         return (block.timestamp - lastFeeOperationTime) / ONE_MINUTE;
 191 |     }
 192 | 
 193 |     // Updates the `baseRate` state with math from `_getUpdatedBaseRateFromRedemption`
 194 |     function _updateBaseRateAndGetRedemptionRate(uint256 _boldAmount, uint256 _totalBoldSupplyAtStart) internal {
 195 |         uint256 newBaseRate = _getUpdatedBaseRateFromRedemption(_boldAmount, _totalBoldSupplyAtStart);
 196 | 
 197 |         //assert(newBaseRate <= DECIMAL_PRECISION); // This is already enforced in `_getUpdatedBaseRateFromRedemption`
 198 | 
 199 |         // Update the baseRate state variable
 200 |         baseRate = newBaseRate;
 201 |         emit BaseRateUpdated(newBaseRate);
 202 | 
 203 |         _updateLastFeeOpTime();
 204 |     }
 205 | 
 206 |     /*
 207 |      * This function calculates the new baseRate in the following way:
 208 |      * 1) decays the baseRate based on time passed since last redemption or Bold borrowing operation.
 209 |      * then,
 210 |      * 2) increases the baseRate based on the amount redeemed, as a proportion of total supply
 211 |      */
 212 |     function _getUpdatedBaseRateFromRedemption(uint256 _redeemAmount, uint256 _totalBoldSupply)
 213 |         internal
 214 |         view
 215 |         returns (uint256)
 216 |     {
 217 |         // decay the base rate
 218 |         uint256 decayedBaseRate = _calcDecayedBaseRate();
 219 | 
 220 |         // get the fraction of total supply that was redeemed
 221 |         uint256 redeemedBoldFraction = _redeemAmount * DECIMAL_PRECISION / _totalBoldSupply;
 222 | 
 223 |         uint256 newBaseRate = decayedBaseRate + redeemedBoldFraction / REDEMPTION_BETA;
 224 |         newBaseRate = LiquityMath._min(newBaseRate, DECIMAL_PRECISION); // cap baseRate at a maximum of 100%
 225 | 
 226 |         return newBaseRate;
 227 |     }
 228 | 
 229 |     function _calcDecayedBaseRate() internal view returns (uint256) {
 230 |         uint256 minutesPassed = _minutesPassedSinceLastFeeOp();
 231 |         uint256 decayFactor = LiquityMath._decPow(REDEMPTION_MINUTE_DECAY_FACTOR, minutesPassed);
 232 | 
 233 |         return baseRate * decayFactor / DECIMAL_PRECISION;
 234 |     }
 235 | 
 236 |     function _calcRedemptionRate(uint256 _baseRate) internal pure returns (uint256) {
 237 |         return LiquityMath._min(
 238 |             REDEMPTION_FEE_FLOOR + _baseRate,
 239 |             DECIMAL_PRECISION // cap at a maximum of 100%
 240 |         );
 241 |     }
 242 | 
 243 |     function _calcRedemptionFee(uint256 _redemptionRate, uint256 _amount) internal pure returns (uint256) {
 244 |         uint256 redemptionFee = _redemptionRate * _amount / DECIMAL_PRECISION;
 245 |         return redemptionFee;
 246 |     }
 247 | 
 248 |     // external redemption rate/fee getters
 249 | 
 250 |     function getRedemptionRate() external view override returns (uint256) {
 251 |         return _calcRedemptionRate(baseRate);
 252 |     }
 253 | 
 254 |     function getRedemptionRateWithDecay() public view override returns (uint256) {
 255 |         return _calcRedemptionRate(_calcDecayedBaseRate());
 256 |     }
 257 | 
 258 |     function getRedemptionRateForRedeemedAmount(uint256 _redeemAmount) external view returns (uint256) {
 259 |         uint256 totalBoldSupply = boldToken.totalSupply();
 260 |         uint256 newBaseRate = _getUpdatedBaseRateFromRedemption(_redeemAmount, totalBoldSupply);
 261 |         return _calcRedemptionRate(newBaseRate);
 262 |     }
 263 | 
 264 |     function getRedemptionFeeWithDecay(uint256 _ETHDrawn) external view override returns (uint256) {
 265 |         return _calcRedemptionFee(getRedemptionRateWithDecay(), _ETHDrawn);
 266 |     }
 267 | 
 268 |     function getEffectiveRedemptionFeeInBold(uint256 _redeemAmount) external view override returns (uint256) {
 269 |         uint256 totalBoldSupply = boldToken.totalSupply();
 270 |         uint256 newBaseRate = _getUpdatedBaseRateFromRedemption(_redeemAmount, totalBoldSupply);
 271 |         return _calcRedemptionFee(_calcRedemptionRate(newBaseRate), _redeemAmount);
 272 |     }
 273 | 
 274 |     // getters
 275 | 
 276 |     function getToken(uint256 _index) external view returns (IERC20Metadata) {
 277 |         if (_index == 0) return token0;
 278 |         else if (_index == 1) return token1;
 279 |         else if (_index == 2) return token2;
 280 |         else if (_index == 3) return token3;
 281 |         else if (_index == 4) return token4;
 282 |         else if (_index == 5) return token5;
 283 |         else if (_index == 6) return token6;
 284 |         else if (_index == 7) return token7;
 285 |         else if (_index == 8) return token8;
 286 |         else if (_index == 9) return token9;
 287 |         else revert("Invalid index");
 288 |     }
 289 | 
 290 |     function getTroveManager(uint256 _index) public view returns (ITroveManager) {
 291 |         if (_index == 0) return troveManager0;
 292 |         else if (_index == 1) return troveManager1;
 293 |         else if (_index == 2) return troveManager2;
 294 |         else if (_index == 3) return troveManager3;
 295 |         else if (_index == 4) return troveManager4;
 296 |         else if (_index == 5) return troveManager5;
 297 |         else if (_index == 6) return troveManager6;
 298 |         else if (_index == 7) return troveManager7;
 299 |         else if (_index == 8) return troveManager8;
 300 |         else if (_index == 9) return troveManager9;
 301 |         else revert("Invalid index");
 302 |     }
 303 | 
 304 |     // require functions
 305 | 
 306 |     function _requireValidMaxFeePercentage(uint256 _maxFeePercentage) internal pure {
 307 |         require(
 308 |             _maxFeePercentage >= REDEMPTION_FEE_FLOOR && _maxFeePercentage <= DECIMAL_PRECISION,
 309 |             "Max fee percentage must be between 0.5% and 100%"
 310 |         );
 311 |     }
 312 | 
 313 |     function _requireAmountGreaterThanZero(uint256 _amount) internal pure {
 314 |         require(_amount > 0, "CollateralRegistry: Amount must be greater than zero");
 315 |     }
 316 | }
 317 | 