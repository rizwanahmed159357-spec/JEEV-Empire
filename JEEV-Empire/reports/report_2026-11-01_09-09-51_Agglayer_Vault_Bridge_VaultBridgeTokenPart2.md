Title: Missing disableInitializers in VaultBridgeTokenPart2.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/VaultBridgeTokenPart2.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {VaultBridgeToken} from "./VaultBridgeToken.sol";
   8 | import {IERC4626} from "@openzeppelin/contracts/interfaces/IERC4626.sol";
   9 | 
  10 | // Libraries.
  11 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  12 | import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
  13 | 
  14 | // External contracts.
  15 | import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
  16 | 
  17 | /// @title Vault Bridge Token: Part 2 (singleton)
  18 | /// @author See https://github.com/agglayer/vault-bridge
  19 | /// @dev This contract exists because of the contract size limit of the EVM.
  20 | contract VaultBridgeTokenPart2 is VaultBridgeToken {
  21 |     // Libraries.
  22 |     using SafeERC20 for IERC20;
  23 | 
  24 |     /// @dev The storage slot at which Vault Bridge Token storage starts, following the EIP-7201 standard.
  25 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.VaultBridgeToken.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  26 |     bytes32 private constant _VAULT_BRIDGE_TOKEN_STORAGE =
  27 |         hex"f082fbc4cfb4d172ba00d34227e208a31ceb0982bc189440d519185302e44700";
  28 | 
  29 |     // -----================= ::: SOLIDITY ::: =================-----
  30 | 
  31 |     fallback() external {
  32 |         revert UnknownFunction(bytes4(msg.data));
  33 |     }
  34 | 
  35 |     // -----================= ::: SETUP ::: =================-----
  36 | 
  37 |     constructor() {
  38 |         _disableInitializers();
  39 |     }
  40 | 
  41 |     /// @inheritdoc VaultBridgeToken
  42 |     function _VAULT_BRIDGE_TOKEN_INIT_2_COMPATIBLE() internal pure override {}
  43 | 
  44 |     // -----================= ::: STORAGE ::: =================-----
  45 | 
  46 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
  47 |     function __getVaultBridgeTokenStorage() private pure returns (VaultBridgeTokenStorage storage $) {
  48 |         assembly {
  49 |             $.slot := _VAULT_BRIDGE_TOKEN_STORAGE
  50 |         }
  51 |     }
  52 | 
  53 |     // -----================= ::: VAULT BRIDGE TOKEN ::: =================-----
  54 | 
  55 |     /// @inheritdoc VaultBridgeToken
  56 |     function rebalanceReserve() external override whenNotPaused onlyRole(REBALANCER_ROLE) nonReentrant {
  57 |         _rebalanceReserve(true, true);
  58 |     }
  59 | 
  60 |     /// @inheritdoc VaultBridgeToken
  61 |     function collectYield() external override onlyRole(YIELD_COLLECTOR_ROLE) nonReentrant {
  62 |         _collectYield(true);
  63 |     }
  64 | 
  65 |     /// @notice Transfers yield produced by the yield vault to the yield recipient in the form of vbToken.
  66 |     /// @dev Does not rebalance the reserve after collecting yield to allow usage while the contract is paused.
  67 |     /// @param force Whether to revert if no yield can be collected.
  68 |     function _collectYield(bool force) internal {
  69 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
  70 | 
  71 |         // Calculate the yield.
  72 |         uint256 yield_ = yield();
  73 | 
  74 |         if (yield_ > 0) {
  75 |             // Update the net collected yield.
  76 |             $._netCollectedYield += yield_;
  77 | 
  78 |             // Mint vbToken to the yield recipient.
  79 |             _mint($.yieldRecipient, yield_);
  80 | 
  81 |             // Emit the event.
  82 |             emit YieldCollected(yieldRecipient(), yield_);
  83 |         } else if (force) {
  84 |             // Revert if there is no yield and `force` is `true`.
  85 |             revert NoYield();
  86 |         }
  87 |     }
  88 | 
  89 |     /// @inheritdoc VaultBridgeToken
  90 |     function burn(uint256 shares) external override onlyYieldRecipient nonReentrant {
  91 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
  92 | 
  93 |         // Check the inputs.
  94 |         require(shares > 0, InvalidShares());
  95 | 
  96 |         // Update the net collected yield.
  97 |         $._netCollectedYield -= shares;
  98 | 
  99 |         // Burn vbToken.
 100 |         _burn(msg.sender, shares);
 101 | 
 102 |         // Emit the event.
 103 |         emit Burned(shares);
 104 |     }
 105 | 
 106 |     /// @inheritdoc VaultBridgeToken
 107 |     function donateAsYield(uint256 assets) external override nonReentrant {
 108 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 109 | 
 110 |         // Check the input.
 111 |         require(assets > 0, InvalidAssets());
 112 | 
 113 |         // Transfer the underlying token from the sender to self.
 114 |         _receiveUnderlyingToken(msg.sender, assets);
 115 | 
 116 |         // Update the reserve.
 117 |         $.reservedAssets += assets;
 118 | 
 119 |         // Emit the event.
 120 |         emit DonatedAsYield(msg.sender, assets);
 121 |     }
 122 | 
 123 |     /// @inheritdoc VaultBridgeToken
 124 |     function completeMigration(uint32 originNetwork, uint256 shares, uint256 assets)
 125 |         external
 126 |         override
 127 |         whenNotPaused
 128 |         onlyMigrationManager
 129 |         nonReentrant
 130 |     {
 131 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 132 | 
 133 |         // Check the inputs.
 134 |         require(originNetwork != $.agglayerId, InvalidOriginNetwork());
 135 |         require(shares > 0, InvalidShares());
 136 | 
 137 |         // Transfer the underlying token from the sender to self.
 138 |         _receiveUnderlyingToken(msg.sender, assets);
 139 | 
 140 |         // Calculate the discrepancy between the required amount of vbToken (`shares`) and the amount of the underlying token received from Migration Manager (`assets`).
 141 |         // A discrepancy is possible if the underlying token implements transfer fees on Secondary Chain. To offset the discrepancy, we mint more vbToken, backed by assets from the dedicated migration fees fund.
 142 |         // This ensures that the amount of vbToken locked up in Agglayer Bridge on Primary Chain matches the supply of Custom Token on Secondary Chains down to a wei.
 143 |         uint256 requiredAssets = convertToAssets(shares);
 144 |         uint256 discrepancy = requiredAssets - assets;
 145 |         uint256 assetsInMigrationFund = $.migrationFeesFund;
 146 |         if (discrepancy > 0) {
 147 |             // Check if there are enought assets in the migration fees fund to cover the discrepancy.
 148 |             require(
 149 |                 assetsInMigrationFund >= discrepancy,
 150 |                 CannotCompleteMigration(requiredAssets, assets, assetsInMigrationFund)
 151 |             );
 152 | 
 153 |             // Move the discrepancy from the migration fees fund to the reserve.
 154 |             $.migrationFeesFund -= discrepancy;
 155 |             $.reservedAssets += discrepancy;
 156 |         }
 157 | 
 158 |         // Calculate the amount to reserve.
 159 |         uint256 assetsToReserve = _calculateAmountToReserve(assets, shares);
 160 | 
 161 |         // Calculate the amount to try to deposit into the yield vault.
 162 |         uint256 assetsToDeposit = assets - assetsToReserve;
 163 | 
 164 |         // Try to deposit into the yield vault.
 165 |         if (assetsToDeposit > 0) {
 166 |             // Deposit, and update the amount to reserve if necessary.
 167 |             assetsToReserve += _depositIntoYieldVault(assetsToDeposit, false, false);
 168 |         }
 169 | 
 170 |         // Update the reserve.
 171 |         $.reservedAssets += assetsToReserve;
 172 | 
 173 |         // Mint vbToken to self and bridge it to address zero on the origin network.
 174 |         // The vbToken will not be claimable on the origin network, but provides liquidity when bridging from Secondary Chains to Primary Chain and increments the pessimistic proof.
 175 |         _mint(address(this), shares);
 176 |         $.agglayerBridge.bridgeAsset(originNetwork, address(0), shares, address(this), true, "");
 177 | 
 178 |         // Emit the ERC-4626 event.
 179 |         emit IERC4626.Deposit(msg.sender, address(this), assets, shares);
 180 | 
 181 |         // Emit the event.
 182 |         emit MigrationCompleted(originNetwork, shares, assets, discrepancy);
 183 |     }
 184 | 
 185 |     /// @inheritdoc VaultBridgeToken
 186 |     function donateForCompletingMigration(uint256 assets) external override whenNotPaused nonReentrant {
 187 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 188 | 
 189 |         // Check the input.
 190 |         require(assets > 0, InvalidAssets());
 191 | 
 192 |         // Transfer the underlying token from the sender to self.
 193 |         _receiveUnderlyingToken(msg.sender, assets);
 194 | 
 195 |         // Update the migration fees fund.
 196 |         $.migrationFeesFund += assets;
 197 | 
 198 |         // Emit the event.
 199 |         emit DonatedForCompletingMigration(msg.sender, assets);
 200 |     }
 201 | 
 202 |     /// @inheritdoc VaultBridgeToken
 203 |     function setYieldRecipient(bool precollectYield, address yieldRecipient_)
 204 |         external
 205 |         override
 206 |         onlyRole(DEFAULT_ADMIN_ROLE)
 207 |         nonReentrant
 208 |     {
 209 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 210 | 
 211 |         // Check the input.
 212 |         require(yieldRecipient_ != address(0), InvalidYieldRecipient());
 213 | 
 214 |         if (precollectYield) {
 215 |             // Try to collect yield.
 216 |             _collectYield(false);
 217 |         }
 218 | 
 219 |         // Set the yield recipient.
 220 |         $.yieldRecipient = yieldRecipient_;
 221 | 
 222 |         // Emit the event.
 223 |         emit YieldRecipientSet(yieldRecipient_);
 224 |     }
 225 | 
 226 |     /// @inheritdoc VaultBridgeToken
 227 |     function setMinimumReservePercentage(uint256 minimumReservePercentage_)
 228 |         external
 229 |         override
 230 |         onlyRole(DEFAULT_ADMIN_ROLE)
 231 |         nonReentrant
 232 |     {
 233 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 234 | 
 235 |         // Check the input.
 236 |         require(minimumReservePercentage_ <= 1e18, InvalidMinimumReservePercentage());
 237 | 
 238 |         // Set the minimum reserve percentage.
 239 |         $.minimumReservePercentage = minimumReservePercentage_;
 240 | 
 241 |         // Emit the event.
 242 |         emit MinimumReservePercentageSet(minimumReservePercentage_);
 243 |     }
 244 | 
 245 |     /// @inheritdoc VaultBridgeToken
 246 |     function drainYieldVault(uint256 shares, bool exact) external override onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 247 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 248 | 
 249 |         // Check the input.
 250 |         require(shares > 0, InvalidShares());
 251 | 
 252 |         // Cache the original total supply, reserved assets, and the yield vault shares balance.
 253 |         uint256 originalTotalSupply = totalSupply();
 254 |         uint256 originalReservedAssets = $.reservedAssets;
 255 |         uint256 originalYieldVaultSharesBalance = $.yieldVault.balanceOf(address(this));
 256 | 
 257 |         // Modify the input if set to infinite.
 258 |         if (shares == type(uint256).max) {
 259 |             shares = originalYieldVaultSharesBalance;
 260 |         }
 261 | 
 262 |         // Check the maximum shares that can be redeemed.
 263 |         uint256 maxShares = $.yieldVault.maxRedeem(address(this));
 264 | 
 265 |         // Revert if the requested shares are more than the maximum shares that can be redeemed, and `exact` is set to `true`.
 266 |         if (exact) {
 267 |             require(shares <= maxShares, YieldVaultRedemptionFailed(shares, maxShares));
 268 |         }
 269 | 
 270 |         // Modify the input if it is more than the maximum shares that can be redeemed.
 271 |         shares = shares > maxShares ? maxShares : shares;
 272 | 
 273 |         // Return if no shares would be redeemed.
 274 |         if (shares == 0) return;
 275 | 
 276 |         // Cache the underlying token balance.
 277 |         uint256 balanceBefore = $.underlyingToken.balanceOf(address(this));
 278 | 
 279 |         // Redeem.
 280 |         $.yieldVault.redeem(shares, address(this), address(this));
 281 | 
 282 |         // Get the new underlying token balance.
 283 |         uint256 balanceAfter = $.underlyingToken.balanceOf(address(this));
 284 | 
 285 |         // Calculate the amount of assets received from the yield vault.
 286 |         uint256 receivedAssets = balanceAfter - balanceBefore;
 287 | 
 288 |         // Update the reserve.
 289 |         $.reservedAssets += receivedAssets;
 290 | 
 291 |         // Check the output.
 292 |         // Redeeming all shares at this exchange rate would need to give enough assets to back the total supply of vbToken together with the reserved assets. Allows slippage.
 293 |         // Does not check uncollected yield to relax the condition. Yield can be collected manually before calling this function.
 294 |         require(
 295 |             Math.mulDiv(originalYieldVaultSharesBalance, receivedAssets, shares)
 296 |                 >= Math.mulDiv(
 297 |                     convertToAssets(originalTotalSupply) - originalReservedAssets,
 298 |                     1e18 - $.yieldVaultMaximumSlippagePercentage,
 299 |                     1e18
 300 |                 ),
 301 |             ExcessiveYieldVaultSharesBurned(shares, receivedAssets)
 302 |         );
 303 | 
 304 |         // Emit the event.
 305 |         emit YieldVaultDrained(shares, receivedAssets);
 306 |     }
 307 | 
 308 |     /// @inheritdoc VaultBridgeToken
 309 |     function setYieldVault(address yieldVault_) external override onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 310 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 311 | 
 312 |         // Check the input.
 313 |         require(yieldVault_ != address(0), InvalidYieldVault());
 314 | 
 315 |         // Revoke the approval for the old yield vault.
 316 |         $.underlyingToken.forceApprove(address($.yieldVault), 0);
 317 | 
 318 |         // Set the yield vault.
 319 |         $.yieldVault = IERC4626(yieldVault_);
 320 | 
 321 |         // Approve the new yield vault.
 322 |         $.underlyingToken.forceApprove(yieldVault_, type(uint256).max);
 323 | 
 324 |         // Emit the event.
 325 |         emit YieldVaultSet(yieldVault_);
 326 |     }
 327 | 
 328 |     function revokeYieldVaultApproval() external override onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 329 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 330 | 
 331 |         $.underlyingToken.forceApprove(address($.yieldVault), 0);
 332 |     }
 333 | 
 334 |     function restoreYieldVaultApproval() external override onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 335 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 336 | 
 337 |         $.underlyingToken.forceApprove(address($.yieldVault), type(uint256).max);
 338 |     }
 339 | 
 340 |     /// @inheritdoc VaultBridgeToken
 341 |     function setMinimumYieldVaultDeposit(uint256 minimumYieldVaultDeposit_)
 342 |         external
 343 |         override
 344 |         onlyRole(DEFAULT_ADMIN_ROLE)
 345 |         nonReentrant
 346 |     {
 347 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 348 |         $.minimumYieldVaultDeposit = minimumYieldVaultDeposit_;
 349 |     }
 350 | 
 351 |     /// @inheritdoc VaultBridgeToken
 352 |     function setYieldVaultMaximumSlippagePercentage(uint256 maximumSlippagePercentage)
 353 |         external
 354 |         override
 355 |         onlyRole(DEFAULT_ADMIN_ROLE)
 356 |         nonReentrant
 357 |     {
 358 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
 359 | 
 360 |         // Check the input.
 361 |         require(maximumSlippagePercentage <= 1e18, InvalidYieldVaultMaximumSlippagePercentage());
 362 | 
 363 |         // Set the maximum slippage percentage.
 364 |         $.yieldVaultMaximumSlippagePercentage = maximumSlippagePercentage;
 365 | 
 366 |         // Emit the event.
 367 |         emit YieldVaultMaximumSlippagePercentageSet(maximumSlippagePercentage);
 368 |     }
 369 | 
 370 |     // -----================= ::: ADMIN ::: =================-----
 371 | 
 372 |     /// @inheritdoc VaultBridgeToken
 373 |     function pause() external override onlyRole(PAUSER_ROLE) nonReentrant {
 374 |         _pause();
 375 |     }
 376 | 
 377 |     /// @inheritdoc VaultBridgeToken
 378 |     function unpause() external override onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 379 |         _unpause();
 380 |     }
 381 | }
 382 | 