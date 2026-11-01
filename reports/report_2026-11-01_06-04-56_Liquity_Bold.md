# Review /tmp/target/contracts/src/TroveManager.sol
Strategy: Liquity Bold - 125000 BOLD - FREE
Wallet: 0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40

Manual review needed.
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "./Interfaces/ITroveManager.sol";
   6 | import "./Interfaces/IAddressesRegistry.sol";
   7 | import "./Interfaces/IStabilityPool.sol";
   8 | import "./Interfaces/ICollSurplusPool.sol";
   9 | import "./Interfaces/IBoldToken.sol";
  10 | import "./Interfaces/ISortedTroves.sol";
  11 | import "./Interfaces/ITroveEvents.sol";
  12 | import "./Interfaces/ITroveNFT.sol";
  13 | import "./Interfaces/ICollateralRegistry.sol";
  14 | import "./Interfaces/IWETH.sol";
  15 | import "./Dependencies/LiquityBase.sol";
  16 | 
  17 | contract TroveManager is LiquityBase, ITroveManager, ITroveEvents {
  18 |     // --- Connected contract declarations ---
  19 | 
  20 |     ITroveNFT public troveNFT;
  21 |     IBorrowerOperations public borrowerOperations;
  22 |     IStabilityPool public stabilityPool;
  23 |     address internal gasPoolAddress;
  24 |     ICollSurplusPool internal collSurplusPool;
  25 |     IBoldToken internal boldToken;
  26 |     // A doubly linked list of Troves, sorted by their interest rate
  27 |     ISortedTroves public sortedTroves;
  28 |     ICollateralRegistry internal collateralRegistry;
  29 |     // Wrapped ETH for liquidation reserve (gas compensation)
  30 |     IWETH internal immutable WETH;
  31 | 
  32 |     // Critical system collateral ratio. If the system's total collateral ratio (TCR) falls below the CCR, some borrowing operation restrictions are applied
  33 |     uint256 public immutable CCR;
  34 | 
  35 |     // Minimum collateral ratio for individual troves
  36 |     uint256 internal immutable MCR;
  37 |     // Shutdown system collateral ratio. If the system's total collateral ratio (TCR) for a given collateral falls below the SCR,
  38 |     // the protocol triggers the shutdown of the borrow market and permanently disables all borrowing operations except for closing Troves.
  39 |     uint256 internal immutable SCR;
  40 | 
  41 |     // Liquidation penalty for troves offset to the SP
  42 |     uint256 internal immutable LIQUIDATION_PENALTY_SP;
  43 |     // Liquidation penalty for troves redistributed
  44 |     uint256 internal immutable LIQUIDATION_PENALTY_REDISTRIBUTION;
  45 | 
  46 |     // --- Data structures ---
  47 | 
  48 |     // Store the necessary data for a trove
  49 |     struct Trove {
  50 |         uint256 debt;
  51 |         uint256 coll;
  52 |         uint256 stake;
  53 |         Status status;
  54 |         uint64 arrayIndex;
  55 |         uint64 lastDebtUpdateTime;
  56 |         uint64 lastInterestRateAdjTime;
  57 |         uint256 annualInterestRate;
  58 |         address interestBatchManager;
  59 |         uint256 batchDebtShares;
  60 |     }
  61 | 
  62 |     mapping(uint256 => Trove) public Troves;
  63 | 
  64 |     // Store the necessary data for an interest batch manager. We treat each batch as a “big trove”.
  65 |     // Each trove has a share of the debt of the global batch. Collateral is stored per trove (as CRs are different)
  66 |     // Still the total amount of batch collateral is stored for informational purposes
  67 |     struct Batch {
  68 |         uint256 debt;
  69 |         uint256 coll;
  70 |         uint64 arrayIndex;
  71 |         uint64 lastDebtUpdateTime;
  72 |         uint64 lastInterestRateAdjTime;
  73 |         uint256 annualInterestRate;
  74 |         uint256 annualManagementFee;
  75 |         uint256 totalDebtShares;
  76 |     }
  77 | 
  78 |     mapping(address => Batch) internal batches;
  79 | 
  80 |     uint256 internal totalStakes;
  81 | 
  82 |     // Snapshot of the value of totalStakes, taken immediately after the latest liquidation
  83 |     uint256 internal totalStakesSnapshot;
  84 | 
  85 |     // Snapshot of the total collateral across the ActivePool and DefaultPool, immediately after the latest liquidation.
  86 |     uint256 internal totalCollateralSnapshot;
  87 | 
  88 |     /*
  89 |     * L_coll and L_boldDebt track the sums of accumulated liquidation rewards per unit staked. During its lifetime, each stake earns:
  90 |     *
  91 |     * An Coll gain of ( stake * [L_coll - L_coll(0)] )
  92 |     * A boldDebt increase  of ( stake * [L_boldDebt - L_boldDebt(0)] )
  93 |     *
  94 |     * Where L_coll(0) and L_boldDebt(0) are snapshots of L_coll and L_boldDebt for the active Trove taken at the instant the stake was made
  95 |     */
  96 |     uint256 internal L_coll;
  97 |     uint256 internal L_boldDebt;
  98 | 
  99 |     // Map active troves to their RewardSnapshot
 100 |     mapping(uint256 => RewardSnapshot) public rewardSnapshots;
 101 | 
 102 |     // Object containing the Coll and Bold snapshots for a given active trove
 103 |     struct RewardSnapshot {
 104 |         uint256 coll;
 105 |         uint256 boldDebt;
 106 |     }
 107 | 
 108 |     // Array of all active trove addresses - used to compute an approximate hint off-chain, for the sorted list in


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "./Interfaces/ITroveManager.sol";
   6 | import "./Interfaces/IAddressesRegistry.sol";
   7 | import "./Interfaces/IStabilityPool.sol";
   8 | import "./Interfaces/ICollSurplusPool.sol";
   9 | import "./Interfaces/IBoldToken.sol";
  10 | import "./Interfaces/ISortedTroves.sol";
  11 | import "./Interfaces/ITroveEvents.sol";
  12 | import "./Interfaces/ITroveNFT.sol";
  13 | import "./Interfaces/ICollateralRegistry.sol";
  14 | import "./Interfaces/IWETH.sol";
  15 | import "./Dependencies/LiquityBase.sol";
  16 | 
  17 | contract TroveManager is LiquityBase, ITroveManager, ITroveEvents {
  18 |     // --- Connected contract declarations ---
  19 | 
  20 |     ITroveNFT public troveNFT;
  21 |     IBorrowerOperations public borrowerOperations;
  22 |     IStabilityPool public stabilityPool;
  23 |     address internal gasPoolAddress;
  24 |     ICollSurplusPool internal collSurplusPool;
  25 |     IBoldToken internal boldToken;
  26 |     // A doubly linked list of Troves, sorted by their interest rate
  27 |     ISortedTroves public sortedTroves;
  28 |     ICollateralRegistry internal collateralRegistry;
  29 |     // Wrapped ETH for liquidation reserve (gas compensation)
  30 |     IWETH internal immutable WETH;
  31 | 
  32 |     // Critical system collateral ratio. If the system's total collateral ratio (TCR) falls below the CCR, some borrowing operation restrictions are applied
  33 |     uint256 public immutable CCR;
  34 | 
  35 |     // Minimum collateral ratio for individual troves
  36 |     uint256 internal immutable MCR;
  37 |     // Shutdown system collateral ratio. If the system's total collateral ratio (TCR) for a given collateral falls below the SCR,
  38 |     // the protocol triggers the shutdown of the borrow market and permanently disables all borrowing operations except for closing Troves.
  39 |     uint256 internal immutable SCR;
  40 | 
  41 |     // Liquidation penalty for troves offset to the SP
  42 |     uint256 internal immutable LIQUIDATION_PENALTY_SP;
  43 |     // Liquidation penalty for troves redistributed
  44 |     uint256 internal immutable LIQUIDATION_PENALTY_REDISTRIBUTION;
  45 | 
  46 |     // --- Data structures ---
  47 | 
  48 |     // Store the necessary data for a trove
  49 |     struct Trove {
  50 |         uint256 debt;
  51 |         uint256 coll;
  52 |         uint256 stake;
  53 |         Status status;
  54 |         uint64 arrayIndex;
  55 |         uint64 lastDebtUpdateTime;
  56 |         uint64 lastInterestRateAdjTime;
  57 |         uint256 annualInterestRate;
  58 |         address interestBatchManager;
  59 |         uint256 batchDebtShares;
  60 |     }
  61 | 
  62 |     mapping(uint256 => Trove) public Troves;
  63 | 
  64 |     // Store the necessary data for an interest batch manager. We treat each batch as a “big trove”.
  65 |     // Each trove has a share of the debt of the global batch. Collateral is stored per trove (as CRs are different)
  66 |     // Still the total amount of batch collateral is stored for informational purposes
  67 |     struct Batch {
  68 |         uint256 debt;
  69 |         uint256 coll;
  70 |         uint64 arrayIndex;
  71 |         uint64 lastDebtUpdateTime;
  72 |         uint64 lastInterestRateAdjTime;
  73 |         uint256 annualInterestRate;
  74 |         uint256 annualManagementFee;
  75 |         uint256 totalDebtShares;
  76 |     }
  77 | 
  78 |     mapping(address => Batch) internal batches;
  79 | 
  80 |     uint256 internal totalStakes;
  81 | 
  82 |     // Snapshot of the value of totalStakes, taken immediately after the latest liquidation
  83 |     uint256 internal totalStakesSnapshot;
  84 | 
  85 |     // Snapshot of the total collateral across the ActivePool and DefaultPool, immediately after the latest liquidation.
  86 |     uint256 internal totalCollateralSnapshot;
  87 | 
  88 |     /*
  89 |     * L_coll and L_boldDebt track the sums of accumulated liquidation rewards per unit staked. During its lifetime, each stake earns:
  90 |     *
  91 |     * An Coll gain of ( stake * [L_coll - L_coll(0)] )
  92 |     * A boldDebt increase  of ( stake * [L_boldDebt - L_boldDebt(0)] )
  93 |     *
  94 |     * Where L_coll(0) and L_boldDebt(0) are snapshots of L_coll and L_boldDebt for the active Trove taken at the instant the stake was made
  95 |     */
  96 |     uint256 internal L_coll;
  97 |     uint256 internal L_boldDebt;
  98 | 
  99 |     // Map active troves to their RewardSnapshot
 100 |     mapping(uint256 => RewardSnapshot) public rewardSnapshots;
 101 | 
 102 |     // Object containing the Coll and Bold snapshots for a given active trove
 103 |     struct RewardSnapshot {
 104 |         uint256 coll;
 105 |         uint256 boldDebt;
 106 |     }
 107 | 
 108 |     // Array of all active trove addresses - used to compute an approximate hint off-chain, for the sorted list insertion
 109 |     uint256[] internal TroveIds;
 110 |     // Array of all batch managers - used to fetch them off-chain
 111 |     address[] public batchIds;
 112 | 
 113 |     uint256 public lastZombieTroveId;
 114 | 
 115 |     // Error trackers for the trove redistribution calculation
 116 |     uint256 internal lastCollError_Redistribution;
 117 |     uint256 internal lastBoldDebtError_Redistribution;
 118 | 
 119 |     // Timestamp at which branch was shut down. 0 if not shut down.
 120 |     uint256 public shutdownTime;
 121 | 
 122 |     /*
 123 |     * --- Variable container structs for liquidations ---
 124 |     *
 125 |     * These structs are used to hold, return and assign variables inside the liquidation functions,
 126 |     * in order to avoid the error: "CompilerError: Stack too deep".
 127 |     **/
 128 | 
 129 |     struct LiquidationValues {
 130 |         uint256 collGasCompensation;
 131 |         uint256 debtToOffset;
 132 |         uint256 collToSendToSP;
 133 |         uint256 debtToRedistribute;
 134 |         uint256 collToRedistribute;
 135 |         uint256 collSurplus;
 136 |         uint256 ETHGasCompensation;
 137 |         uint256 oldWeightedRecordedDebt;
 138 |         uint256 newWeightedRecordedDebt;
 139 |     }
 140 | 
 141 |     // --- Variable container structs for redemptions ---
 142 | 
 143 |     struct RedeemCollateralValues {
 144 |         uint256 totalCollFee;
 145 |         uint256 remainingBold;
 146 |         address lastBatchUpdatedInterest;
 147 |         uint256 nextUserToCheck;
 148 |     }
 149 | 
 150 |     struct SingleRedemptionValues {
 151 |         uint256 troveId;
 152 |         address batchAddress;
 153 |         uint256 boldLot;
 154 |         uint256 collLot;
 155 |         uint256 collFee;
 156 |         uint256 appliedRedistBoldDebtGain;
 157 |         uint256 oldWeightedRecordedDebt;
 158 |         uint256 newWeightedRecordedDebt;
 159 |         uint256 newStake;
 160 |         bool isZombieTrove;
 161 |         LatestTroveData trove;
 162 |         LatestBatchData batch;
 163 |     }
 164 | 
 165 |     // --- Errors ---
 166 | 
 167 |     error EmptyData();
 168 |     error NothingToLiquidate();
 169 |     error CallerNotBorrowerOperations();
 170 |     error CallerNotCollateralRegistry();
 171 |     error OnlyOneTroveLeft();
 172 |     error NotShutDown();
 173 |     error ZeroAmount();
 174 |     error NotEnoughBoldBalance();
 175 |     error MinCollNotReached(uint256 _coll);
 176 |     error BatchSharesRatioTooHigh();
 177 | 
 178 |     // --- Events ---
 179 | 
 180 |     event TroveNFTAddressChanged(address _newTroveNFTAddress);
 181 |     event BorrowerOperationsAddressChanged(address _newBorrowerOperationsAddress);
 182 |     event BoldTokenAddressChanged(address _newBoldTokenAddress);
 183 |     event StabilityPoolAddressChanged(address _stabilityPoolAddress);
 184 |     event GasPoolAddressChanged(address _gasPoolAddress);
 185 |     event CollSurplusPoolAddressChanged(address _collSurplusPoolAddress);
 186 |     event SortedTrovesAddressChanged(address _sortedTrovesAddress);
 187 |     event CollateralRegistryAddressChanged(address _collateralRegistryAddress);
 188 | 
 189 |     constructor(IAddressesRegistry _addressesRegistry) LiquityBase(_addressesRegistry) {
 190 |         CCR = _addressesRegistry.CCR();
 191 |         MCR = _addressesRegistry.MCR();
 192 |         SCR = _addressesRegistry.SCR();
 193 |         LIQUIDATION_PENALTY_SP = _addressesRegistry.LIQUIDATION_PENALTY_SP();
 194 |         LIQUIDATION_PENALTY_REDISTRIBUTION = _addressesRegistry.LIQUIDATION_PENALTY_REDISTRIBUTION();
 195 | 
 196 |         troveNFT = _addressesRegistry.troveNFT();
 197 |         borrowerOperations = _addressesRegistry.borrowerOperations();
 198 |         stabilityPool = _addressesRegistry.stabilityPool();
 199 |         gasPoolAddress = _addressesRegistry.gasPoolAddress();
 200 |         collSurplusPool = _addressesRegistry.collSurplusPool();
 201 |         boldToken = _addressesRegistry.boldToken();
 202 |         sortedTroves = _addressesRegistry.sortedTroves();
 203 |         WETH = _addressesRegistry.WETH();
 204 |         collateralRegistry = _addressesRegistry.collateralRegistry();
 205 | 
 206 |         emit TroveNFTAddressChanged(address(troveNFT));
 207 |         emit BorrowerOperationsAddressChanged(address(borrowerOperations));
 208 |         emit StabilityPoolAddressChanged(address(stabilityPool));
 209 |         emit GasPoolAddressChanged(gasPoolAddress);
 210 |         emit CollSurplusPoolAddressChanged(address(collSurplusPool));
 211 |         emit BoldTokenAddressChanged(address(boldToken));
 212 |         emit SortedTrovesAddressChanged(address(sortedTroves));
 213 |         emit CollateralRegistryAddressChanged(address(collateralRegistry));
 214 |     }
 215 | 
 216 |     // --- Getters ---
 217 | 
 218 |     function getTroveIdsCount() external view override returns (uint256) {
 219 |         return TroveIds.length;
 220 |     }
 221 | 
 222 |     function getTroveFromTroveIdsArray(uint256 _index) external view override returns (uint256) {
 223 |         return TroveIds[_index];
 224 |     }
 225 | 
 226 |     // --- Trove Liquidation functions ---
 227 | 
 228 |     // --- Inner single liquidation functions ---
 229 | 
 230 |     // Liquidate one trove
 231 |     function _liquidate(
 232 |         IDefaultPool _defaultPool,
 233 |         uint256 _troveId,
 234 |         uint256 _boldInSPForOffsets,
 235 |         uint256 _price,
 236 |         LatestTroveData memory trove,
 237 |         LiquidationValues memory singleLiquidation
 238 |     ) internal {
 239 |         address owner = troveNFT.ownerOf(_troveId);
 240 | 
 241 |         _getLatestTroveData(_troveId, trove);
 242 |         address batchAddress = _getBatchManager(_troveId);
 243 |         bool isTroveInBatch = batchAddress != address(0);
 244 |         LatestBatchData memory batch;
 245 |         if (isTroveInBatch) _getLatestBatchData(batchAddress, batch);
 246 | 
 247 |         _movePendingTroveRewardsToActivePool(_defaultPool, trove.redistBoldDebtGain, trove.redistCollGain);
 248 | 
 249 |         (
 250 |             singleLiquidation.debtToOffset,
 251 |             singleLiquidation.collToSendToSP,
 252 |             singleLiquidation.collGasCompensation,
 253 |             singleLiquidation.debtToRedistribute,
 254 |             singleLiquidation.collToRedistribute,
 255 |             singleLiquidation.collSurplus
 256 |         ) = _getOffsetAndRedistributionVals(trove.entireDebt, trove.entireColl, _boldInSPForOffsets, _price);
 257 | 
 258 |         TroveChange memory troveChange;
 259 |         troveChange.collDecrease = trove.entireColl;
 260 |         troveChange.debtDecrease = trove.entireDebt;
 261 |         troveChange.appliedRedistCollGain = trove.redistCollGain;
 262 |         troveChange.appliedRedistBoldDebtGain = trove.redistBoldDebtGain;
 263 |         _closeTrove(
 264 |             _troveId,
 265 |             troveChange,
 266 |             batchAddress,
 267 |             batch.entireCollWithoutRedistribution,
 268 |             batch.entireDebtWithoutRedistribution,
 269 |             Status.closedByLiquidation
 270 |         );
 271 | 
 272 |         if (isTroveInBatch) {
 273 |             // the parenthesis in the old weighted term equals `recordedDebt + accruedInterest + accruedBatchManagementFee`
 274 |             // We want to capture last 2 ones, as the batch part only has recorded debt. The recorded debt of the trove is duplicated there,
 275 |             // but it needs to be, because it’s also included in `entireDebtWithoutRedistribution` in the next line.
 276 |             // So in the end we add it once and subtract it twice, which is the same as subtracting it once.
 277 |             singleLiquidation.oldWeightedRecordedDebt =
 278 |                 batch.weightedRecordedDebt + (trove.entireDebt - trove.redistBoldDebtGain) * batch.annualInterestRate;
 279 |             singleLiquidation.newWeightedRecordedDebt = batch.entireDebtWithoutRedistribution * batch.annualInterestRate;
 280 |             // Mint batch management fee
 281 |             troveChange.batchAccruedManagementFee = batch.accruedManagementFee;
 282 |             troveChange.oldWeightedRecordedBatchManagementFee = batch.weightedRecordedBatchManagementFee
 283 |                 + (trove.entireDebt - trove.redistBoldDebtGain) * batch.annualManagementFee;
 284 |             troveChange.newWeightedRecordedBatchManagementFee =
 285 |                 batch.entireDebtWithoutRedistribution * batch.annualManagementFee;
 286 |             activePool.mintBatchManagementFeeAndAccountForChange(troveChange, batchAddress);
 287 |         } else {
 288 |             singleLiquidation.oldWeightedRecordedDebt = trove.weightedRecordedDebt;
 289 |         }
 290 | 
 291 |         // Difference between liquidation penalty and liquidation threshold
 292 |         if (singleLiquidation.collSurplus > 0) {
 293 |             collSurplusPool.accountSurplus(owner, singleLiquidation.collSurplus);
 294 |         }
 295 | 
 296 |         // Wipe out state in BO
 297 |         borrowerOperations.onLiquidateTrove(_troveId);
 298 | 
 299 |         emit TroveUpdated({
 300 |             _troveId: _troveId,
 301 |             _debt: 0,
 302 |             _coll: 0,
 303 |             _stake: 0,
 304 |             _annualInterestRate: 0,
 305 |             _snapshotOfTotalCollRedist: 0,
 306 |             _snapshotOfTotalDebtRedist: 0
 307 |         });
 308 | 
 309 |         emit TroveOperation({
 310 |             _troveId: _troveId,
 311 |             _operation: Operation.liquidate,
 312 |             _annualInterestRate: 0,
 313 |             _debtIncreaseFromRedist: trove.redistBoldDebtGain,
 314 |             _debtIncreaseFromUpfrontFee: 0,
 315 |             _debtChangeFromOperation: -int256(trove.entireDebt),
 316 |             _collIncreaseFromRedist: trove.redistCollGain,
 317 |             _collChangeFromOperation: -int256(trove.entireColl)
 318 |         });
 319 | 
 320 |         if (isTroveInBatch) {
 321 |             emit BatchUpdated({
 322 |                 _interestBatchManager: batchAddress,
 323 |                 _operation: BatchOperation.exitBatch,
 324 |                 _debt: batches[batchAddress].debt,
 325 |                 _coll: batches[batchAddress].coll,
 326 |                 _annualInterestRate: batch.annualInterestRate,
 327 |                 _annualManagementFee: batch.annualManagementFee,
 328 |                 _totalDebtShares: batches[batchAddress].totalDebtShares,
 329 |                 _debtIncreaseFromUpfrontFee: 0
 330 |             });
 331 |         }
 332 |     }
 333 | 
 334 |     // Return the amount of Coll to be drawn from a trove's collateral and sent as gas compensation.
 335 |     function _getCollGasCompensation(uint256 _coll) internal pure returns (uint256) {
 336 |         // _entireDebt should never be zero, but we add the condition defensively to avoid an unexpected revert
 337 |         return LiquityMath._min(_coll / COLL_GAS_COMPENSATION_DIVISOR, COLL_GAS_COMPENSATION_CAP);
 338 |     }
 339 | 
 340 |     /* In a full liquidation, returns the values for a trove's coll and debt to be offset, and coll and debt to be
 341 |     * redistributed to active troves.
 342 |     */
 343 |     function _getOffsetAndRedistributionVals(
 344 |         uint256 _entireTroveDebt,
 345 |         uint256 _entireTroveColl,
 346 |         uint256 _boldInSPForOffsets,
 347 |         uint256 _price
 348 |     )
 349 |         internal
 350 |         view
 351 |         returns (
 352 |             uint256 debtToOffset,
 353 |             uint256 collToSendToSP,
 354 |             uint256 collGasCompensation,
 355 |             uint256 debtToRedistribute,
 356 |             uint256 collToRedistribute,
 357 |             uint256 collSurplus
 358 |         )
 359 |     {
 360 |         uint256 collSPPortion;
 361 |         /*
 362 |          * Offset as much debt & collateral as possible against the Stability Pool, and redistribute the remainder
 363 |          * between all active troves.
 364 |          *
 365 |          *  If the trove's debt is larger than the deposited Bold in the Stability Pool:
 366 |          *
 367 |          *  - Offset an amount of the trove's debt equal to the Bold in the Stability Pool
 368 |          *  - Send a fraction of the trove's collateral to the Stability Pool, equal to the fraction of its offset debt
 369 |          *
 370 |          */
 371 |         if (_boldInSPForOffsets > 0) {
 372 |             debtToOffset = LiquityMath._min(_entireTroveDebt, _boldInSPForOffsets);
 373 |             collSPPortion = _entireTroveColl * debtToOffset / _entireTroveDebt;
 374 | 
 375 |             collGasCompensation = _getCollGasCompensation(collSPPortion);
 376 |             uint256 collToOffset = collSPPortion - collGasCompensation;
 377 | 
 378 |             (collToSendToSP, collSurplus) =
 379 |                 _getCollPenaltyAndSurplus(collToOffset, debtToOffset, LIQUIDATION_PENALTY_SP, _price);
 380 |         }
 381 | 
 382 |         // Redistribution
 383 |         debtToRedistribute = _entireTroveDebt - debtToOffset;
 384 |         if (debtToRedistribute > 0) {
 385 |             uint256 collRedistributionPortion = _entireTroveColl - collSPPortion;
 386 |             if (collRedistributionPortion > 0) {
 387 |                 (collToRedistribute, collSurplus) = _getCollPenaltyAndSurplus(
 388 |                     collRedistributionPortion + collSurplus, // Coll surplus from offset can be eaten up by red. penalty
 389 |                     debtToRedistribute,
 390 |                     LIQUIDATION_PENALTY_REDISTRIBUTION, // _penaltyRatio
 391 |                     _price
 392 |                 );
 393 |             }
 394 |         }
 395 |         // assert(_collToLiquidate == collToSendToSP + collToRedistribute + collSurplus);
 396 |     }
 397 | 
 398 |     function _getCollPenaltyAndSurplus(
 399 |         uint256 _collToLiquidate,
 400 |         uint256 _debtToLiquidate,
 401 |         uint256 _penaltyRatio,
 402 |         uint256 _price
 403 |     ) internal pure returns (uint256 seizedColl, uint256 collSurplus) {
 404 |         uint256 maxSeizedColl = _debtToLiquidate * (DECIMAL_PRECISION + _penaltyRatio) / _price;
 405 |         if (_collToLiquidate > maxSeizedColl) {
 406 |             seizedColl = maxSeizedColl;
 407 |             collSurplus = _collToLiquidate - maxSeizedColl;
 408 |         } else {
 409 |             seizedColl = _collToLiquidate;
 410 |             collSurplus = 0;
 411 |         }
 412 |     }
 413 | 
 414 |     /*
 415 |      * Attempt to liquidate a custom list of troves provided by the caller.
 416 |      */
 417 |     function batchLiquidateTroves(uint256[] memory _troveArray) public override {
 418 |         if (_troveArray.length == 0) {
 419 |             revert EmptyData();
 420 