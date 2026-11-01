Title: Missing check in BorrowerOperations.sol
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
   6 | 
   7 | import "./Interfaces/IBorrowerOperations.sol";
   8 | import "./Interfaces/IAddressesRegistry.sol";
   9 | import "./Interfaces/ITroveManager.sol";
  10 | import "./Interfaces/IBoldToken.sol";
  11 | import "./Interfaces/ICollSurplusPool.sol";
  12 | import "./Interfaces/ISortedTroves.sol";
  13 | import "./Dependencies/LiquityBase.sol";
  14 | import "./Dependencies/AddRemoveManagers.sol";
  15 | import "./Types/LatestTroveData.sol";
  16 | import "./Types/LatestBatchData.sol";
  17 | 
  18 | contract BorrowerOperations is LiquityBase, AddRemoveManagers, IBorrowerOperations {
  19 |     using SafeERC20 for IERC20;
  20 | 
  21 |     // --- Connected contract declarations ---
  22 | 
  23 |     IERC20 internal immutable collToken;
  24 |     ITroveManager internal troveManager;
  25 |     address internal gasPoolAddress;
  26 |     ICollSurplusPool internal collSurplusPool;
  27 |     IBoldToken internal boldToken;
  28 |     // A doubly linked list of Troves, sorted by their collateral ratios
  29 |     ISortedTroves internal sortedTroves;
  30 |     // Wrapped ETH for liquidation reserve (gas compensation)
  31 |     IWETH internal immutable WETH;
  32 | 
  33 |     // Critical system collateral ratio. If the system's total collateral ratio (TCR) falls below the CCR, some borrowing operation restrictions are applied
  34 |     uint256 public immutable CCR;
  35 | 
  36 |     // Shutdown system collateral ratio. If the system's total collateral ratio (TCR) for a given collateral falls below the SCR,
  37 |     // the protocol triggers the shutdown of the borrow market and permanently disables all borrowing operations except for closing Troves.
  38 |     uint256 public immutable SCR;
  39 |     bool public hasBeenShutDown;
  40 | 
  41 |     // Minimum collateral ratio for individual troves
  42 |     uint256 public immutable MCR;
  43 | 
  44 |     // Extra buffer of collateral ratio to join a batch or adjust a trove inside a batch (on top of MCR)
  45 |     uint256 public immutable BCR;
  46 | 
  47 |     /*
  48 |     * Mapping from TroveId to individual delegate for interest rate setting.
  49 |     *
  50 |     * This address then has the ability to update the borrower’s interest rate, but not change its debt or collateral.
  51 |     * Useful for instance for cold/hot wallet setups.
  52 |     */
  53 |     mapping(uint256 => InterestIndividualDelegate) private interestIndividualDelegateOf;
  54 | 
  55 |     /*
  56 |      * Mapping from TroveId to granted address for interest rate setting (batch manager).
  57 |      *
  58 |      * Batch managers set the interest rate for every Trove in the batch. The interest rate is the same for all Troves in the batch.
  59 |      */
  60 |     mapping(uint256 => address) public interestBatchManagerOf;
  61 | 
  62 |     // List of registered Interest Batch Managers
  63 |     mapping(address => InterestBatchManager) private interestBatchManagers;
  64 | 
  65 |     /* --- Variable container structs  ---
  66 | 
  67 |     Used to hold, return and assign variables inside a function, in order to avoid the error:
  68 |     "CompilerError: Stack too deep". */
  69 | 
  70 |     struct OpenTroveVars {
  71 |         ITroveManager troveManager;
  72 |         uint256 troveId;
  73 |         TroveChange change;
  74 |         LatestBatchData batch;
  75 |     }
  76 | 
  77 |     struct LocalVariables_openTrove {
  78 |         ITroveManager troveManager;
  79 |         IActivePool activePool;
  80 |         IBoldToken boldToken;
  81 |         uint256 troveId;
  82 |         uint256 price;
  83 |         uint256 avgInterestRate;
  84 |         uint256 entireDebt;
  85 |         uint256 ICR;
  86 |         uint256 newTCR;
  87 |         bool newOracleFailureDetected;
  88 |     }
  89 | 
  90 |     struct LocalVariables_adjustTrove {
  91 |         IActivePool activePool;
  92 |         IBoldToken boldToken;
  93 |         LatestTroveData trove;
  94 |         uint256 price;
  95 |         bool isBelowCriticalThreshold;
  96 |         uint256 newICR;
  97 |         uint256 newDebt;
  98 |         uint256 newColl;
  99 |         bool newOracleFailureDetected;
 100 |     }
 101 | 
 102 |     struct LocalVariables_setInterestBatchManager {
 103 |         ITroveManager troveManager;
 104 |         IActivePool activePool;
 105 |         ISortedTroves sortedTroves;
 106 |         address oldBatchManager;
 107 |         LatestTroveData trove;
 108 |         LatestBatchData oldBatch;
 109 |         LatestBatchData newBatch;
 110 |     }
 111 | 
 112 |     struct LocalVariables_removeFromBatch {
 113 |         ITroveManager troveManager;
 114 |         ISortedTroves sortedTroves;
 115 |         address batchManager;
 116 |         LatestTroveData trove;
 117 |         LatestBatchData batch;
 118 |         uint256 batchFutureDebt;
 119 |         TroveChange batchChange;
 120 |     }
 121 | 
 122 |     error IsShutDown();
 123 |     error TCRNotBelowSCR();
 124 |     error ZeroAdjustment();
 125 |     error NotOwnerNorInterestManager();
 126 |     error TroveInBatch();
 127 |     error TroveNotInBatch();
 128 |     error InterestNotInRange();
 129 |     error BatchInterestRateChangePeriodNotPassed();
 130 |     error DelegateInterestRateChangePeriodNotPassed();
 131 |     error TroveExists();
 132 |     error TroveNotOpen();
 133 |     error TroveNotActive();
 134 |     error TroveNotZombie();
 135 |     error TroveWithZeroDebt();
 136 |     error UpfrontFeeTooHigh();
 137 |     error ICRBelowMCR();
 138 |     error ICRBelowMCRPlusBCR();
 139 |     error RepaymentNotMatchingCollWithdrawal();
 140 |     error TCRBelowCCR();
 141 |     error DebtBelowMin();
 142 |     error CollWithdrawalTooHigh();
 143 |     error NotEnoughBoldBalance();
 144 |     error InterestRateTooLow();
 145 |     error InterestRateTooHigh();
 146 |     error InterestRateNotNew();
 147 |     error InvalidInterestBatchManager();
 148 |     error BatchManagerExists();
 149 |     error BatchManagerNotNew();
 150 |     error NewFeeNotLower();
 151 |     error CallerNotTroveManager();
 152 |     error CallerNotPriceFeed();
 153 |     error MinGeMax();
 154 |     error AnnualManagementFeeTooHigh();
 155 |     error MinInterestRateChangePeriodTooLow();
 156 |     error NewOracleFailureDetected();
 157 |     error BatchSharesRatioTooLow();
 158 | 
 159 |     event TroveManagerAddressChanged(address _newTroveManagerAddress);
 160 |     event GasPoolAddressChanged(address _gasPoolAddress);
 161 |     event CollSurplusPoolAddressChanged(address _collSurplusPoolAddress);
 162 |     event SortedTrovesAddressChanged(address _sortedTrovesAddress);
 163 |     event BoldTokenAddressChanged(address _boldTokenAddress);
 164 | 
 165 |     event ShutDown(uint256 _tcr);
 166 | 
 167 |     constructor(IAddressesRegistry _addressesRegistry)
 168 |         AddRemoveManagers(_addressesRegistry)
 169 |         LiquityBase(_addressesRegistry)
 170 |     {
 171 |         // This makes impossible to open a trove with zero withdrawn Bold
 172 |         assert(MIN_DEBT > 0);
 173 | 
 174 |         collToken = _addressesRegistry.collToken();
 175 | 
 176 |         WETH = _addressesRegistry.WETH();
 177 | 
 178 |         CCR = _addressesRegistry.CCR();
 179 |         SCR = _addressesRegistry.SCR();
 180 |         MCR = _addressesRegistry.MCR();
 181 |         BCR = _addressesRegistry.BCR();
 182 | 
 183 |         troveManager = _addressesRegistry.troveManager();
 184 |         gasPoolAddress = _addressesRegistry.gasPoolAddress();
 185 |         collSurplusPool = _addressesRegistry.collSurplusPool();
 186 |         sortedTroves = _addressesRegistry.sortedTroves();
 187 |         boldToken = _addressesRegistry.boldToken();
 188 | 
 189 |         emit TroveManagerAddressChanged(address(troveManager));
 190 |         emit GasPoolAddressChanged(gasPoolAddress);
 191 |         emit CollSurplusPoolAddressChanged(address(collSurplusPool));
 192 |         emit SortedTrovesAddressChanged(address(sortedTroves));
 193 |         emit BoldTokenAddressChanged(address(boldToken));
 194 | 
 195 |         // Allow funds movements between Liquity contracts
 196 |         collToken.approve(address(activePool), type(uint256).max);
 197 |     }
 198 | 
 199 |     // --- Borrower Trove Operations ---
 200 | 
 201 |     function openTrove(
 202 |         address _owner,
 203 |         uint256 _ownerIndex,
 204 |         uint256 _collAmount,
 205 |         uint256 _boldAmount,
 206 |         uint256 _upperHint,
 207 |         uint256 _lowerHint,
 208 |         uint256 _annualInterestRate,
 209 |         uint256 _maxUpfrontFee,
 210 |         address _addManager,
 211 |         address _removeManager,
 212 |         address _receiver
 213 |     ) external override returns (uint256) {
 214 |         _requireValidAnnualInterestRate(_annualInterestRate);
 215 | 
 216 |         OpenTroveVars memory vars;
 217 | 
 218 |         vars.troveId = _openTrove(
 219 |             _owner,
 220 |             _ownerIndex,
 221 |             _collAmount,
 222 |             _boldAmount,
 223 |             _annualInterestRate,
 224 |             address(0),
 225 |             0,
 226 |             0,
 227 |             _maxUpfrontFee,
 228 |             _addManager,
 229 |             _removeManager,
 230 |             _receiver,
 231 |             vars.change
 232 |         );
 233 | 
 234 |         // Set the stored Trove properties and mint the NFT
 235 |         troveManager.onOpenTrove(_owner, vars.troveId, vars.change, _annualInterestRate);
 236 | 
 237 |         sortedTroves.insert(vars.troveId, _annualInterestRate, _upperHint, _lowerHint);
 238 | 
 239 |         return vars.troveId;
 240 |     }
 241 | 
 242 |     function openTroveAndJoinInterestBatchManager(OpenTroveAndJoinInterestBatchManagerParams calldata _params)
 243 |         external
 244 |         override
 245 |         returns (uint256)
 246 |     {
 247 |         _requireValidInterestBatchManager(_params.interestBatchManager);
 248 | 
 249 |         OpenTroveVars memory vars;
 250 |         vars.troveManager = troveManager;
 251 | 
 252 |         vars.batch = vars.troveManager.getLatestBatchData(_params.interestBatchManager);
 253 | 
 254 |         // We set old weighted values here, as it’s only necessary for batches, so we don’t need to pass them to _openTrove func
 255 |         vars.change.batchAccruedManagementFee = vars.batch.accruedManagementFee;
 256 |         vars.change.oldWeightedRecordedDebt = vars.batch.weightedRecordedDebt;
 257 |         vars.change.oldWeightedRecordedBatchManagementFee = vars.batch.weightedRecordedBatchManagementFee;
 258 |         vars.troveId = _openTrove(
 259 |             _params.owner,
 260 |             _params.ownerIndex,
 261 |             _params.collAmount,
 262 |             _params.boldAmount,
 263 |             vars.batch.annualInterestRate,
 264 |             _params.interestBatchManager,
 265 |             vars.batch.entireDebtWithoutRedistribution,
 266 |             vars.batch.annualManagementFee,
 267 |             _params.maxUpfrontFee,
 268 |             _params.addManager,
 269 |             _params.removeManager,
 270 |             _params.receiver,
 271 |             vars.change
 272 |         );
 273 | 
 274 |         interestBatchManagerOf[vars.troveId] = _params.interestBatchManager;
 275 | 
 276 |         // Set the stored Trove properties and mint the NFT
 277 |         vars.troveManager.onOpenTroveAndJoinBatch(
 278 |             _params.owner,
 279 |             vars.troveId,
 280 |             vars.change,
 281 |             _params.interestBatchManager,
 282 |             vars.batch.entireCollWithoutRedistribution,
 283 |             vars.batch.entireDebtWithoutRedistribution
 284 |         );
 285 | 
 286 |         sortedTroves.insertIntoBatch(
 287 |             vars.troveId,
 288 |             BatchId.wrap(_params.interestBatchManager),
 289 |             vars.batch.annualInterestRate,
 290 |             _params.upperHint,
 291 |             _params.lowerHint
 292 |         );
 293 | 
 294 |         return vars.troveId;
 295 |     }
 296 | 
 297 |     function _openTrove(
 298 |         address _owner,
 299 |         uint256 _ownerIndex,
 300 |         uint256 _collAmount,
 301 |         uint256 _boldAmount,
 302 |         uint256 _annualInterestRate,
 303 |         address _interestBatchManager,
 304 |         uint256 _batchEntireDebt,
 305 |         uint256 _batchManagementAnnualFee,
 306 |         uint256 _maxUpfrontFee,
 307 |         address _addManager,
 308 |         address _removeManager,
 309 |         address _receiver,
 310 |         TroveChange memory _change
 311 |     ) internal returns (uint256) {
 312 |         _requireIsNotShutDown();
 313 | 
 314 |         LocalVariables_openTrove memory vars;
 315 | 
 316 |         // stack too deep not allowing to reuse troveManager from outer functions
 317 |         vars.troveManager = troveManager;
 318 |         vars.activePool = activePool;
 319 |         vars.boldToken = boldToken;
 320 | 
 321 |         vars.price = _requireOraclesLive();
 322 | 
 323 |         // --- Checks ---
 324 | 
 325 |         vars.troveId = uint256(keccak256(abi.encode(msg.sender, _owner, _ownerIndex)));
 326 |         _requireTroveDoesNotExists(vars.troveManager, vars.troveId);
 327 | 
 328 |         _change.collIncrease = _collAmount;
 329 |         _change.debtIncrease = _boldAmount;
 330 | 
 331 |         // For simplicity, we ignore the fee when calculating the approx. interest rate
 332 |         _change.newWeightedRecordedDebt = (_batchEntireDebt + _change.debtIncrease) * _annualInterestRate;
 333 | 
 334 |         vars.avgInterestRate = vars.activePool.getNewApproxAvgInterestRateFromTroveChange(_change);
 335 |         _change.upfrontFee = _calcUpfrontFee(_change.debtIncrease, vars.avgInterestRate);
 336 |         _requireUserAcceptsUpfrontFee(_change.upfrontFee, _maxUpfrontFee);
 337 | 
 338 |         vars.entireDebt = _change.debtIncrease + _change.upfrontFee;
 339 |         _requireAtLeastMinDebt(vars.entireDebt);
 340 | 
 341 |         vars.ICR = LiquityMath._computeCR(_collAmount, vars.entireDebt, vars.price);
 342 | 
 343 |         // Recalculate newWeightedRecordedDebt, now taking into account the upfront fee, and the batch fee if needed
 344 |         if (_interestBatchManager == address(0)) {
 345 |             _change.newWeightedRecordedDebt = vars.entireDebt * _annualInterestRate;
 346 | 
 347 |             // ICR is based on the requested Bold amount + upfront fee.
 348 |             _requireICRisAboveMCR(vars.ICR);
 349 |         } else {
 350 |             // old values have been set outside, before calling this function
 351 |             _change.newWeightedRecordedDebt = (_batchEntireDebt + vars.entireDebt) * _annualInterestRate;
 352 |             _change.newWeightedRecordedBatchManagementFee =
 353 |                 (_batchEntireDebt + vars.entireDebt) * _batchManagementAnnualFee;
 354 | 
 355 |             // ICR is based on the requested Bold amount + upfront fee.
 356 |             // Troves in a batch have a stronger requirement (MCR+BCR)
 357 |             _requireICRisAboveMCRPlusBCR(vars.ICR);
 358 |         }
 359 | 
 360 |         vars.newTCR = _getNewTCRFromTroveChange(_change, vars.price);
 361 |         _requireNewTCRisAboveCCR(vars.newTCR);
 362 | 
 363 |         // --- Effects & interactions ---
 364 | 
 365 |         // Set add/remove managers
 366 |         _setAddManager(vars.troveId, _addManager);
 367 |         _setRemoveManagerAndReceiver(vars.troveId, _removeManager, _receiver);
 368 | 
 369 |         vars.activePool.mintAggInterestAndAccountForTroveChange(_change, _interestBatchManager);
 370 | 
 371 |         // Pull coll tokens from sender and move them to the Active Pool
 372 |         _pullCollAndSendToActivePool(vars.activePool, _collAmount);
 373 | 
 374 |         // Mint the requested _boldAmount to the borrower and mint the gas comp to the GasPool
 375 |         vars.boldToken.mint(msg.sender, _boldAmount);
 376 |         WETH.transferFrom(msg.sender, gasPoolAddress, ETH_GAS_COMPENSATION);
 377 | 
 378 |         return vars.troveId;
 379 |     }
 380 | 
 381 |     // Send collateral to a trove
 382 |     function addColl(uint256 _troveId, uint256 _collAmount) external override {
 383 |         ITroveManager troveManagerCached = troveManager;
 384 |         _requireTroveIsActive(troveManagerCached, _troveId);
 385 | 
 386 |         TroveChange memory troveChange;
 387 |         troveChange.collIncrease = _collAmount;
 388 | 
 389 |         _adjustTrove(
 390 |             troveManagerCached,
 391 |             _troveId,
 392 |             troveChange,
 393 |             0 // _maxUpfrontFee
 394 |         );
 395 |     }
 396 | 
 397 |     // Withdraw collateral from a trove
 398 |     function withdrawColl(uint256 _troveId, uint256 _collWithdrawal) external override {
 399 |         ITroveManager troveManagerCached = troveManager;
 400 |         _requireTroveIsActive(troveManagerCached, _troveId);
 401 | 
 402 |         TroveChange memory troveChange;
 403 |         troveChange.collDecrease = _collWithdrawal;
 404 | 
 405 |         _adjustTrove(
 406 |             troveManagerCached,
 407 |             _troveId,
 408 |             troveChange,
 409 |             0 // _maxUpfrontFee
 410 |         );
 411 |     }
 412 | 
 413 |     // Withdraw Bold tokens from a trove: mint new Bold tokens to the owner, and increase the trove's debt accordingly
 414 |     function withdrawBold(uint256 _troveId, uint256 _boldAmount, uint256 _maxUpfrontFee) external override {
 415 |         ITroveManager troveManagerCached = troveManager;
 416 |         _requireTroveIsActive(troveManagerCached, _troveId);
 417 | 
 418 |         TroveChange memory troveChange;
 419 |         troveChange.debtIncrease = _boldAmount;
 420 |         _adjustTrove(troveManagerCached, _troveId, troveChange, _maxUpfrontFee);
 421 |     }
 422 | 
 423 |     // Repay Bold tokens to a Trove: Burn the repaid Bold tokens, and reduce the trove's debt accordingly
 424 |     function repayBold(uint256 _troveId, uint256 _boldAmount) external override {
 425 |         ITroveManager troveManagerCached = troveManager;
 426 |         _requireTroveIsActive(troveManagerCached, _troveId);
 427 | 
 428 |         TroveChange memory troveChange;
 429 |         troveChange.debtDecrease = _boldAmount;
 430 | 
 431 |         _adjustTrove(
 432 |             troveManagerCached,
 433 |             _troveId,
 434 |             troveChange,
 435 |             0 // _maxUpfrontFee
 436 |         );
 437 |     }
 438 | 
 439 |     function _initTroveChange(
 440 |         TroveChange memory _troveChange,
 441 |         uint256 _collChange,
 442 |         bool _isCollIncrease,
 443 |         uint256 _boldChange,
 444 |         bool _isDebtIncrease
 445 |     ) internal pure {
 446 |         if (_isCollIncrease) {
 447 |             _troveChange.collIncrease = _collChange;
 448 |         } else {
 449 |             _troveChange.collDecrease = _collChange;
 450 |         }
 451 | 
 452 |         if (_isDebtIncrease) {
 453 |             _troveChange.debtIncrease = _boldChange;
 454 |         } else {
 455 |             _troveChange.debtDecrease = _boldChange;
 456 |         }
 457 |     }
 458 | 
 459 |     function adjustTrove(
 460 |         uint256 _troveId,
 461 |         uint256 _collChange,
 462 |         bool _isCollIncrease,
 463 |         uint256 _boldChange,
 464 |         bool _isDebtIncrease,
 465 |         uint256 _maxUpfrontFee
 466 |     ) external override {
 467 |         ITroveManager troveManagerCached = troveManager;
 468 |         _requireTroveIsActive(troveManagerCached, _troveId);
 469 | 
 470 |         TroveChange memory troveChange;
 471 |         _initTroveChange(troveChange, _collChange, _isCollIncrease, _boldChange, _isDebtIncrease);
 472 |         _adjustTrove(troveManagerCached, _troveId, troveChange, _maxUpfrontFee);
 473 |     }
 474 | 
 475 |     function adjustZombieTrove(
 476 |         uint256 _troveId,
 477 |         uint256 _collChange,
 478 |         bool _isCollIncrease,
 479 |         uint256 _boldChange,
 480 |         bool _isDebtIncrease,
 481 |         uint256 _upperHint,
 482 |         uint256 _lowerHint,
 483 |         uint256 _maxUpfrontFee
 484 |     ) external override {
 485 |         ITroveManager troveManagerCached = troveManager;
 486 |         _requireTroveIsZombie(troveManagerCached, _troveId);
 487 | 
 488 |         TroveChange memory troveChange;
 489 |         _initTroveChange(troveChange, _collChange, _isCollIncrease, _boldChange, _isDebtIncrease);
 490 |         _adjustTrove(troveManagerCached, _troveId, troveChange, _maxUpfrontFee);
 491 | 
 492 |         troveManagerCached.setTroveStatusToActive(_troveId);
 493 | 
 494 |         address batchManager = interestBatchManagerOf[_troveId];
 495 |         uint256 batchAnnualInterestRate;
 496 |         if (batchManager != address(0)) {
 497 |             LatestBatchData memory batch = troveManagerCached.getLatestBatchData(batchManager);
 498 |             batchAnnualInterestRate = batch.annualInterestRate;
 499 |         }
 500 |         _reInsertIntoSortedTroves(
 501 |             _troveId,
 502 |             troveManagerCached.getTroveAnnualInterestRate(_troveId),
 503 |             _upperHint,
 504 |             _lowerHint,
 505 |             batchManager,
 506 |             batchAnnualInterestRate
 507 |         );
 508 |     }
 509 | 
 510 |     function adjustTroveInterestRate(
 511 |         uint256 _troveId,
 512 |         uint256 _newAnnualInterestRate,
 513 |         uint256 _upperHint,
 514 |         uint256 _lowerHint,
 515 |         uint256 _maxUpfrontFee
 516 |     ) external {
 517 |         _requireIsNotShutDown();
 518 | 
 519 |         ITroveManager troveManagerCached = troveManager;
 520 | 
 521 |         _requireValidAnnualInterestRate(_newAnnualInterestRate);
 522 |         _requireIsNotInBatch(_troveId);
 523 |         _requireSenderIsOwnerOrInterestManager(_troveId);
 524 |         _requireTroveIsActive(troveManagerCached, _troveId);
 525 | 
 526 |         LatestTroveData memory trove = troveManagerCached.getLatestTroveData(_troveId);
 527 |         _requireValidDelegateAdustment(_troveId, trove.lastInterestRateAdjTime, _newAnnualInterestRate);
 528 |         _requireAnnualInterestRateIsNew(trove.annualInterestRate, _newAnnualInterestRate);
 529 | 
 530 |         uint256 newDebt = trove.entireDebt;
 531 | 
 532 |         TroveChange memory troveChange;
 533 |         troveChange.appliedRedistBoldDebtGain = trove.redistBoldDebtGain;
 534 |         troveChange.appliedRedistCollGain = trove.redistCollGain;
 535 |         troveChange.newWeightedRecordedDebt = newDebt * _newAnnualInterestRate;
 536 |         troveChange.oldWeightedRecordedDebt = trove.weightedRecordedDebt;
 537 | 
 538 |         // Apply upfront fee on premature adjustments. It checks the resulting ICR
 539 |         if (block.timestamp < trove.lastInterestRateAdjTime + INTEREST_RATE_ADJ_COOLDOWN) {
 540 |             newDebt = _applyUpfrontFee(trove.entireColl, newDebt, troveChange, _maxUpfrontFee, false);
 541 |         }
 542 | 
 543 |         // Recalculate newWeightedRecordedDebt, now taking into account the upfront fee
 544 |         troveChange.newWeightedRecordedDebt = newDebt * _newAnnualInterestRate;
 545 | 
 546 |         activePool.mintAggInterestAndAccountForTroveChange(troveChange, address(0));
 547 | 
 548 |         sortedTroves.reInsert(_troveId, _newAnnualInterestRate, _upperHint, _lowerHint);
 549 |         troveManagerCached.onAdjustTroveInterestRate(
 550 |             _troveId, trove.entireColl, newDebt, _newAnnualInterestRate, troveChange
 551 |         );
 552 |     }
 553 | 
 554 |     /*
 555 |     * _adjustTrove(): Alongside a debt change, this function can perform either a collateral top-up or a collateral withdrawal.
 556 |     */
 557 |     function _adjustTrove(
 558 |         ITroveManager _troveManager,
 559 |         uint256 _troveId,
 560 |         TroveChange memory _troveChange,
 561 |         uint256 _maxUpfrontFee
 562 |     ) internal {
 563 |         _requireIsNotShutDown();
 564 | 
 565 |         LocalVariables_adjustTrove memory vars;
 566 |         vars.activePool = activePool;
 567 |         vars.boldToken = boldToken;
 568 | 
 569 |         vars.price = _requireOraclesLive();
 570 |         vars.isBelowCriticalThreshold = _checkBelowCriticalThreshold(vars.price, CCR);
 571 | 
 572 |         // --- Checks ---
 573 | 
 574 |         _requireTroveIsOpen(_troveManager, _troveId);
 575 | 
 576 |         address owner = troveNFT.ownerOf(_troveId);
 577 |         address receiver = owner; // If it’s a withdrawal, and remove