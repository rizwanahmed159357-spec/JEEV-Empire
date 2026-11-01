Title: Missing check in ActivePool.sol
Severity: High
Risk: Funds at risk due to missing validation
Description: At Line 41 abstract contract. At Line 58 struct.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "openzeppelin-contracts/contracts/token/ERC20/utils/SafeERC20.sol";
   6 | import "openzeppelin-contracts/contracts/utils/math/Math.sol";
   7 | 
   8 | import "./Dependencies/Constants.sol";
   9 | import "./Interfaces/IActivePool.sol";
  10 | import "./Interfaces/IAddressesRegistry.sol";
  11 | import "./Interfaces/IBoldToken.sol";
  12 | import "./Interfaces/IInterestRouter.sol";
  13 | import "./Interfaces/IDefaultPool.sol";
  14 | 
  15 | /*
  16 |  * The Active Pool holds the collateral and Bold debt (but not Bold tokens) for all active troves.
  17 |  *
  18 |  * When a trove is liquidated, it's Coll and Bold debt are transferred from the Active Pool, to either the
  19 |  * Stability Pool, the Default Pool, or both, depending on the liquidation conditions.
  20 |  *
  21 |  */
  22 | contract ActivePool is IActivePool {
  23 |     using SafeERC20 for IERC20;
  24 | 
  25 |     string public constant NAME = "ActivePool";
  26 | 
  27 |     IERC20 public immutable collToken;
  28 |     address public immutable borrowerOperationsAddress;
  29 |     address public immutable troveManagerAddress;
  30 |     address public immutable defaultPoolAddress;
  31 | 
  32 |     IBoldToken public immutable boldToken;
  33 | 
  34 |     IInterestRouter public immutable interestRouter;
  35 |     IBoldRewardsReceiver public immutable stabilityPool;
  36 | 
  37 |     uint256 internal collBalance; // deposited coll tracker
  38 | 
  39 |     // Aggregate recorded debt tracker. Updated whenever a Trove's debt is touched AND whenever the aggregate pending interest is minted.
  40 |     // "D" in the spec.
  41 |     uint256 public aggRecordedDebt;
  42 | 
  43 |     /* Sum of individual recorded Trove debts weighted by their respective chosen interest rates.
  44 |     * Updated at individual Trove operations.
  45 |     * "S" in the spec.
  46 |     */
  47 |     uint256 public aggWeightedDebtSum;
  48 | 
  49 |     // Last time at which the aggregate recorded debt and weighted sum were updated
  50 |     uint256 public lastAggUpdateTime;
  51 | 
  52 |     // Timestamp at which branch was shut down. 0 if not shut down.
  53 |     uint256 public shutdownTime;
  54 | 
  55 |     // Aggregate batch fees tracker
  56 |     uint256 public aggBatchManagementFees;
  57 |     /* Sum of individual recorded Trove debts weighted by their respective batch management fees
  58 |      * Updated at individual batched Trove operations.
  59 |      */
  60 |     uint256 public aggWeightedBatchManagementFeeSum;
  61 |     // Last time at which the aggregate batch fees and weighted sum were updated
  62 |     uint256 public lastAggBatchManagementFeesUpdateTime;
  63 | 
  64 |     // --- Events ---
  65 | 
  66 |     event CollTokenAddressChanged(address _newCollTokenAddress);
  67 |     event BorrowerOperationsAddressChanged(address _newBorrowerOperationsAddress);
  68 |     event TroveManagerAddressChanged(address _newTroveManagerAddress);
  69 |     event DefaultPoolAddressChanged(address _newDefaultPoolAddress);
  70 |     event StabilityPoolAddressChanged(address _newStabilityPoolAddress);
  71 |     event ActivePoolBoldDebtUpdated(uint256 _recordedDebtSum);
  72 |     event ActivePoolCollBalanceUpdated(uint256 _collBalance);
  73 | 
  74 |     constructor(IAddressesRegistry _addressesRegistry) {
  75 |         collToken = _addressesRegistry.collToken();
  76 |         borrowerOperationsAddress = address(_addressesRegistry.borrowerOperations());
  77 |         troveManagerAddress = address(_addressesRegistry.troveManager());
  78 |         stabilityPool = IBoldRewardsReceiver(_addressesRegistry.stabilityPool());
  79 |         defaultPoolAddress = address(_addressesRegistry.defaultPool());
  80 |         interestRouter = _addressesRegistry.interestRouter();
  81 |         boldToken = _addressesRegistry.boldToken();
  82 | 
  83 |         emit CollTokenAddressChanged(address(collToken));
  84 |         emit BorrowerOperationsAddressChanged(borrowerOperationsAddress);
  85 |         emit TroveManagerAddressChanged(troveManagerAddress);
  86 |         emit StabilityPoolAddressChanged(address(stabilityPool));
  87 |         emit DefaultPoolAddressChanged(defaultPoolAddress);
  88 | 
  89 |         // Allow funds movements between Liquity contracts
  90 |         collToken.approve(defaultPoolAddress, type(uint256).max);
  91 |     }
  92 | 
  93 |     // --- Getters for public variables. Required by IPool interface ---
  94 | 
  95 |     /*
  96 |     * Returns the Coll state variable.
  97 |     *
  98 |     *Not necessarily equal to the the contract's raw Coll balance - ether can be forcibly sent to contracts.
  99 |     */
 100 |     function getCollBalance() external view override returns (uint256) {
 101 |         return collBalance;
 102 |     }
 103 | 
 104 |     function calcPendingAggInterest() public view returns (uint256) {
 105 |         if (shutdownTime != 0) return 0;
 106 | 
 107 |         // We use the ceiling of the division here to ensure positive error, while we use regular floor division
 108 |         // when calculating the interest accrued by individual Troves.
 109 |         // This ensures that `system debt >= sum(trove debt)` always holds, and thus system debt won't turn negative
 110 |         // even if all Trove debt is repaid. The difference should be small and it should scale with the number of
 111 |         // interest minting events.
 112 |         return Math.ceilDiv(aggWeightedDebtSum * (block.timestamp - lastAggUpdateTime), ONE_YEAR * DECIMAL_PRECISION);
 113 |     }
 114 | 
 115 |     function calcPendingSPYield() external view returns (uint256) {
 116 |         return calcPendingAggInterest() * SP_YIELD_SPLIT / DECIMAL_PRECISION;
 117 |     }
 118 | 
 119 |     function calcPendingAggBatchManagementFee() public view returns (uint256) {
 120 |         uint256 periodEnd = shutdownTime != 0 ? shutdownTime : block.timestamp;
 121 |         uint256 periodStart = Math.min(lastAggBatchManagementFeesUpdateTime, periodEnd);
 122 | 
 123 |         return Math.ceilDiv(aggWeightedBatchManagementFeeSum * (periodEnd - periodStart), ONE_YEAR * DECIMAL_PRECISION);
 124 |     }
 125 | 
 126 |     function getNewApproxAvgInterestRateFromTroveChange(TroveChange calldata _troveChange)
 127 |         external
 128 |         view
 129 |         returns (uint256)
 130 |     {
 131 |         // We are ignoring the upfront fee when calculating the approx. avg. interest rate.
 132 |         // This is a simple way to resolve the circularity in:
 133 |         //   fee depends on avg. interest rate -> avg. interest rate is weighted by debt -> debt includes fee -> ...
 134 |         assert(_troveChange.upfrontFee == 0);
 135 | 
 136 |         if (shutdownTime != 0) return 0;
 137 | 
 138 |         uint256 newAggRecordedDebt = aggRecordedDebt;
 139 |         newAggRecordedDebt += calcPendingAggInterest();
 140 |         newAggRecordedDebt += _troveChange.appliedRedistBoldDebtGain;
 141 |         newAggRecordedDebt += _troveChange.debtIncrease;
 142 |         newAggRecordedDebt += _troveChange.batchAccruedManagementFee;
 143 |         newAggRecordedDebt -= _troveChange.debtDecrease;
 144 | 
 145 |         uint256 newAggWeightedDebtSum = aggWeightedDebtSum;
 146 |         newAggWeightedDebtSum += _troveChange.newWeightedRecordedDebt;
 147 |         newAggWeightedDebtSum -= _troveChange.oldWeightedRecordedDebt;
 148 | 
 149 |         // Avoid division by 0 if the first ever borrower tries to borrow 0 BOLD
 150 |         // Borrowing 0 BOLD is not allowed, but our check of debt >= MIN_DEBT happens _after_ calculating the upfront
 151 |         // fee, which involves getting the new approx. avg. interest rate
 152 |         return newAggRecordedDebt > 0 ? newAggWeightedDebtSum / newAggRecordedDebt : 0;
 153 |     }
 154 | 
 155 |     // Returns sum of agg.recorded debt plus agg. pending interest. Excludes pending redist. gains.
 156 |     function getBoldDebt() external view returns (uint256) {
 157 |         return aggRecordedDebt + calcPendingAggInterest() + aggBatchManagementFees + calcPendingAggBatchManagementFee();
 158 |     }
 159 | 
 160 |     // --- Pool functionality ---
 161 | 
 162 |     function sendColl(address _account, uint256 _amount) external override {
 163 |         _requireCallerIsBOorTroveMorSP();
 164 | 
 165 |         _accountForSendColl(_amount);
 166 | 
 167 |         collToken.safeTransfer(_account, _amount);
 168 |     }
 169 | 
 170 |     function sendCollToDefaultPool(uint256 _amount) external override {
 171 |         _requireCallerIsTroveManager();
 172 | 
 173 |         _accountForSendColl(_amount);
 174 | 
 175 |         IDefaultPool(defaultPoolAddress).receiveColl(_amount);
 176 |     }
 177 | 
 178 |     function _accountForSendColl(uint256 _amount) internal {
 179 |         uint256 newCollBalance = collBalance - _amount;
 180 |         collBalance = newCollBalance;
 181 |         emit ActivePoolCollBalanceUpdated(newCollBalance);
 182 |     }
 183 | 
 184 |     function receiveColl(uint256 _amount) external {
 185 |         _requireCallerIsBorrowerOperationsOrDefaultPool();
 186 | 
 187 |         _accountForReceivedColl(_amount);
 188 | 
 189 |         // Pull Coll tokens from sender
 190 |         collToken.safeTransferFrom(msg.sender, address(this), _amount);
 191 |     }
 192 | 
 193 |     function accountForReceivedColl(uint256 _amount) public {
 194 |         _requireCallerIsBorrowerOperationsOrDefaultPool();
 195 | 
 196 |         _accountForReceivedColl(_amount);
 197 |     }
 198 | 
 199 |     function _accountForReceivedColl(uint256 _amount) internal {
 200 |         uint256 newCollBalance = collBalance + _amount;
 201 |         collBalance = newCollBalance;
 202 | 
 203 |         emit ActivePoolCollBalanceUpdated(newCollBalance);
 204 |     }
 205 | 
 206 |     // --- Aggregate interest operations ---
 207 | 
 208 |     // This function is called inside all state-changing user ops: borrower ops, liquidations, redemptions and SP deposits/withdrawals.
 209 |     // Some user ops trigger debt changes to Trove(s), in which case _troveDebtChange will be non-zero.
 210 |     // The aggregate recorded debt is incremented by the aggregate pending interest, plus the net Trove debt change.
 211 |     // The net Trove debt change consists of the sum of a) any debt issued/repaid and b) any redistribution debt gain applied in the encapsulating operation.
 212 |     // It does *not* include the Trove's individual accrued interest - this gets accounted for in the aggregate accrued interest.
 213 |     // The net Trove debt change could be positive or negative in a repayment (depending on whether its redistribution gain or repayment amount is larger),
 214 |     // so this function accepts both the increase and the decrease to avoid using (and converting to/from) signed ints.
 215 |     function mintAggInterestAndAccountForTroveChange(TroveChange calldata _troveChange, address _batchAddress)
 216 |         external
 217 |     {
 218 |         _requireCallerIsBOorTroveM();
 219 | 
 220 |         // Batch management fees
 221 |         if (_batchAddress != address(0)) {
 222 |             _mintBatchManagementFeeAndAccountForChange(_troveChange, _batchAddress);
 223 |         }
 224 | 
 225 |         // Do the arithmetic in 2 steps here to avoid underflow from the decrease
 226 |         uint256 newAggRecordedDebt = aggRecordedDebt; // 1 SLOAD
 227 |         newAggRecordedDebt += _mintAggInterest(_troveChange.upfrontFee); // adds minted agg. interest + upfront fee
 228 |         newAggRecordedDebt += _troveChange.appliedRedistBoldDebtGain;
 229 |         newAggRecordedDebt += _troveChange.debtIncrease;
 230 |         newAggRecordedDebt -= _troveChange.debtDecrease;
 231 |         aggRecordedDebt = newAggRecordedDebt; // 1 SSTORE
 232 | 
 233 |         // assert(aggRecordedDebt >= 0) // This should never be negative. If all redistribution gians and all aggregate interest was applied
 234 |         // and all Trove debts were repaid, it should become 0.
 235 | 
 236 |         // Do the arithmetic in 2 steps here to avoid underflow from the decrease
 237 |         uint256 newAggWeightedDebtSum = aggWeightedDebtSum; // 1 SLOAD
 238 |         newAggWeightedDebtSum += _troveChange.newWeightedRecordedDebt;
 239 |         newAggWeightedDebtSum -= _troveChange.oldWeightedRecordedDebt;
 240 |         aggWeightedDebtSum = newAggWeightedDebtSum; // 1 SSTORE
 241 |     }
 242 | 
 243 |     function mintAggInterest() external override {
 244 |         _requireCallerIsBOorSP();
 245 |         aggRecordedDebt += _mintAggInterest(0);
 246 |     }
 247 | 
 248 |     function _mintAggInterest(uint256 _upfrontFee) internal returns (uint256 mintedAmount) {
 249 |         mintedAmount = calcPendingAggInterest() + _upfrontFee;
 250 | 
 251 |         // Mint part of the BOLD interest to the SP and part to the router for LPs.
 252 |         if (mintedAmount > 0) {
 253 |             uint256 spYield = SP_YIELD_SPLIT * mintedAmount / DECIMAL_PRECISION;
 254 |             uint256 remainderToLPs = mintedAmount - spYield;
 255 | 
 256 |             boldToken.mint(address(interestRouter), remainderToLPs);
 257 | 
 258 |             if (spYield > 0) {
 259 |                 boldToken.mint(address(stabilityPool), spYield);
 260 |                 stabilityPool.triggerBoldRewards(spYield);
 261 |             }
 262 |         }
 263 | 
 264 |         lastAggUpdateTime = block.timestamp;
 265 |     }
 266 | 
 267 |     function mintBatchManagementFeeAndAccountForChange(TroveChange calldata _troveChange, address _batchAddress)
 268 |         external
 269 |         override
 270 |     {
 271 |         _requireCallerIsTroveManager();
 272 |         _mintBatchManagementFeeAndAccountForChange(_troveChange, _batchAddress);
 273 |     }
 274 | 
 275 |     function _mintBatchManagementFeeAndAccountForChange(TroveChange memory _troveChange, address _batchAddress)
 276 |         internal
 277 |     {
 278 |         aggRecordedDebt += _troveChange.batchAccruedManagementFee;
 279 | 
 280 |         // Do the arithmetic in 2 steps here to avoid underflow from the decrease
 281 |         uint256 newAggBatchManagementFees = aggBatchManagementFees; // 1 SLOAD
 282 |         newAggBatchManagementFees += calcPendingAggBatchManagementFee();
 283 |         newAggBatchManagementFees -= _troveChange.batchAccruedManagementFee;
 284 |         aggBatchManagementFees = newAggBatchManagementFees; // 1 SSTORE
 285 | 
 286 |         // Do the arithmetic in 2 steps here to avoid underflow from the decrease
 287 |         uint256 newAggWeightedBatchManagementFeeSum = aggWeightedBatchManagementFeeSum; // 1 SLOAD
 288 |         newAggWeightedBatchManagementFeeSum += _troveChange.newWeightedRecordedBatchManagementFee;
 289 |         newAggWeightedBatchManagementFeeSum -= _troveChange.oldWeightedRecordedBatchManagementFee;
 290 |         aggWeightedBatchManagementFeeSum = newAggWeightedBatchManagementFeeSum; // 1 SSTORE
 291 | 
 292 |         // mint fee to batch address
 293 |         if (_troveChange.batchAccruedManagementFee > 0) {
 294 |             boldToken.mint(_batchAddress, _troveChange.batchAccruedManagementFee);
 295 |         }
 296 | 
 297 |         lastAggBatchManagementFeesUpdateTime = block.timestamp;
 298 |     }
 299 | 
 300 |     // --- Shutdown ---
 301 | 
 302 |     function setShutdownFlag() external {
 303 |         _requireCallerIsTroveManager();
 304 |         shutdownTime = block.timestamp;
 305 |     }
 306 | 
 307 |     function hasBeenShutDown() external view returns (bool) {
 308 |         return shutdownTime != 0;
 309 |     }
 310 | 
 311 |     // --- 'require' functions ---
 312 | 
 313 |     function _requireCallerIsBorrowerOperationsOrDefaultPool() internal view {
 314 |         require(
 315 |             msg.sender == borrowerOperationsAddress || msg.sender == defaultPoolAddress,
 316 |             "ActivePool: Caller is neither BO nor Default Pool"
 317 |         );
 318 |     }
 319 | 
 320 |     function _requireCallerIsBOorTroveMorSP() internal view {
 321 |         require(
 322 |             msg.sender == borrowerOperationsAddress || msg.sender == troveManagerAddress
 323 |                 || msg.sender == address(stabilityPool),
 324 |             "ActivePool: Caller is neither BorrowerOperations nor TroveManager nor StabilityPool"
 325 |         );
 326 |     }
 327 | 
 328 |     function _requireCallerIsBOorSP() internal view {
 329 |         require(
 330 |             msg.sender == borrowerOperationsAddress || msg.sender == address(stabilityPool),
 331 |             "ActivePool: Caller is not BorrowerOperations nor StabilityPool"
 332 |         );
 333 |     }
 334 | 
 335 |     function _requireCallerIsBOorTroveM() internal view {
 336 |         require(
 337 |             msg.sender == borrowerOperationsAddress || msg.sender == troveManagerAddress,
 338 |             "ActivePool: Caller is neither BorrowerOperations nor TroveManager"
 339 |         );
 340 |     }
 341 | 
 342 |     function _requireCallerIsTroveManager() internal view {
 343 |         require(msg.sender == troveManagerAddress, "ActivePool: Caller is not TroveManager");
 344 |     }
 345 | }
 346 | 