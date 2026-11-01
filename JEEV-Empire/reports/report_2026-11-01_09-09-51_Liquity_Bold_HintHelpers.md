Title: Missing disableInitializers in HintHelpers.sol
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
   5 | import "./Interfaces/ICollateralRegistry.sol";
   6 | import "./Dependencies/LiquityMath.sol";
   7 | import "./Dependencies/Constants.sol";
   8 | import "./Interfaces/IHintHelpers.sol";
   9 | 
  10 | contract HintHelpers is IHintHelpers {
  11 |     string public constant NAME = "HintHelpers";
  12 | 
  13 |     ICollateralRegistry public immutable collateralRegistry;
  14 | 
  15 |     constructor(ICollateralRegistry _collateralRegistry) {
  16 |         collateralRegistry = _collateralRegistry;
  17 |     }
  18 | 
  19 |     /* getApproxHint() - return id of a Trove that is, on average, (length / numTrials) positions away in the
  20 |     sortedTroves list from the correct insert position of the Trove to be inserted. 
  21 |     
  22 |     Note: The output id is worst-case O(n) positions away from the correct insert position, however, the function
  23 |     is probabilistic. Input can be tuned to guarantee results to a high degree of confidence, e.g:
  24 | 
  25 |     Submitting numTrials = k * sqrt(length), with k = 15 makes it very, very likely that the ouput id will
  26 |     be <= sqrt(length) positions away from the correct insert position.
  27 |     */
  28 |     function getApproxHint(uint256 _collIndex, uint256 _interestRate, uint256 _numTrials, uint256 _inputRandomSeed)
  29 |         external
  30 |         view
  31 |         returns (uint256 hintId, uint256 diff, uint256 latestRandomSeed)
  32 |     {
  33 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
  34 |         ISortedTroves sortedTroves = troveManager.sortedTroves();
  35 | 
  36 |         uint256 arrayLength = troveManager.getTroveIdsCount();
  37 | 
  38 |         if (arrayLength == 0) {
  39 |             return (0, 0, _inputRandomSeed);
  40 |         }
  41 | 
  42 |         hintId = sortedTroves.getLast();
  43 |         diff = LiquityMath._getAbsoluteDifference(_interestRate, troveManager.getTroveAnnualInterestRate(hintId));
  44 |         latestRandomSeed = _inputRandomSeed;
  45 | 
  46 |         for (uint256 i = 1; i < _numTrials; ++i) {
  47 |             latestRandomSeed = uint256(keccak256(abi.encodePacked(latestRandomSeed)));
  48 | 
  49 |             uint256 arrayIndex = latestRandomSeed % arrayLength;
  50 |             uint256 currentId = troveManager.getTroveFromTroveIdsArray(arrayIndex);
  51 | 
  52 |             // Skip this Trove if it's zombie and not in the sorted list
  53 |             if (!sortedTroves.contains(currentId)) continue;
  54 | 
  55 |             uint256 currentInterestRate = troveManager.getTroveAnnualInterestRate(currentId);
  56 | 
  57 |             // check if abs(current - IR) > abs(closest - IR), and update closest if current is closer
  58 |             uint256 currentDiff = LiquityMath._getAbsoluteDifference(currentInterestRate, _interestRate);
  59 | 
  60 |             if (currentDiff < diff) {
  61 |                 diff = currentDiff;
  62 |                 hintId = currentId;
  63 |             }
  64 |         }
  65 |     }
  66 | 
  67 |     function _calcUpfrontFee(uint256 _debt, uint256 _avgInterestRate) internal pure returns (uint256) {
  68 |         return _debt * _avgInterestRate * UPFRONT_INTEREST_PERIOD / ONE_YEAR / DECIMAL_PRECISION;
  69 |     }
  70 | 
  71 |     function predictOpenTroveUpfrontFee(uint256 _collIndex, uint256 _borrowedAmount, uint256 _interestRate)
  72 |         external
  73 |         view
  74 |         returns (uint256)
  75 |     {
  76 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
  77 |         IActivePool activePool = troveManager.activePool();
  78 | 
  79 |         TroveChange memory openTrove;
  80 |         openTrove.debtIncrease = _borrowedAmount;
  81 |         openTrove.newWeightedRecordedDebt = openTrove.debtIncrease * _interestRate;
  82 | 
  83 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(openTrove);
  84 |         return _calcUpfrontFee(openTrove.debtIncrease, avgInterestRate);
  85 |     }
  86 | 
  87 |     function predictAdjustInterestRateUpfrontFee(uint256 _collIndex, uint256 _troveId, uint256 _newInterestRate)
  88 |         external
  89 |         view
  90 |         returns (uint256)
  91 |     {
  92 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
  93 |         IActivePool activePool = troveManager.activePool();
  94 |         LatestTroveData memory trove = troveManager.getLatestTroveData(_troveId);
  95 | 
  96 |         if (
  97 |             _newInterestRate == trove.annualInterestRate
  98 |                 || block.timestamp >= trove.lastInterestRateAdjTime + INTEREST_RATE_ADJ_COOLDOWN
  99 |         ) {
 100 |             return 0;
 101 |         }
 102 | 
 103 |         return _predictAdjustInterestRateUpfrontFee(activePool, trove, _newInterestRate);
 104 |     }
 105 | 
 106 |     function forcePredictAdjustInterestRateUpfrontFee(uint256 _collIndex, uint256 _troveId, uint256 _newInterestRate)
 107 |         external
 108 |         view
 109 |         returns (uint256)
 110 |     {
 111 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 112 |         IActivePool activePool = troveManager.activePool();
 113 |         LatestTroveData memory trove = troveManager.getLatestTroveData(_troveId);
 114 | 
 115 |         return _predictAdjustInterestRateUpfrontFee(activePool, trove, _newInterestRate);
 116 |     }
 117 | 
 118 |     function _predictAdjustInterestRateUpfrontFee(
 119 |         IActivePool _activePool,
 120 |         LatestTroveData memory _trove,
 121 |         uint256 _newInterestRate
 122 |     ) internal view returns (uint256) {
 123 |         TroveChange memory troveChange;
 124 |         troveChange.appliedRedistBoldDebtGain = _trove.redistBoldDebtGain;
 125 |         troveChange.newWeightedRecordedDebt = _trove.entireDebt * _newInterestRate;
 126 |         troveChange.oldWeightedRecordedDebt = _trove.weightedRecordedDebt;
 127 | 
 128 |         uint256 avgInterestRate = _activePool.getNewApproxAvgInterestRateFromTroveChange(troveChange);
 129 |         return _calcUpfrontFee(_trove.entireDebt, avgInterestRate);
 130 |     }
 131 | 
 132 |     function predictAdjustTroveUpfrontFee(uint256 _collIndex, uint256 _troveId, uint256 _debtIncrease)
 133 |         external
 134 |         view
 135 |         returns (uint256)
 136 |     {
 137 |         if (_debtIncrease == 0) return 0;
 138 | 
 139 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 140 |         IActivePool activePool = troveManager.activePool();
 141 |         LatestTroveData memory trove = troveManager.getLatestTroveData(_troveId);
 142 |         (,,,,,,,, address batchManager,) = troveManager.Troves(_troveId);
 143 | 
 144 |         TroveChange memory troveChange;
 145 |         troveChange.appliedRedistBoldDebtGain = trove.redistBoldDebtGain;
 146 |         troveChange.debtIncrease = _debtIncrease;
 147 | 
 148 |         if (batchManager == address(0)) {
 149 |             troveChange.newWeightedRecordedDebt = (trove.entireDebt + _debtIncrease) * trove.annualInterestRate;
 150 |             troveChange.oldWeightedRecordedDebt = trove.weightedRecordedDebt;
 151 |         } else {
 152 |             LatestBatchData memory batch = troveManager.getLatestBatchData(batchManager);
 153 |             troveChange.batchAccruedManagementFee = batch.accruedManagementFee;
 154 |             troveChange.newWeightedRecordedDebt = (
 155 |                 batch.entireDebtWithoutRedistribution + trove.redistBoldDebtGain + _debtIncrease
 156 |             ) * batch.annualInterestRate;
 157 |             troveChange.oldWeightedRecordedDebt = batch.weightedRecordedDebt;
 158 |         }
 159 | 
 160 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(troveChange);
 161 |         return _calcUpfrontFee(_debtIncrease, avgInterestRate);
 162 |     }
 163 | 
 164 |     function predictAdjustBatchInterestRateUpfrontFee(
 165 |         uint256 _collIndex,
 166 |         address _batchAddress,
 167 |         uint256 _newInterestRate
 168 |     ) external view returns (uint256) {
 169 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 170 |         IActivePool activePool = troveManager.activePool();
 171 |         LatestBatchData memory batch = troveManager.getLatestBatchData(_batchAddress);
 172 | 
 173 |         if (
 174 |             _newInterestRate == batch.annualInterestRate
 175 |                 || block.timestamp >= batch.lastInterestRateAdjTime + INTEREST_RATE_ADJ_COOLDOWN
 176 |         ) {
 177 |             return 0;
 178 |         }
 179 | 
 180 |         TroveChange memory troveChange;
 181 |         troveChange.batchAccruedManagementFee = batch.accruedManagementFee;
 182 |         troveChange.newWeightedRecordedDebt = batch.entireDebtWithoutRedistribution * _newInterestRate;
 183 |         troveChange.oldWeightedRecordedDebt = batch.weightedRecordedDebt;
 184 | 
 185 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(troveChange);
 186 |         return _calcUpfrontFee(batch.entireDebtWithoutRedistribution, avgInterestRate);
 187 |     }
 188 | 
 189 |     function predictOpenTroveAndJoinBatchUpfrontFee(uint256 _collIndex, uint256 _borrowedAmount, address _batchAddress)
 190 |         external
 191 |         view
 192 |         returns (uint256)
 193 |     {
 194 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 195 |         IActivePool activePool = troveManager.activePool();
 196 |         LatestBatchData memory batch = troveManager.getLatestBatchData(_batchAddress);
 197 | 
 198 |         TroveChange memory openTrove;
 199 |         openTrove.debtIncrease = _borrowedAmount;
 200 |         openTrove.batchAccruedManagementFee = batch.accruedManagementFee;
 201 |         openTrove.oldWeightedRecordedDebt = batch.weightedRecordedDebt;
 202 |         openTrove.newWeightedRecordedDebt =
 203 |             (batch.entireDebtWithoutRedistribution + _borrowedAmount) * batch.annualInterestRate;
 204 | 
 205 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(openTrove);
 206 |         return _calcUpfrontFee(_borrowedAmount, avgInterestRate);
 207 |     }
 208 | 
 209 |     function predictJoinBatchInterestRateUpfrontFee(uint256 _collIndex, uint256 _troveId, address _batchAddress)
 210 |         external
 211 |         view
 212 |         returns (uint256)
 213 |     {
 214 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 215 |         IActivePool activePool = troveManager.activePool();
 216 |         LatestTroveData memory trove = troveManager.getLatestTroveData(_troveId);
 217 |         LatestBatchData memory batch = troveManager.getLatestBatchData(_batchAddress);
 218 | 
 219 |         TroveChange memory newBatchTroveChange;
 220 |         newBatchTroveChange.appliedRedistBoldDebtGain = trove.redistBoldDebtGain;
 221 |         newBatchTroveChange.batchAccruedManagementFee = batch.accruedManagementFee;
 222 |         newBatchTroveChange.oldWeightedRecordedDebt = batch.weightedRecordedDebt + trove.weightedRecordedDebt;
 223 |         newBatchTroveChange.newWeightedRecordedDebt =
 224 |             (batch.entireDebtWithoutRedistribution + trove.entireDebt) * batch.annualInterestRate;
 225 | 
 226 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(newBatchTroveChange);
 227 |         return _calcUpfrontFee(trove.entireDebt, avgInterestRate);
 228 |     }
 229 | 
 230 |     function predictRemoveFromBatchUpfrontFee(uint256 _collIndex, uint256 _troveId, uint256 _newInterestRate)
 231 |         external
 232 |         view
 233 |         returns (uint256)
 234 |     {
 235 |         ITroveManager troveManager = collateralRegistry.getTroveManager(_collIndex);
 236 |         IActivePool activePool = troveManager.activePool();
 237 |         LatestTroveData memory trove = troveManager.getLatestTroveData(_troveId);
 238 |         (,,,,,,,, address batchManager,) = troveManager.Troves(_troveId);
 239 |         LatestBatchData memory batch = troveManager.getLatestBatchData(batchManager);
 240 | 
 241 |         if (
 242 |             _newInterestRate == batch.annualInterestRate
 243 |                 || block.timestamp >= trove.lastInterestRateAdjTime + INTEREST_RATE_ADJ_COOLDOWN
 244 |         ) {
 245 |             return 0;
 246 |         }
 247 | 
 248 |         TroveChange memory troveChange;
 249 |         troveChange.appliedRedistBoldDebtGain = trove.redistBoldDebtGain;
 250 |         troveChange.batchAccruedManagementFee = batch.accruedManagementFee;
 251 |         troveChange.oldWeightedRecordedDebt = batch.weightedRecordedDebt;
 252 |         troveChange.newWeightedRecordedDebt = (
 253 |             batch.entireDebtWithoutRedistribution - (trove.entireDebt - trove.redistBoldDebtGain)
 254 |         ) * batch.annualInterestRate + trove.entireDebt * _newInterestRate;
 255 | 
 256 |         uint256 avgInterestRate = activePool.getNewApproxAvgInterestRateFromTroveChange(troveChange);
 257 |         return _calcUpfrontFee(trove.entireDebt, avgInterestRate);
 258 |     }
 259 | }
 260 | 