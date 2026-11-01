Title: Missing disableInitializers in NativeConverter.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.0) (secondary-chain/NativeConverter.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Other functionality.
   7 | import {Initializable} from "@openzeppelin-contracts-upgradeable/proxy/utils/Initializable.sol";
   8 | import {AccessControlUpgradeable} from "@openzeppelin-contracts-upgradeable/access/AccessControlUpgradeable.sol";
   9 | import {PausableUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/PausableUpgradeable.sol";
  10 | import {ReentrancyGuardUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
  11 | import {ERC20PermitUser} from "../etc/ERC20PermitUser.sol";
  12 | import {InitializationCounterUpgradeable} from "../etc/InitializationCounterUpgradeable.sol";
  13 | import {Versioned} from "../etc/Versioned.sol";
  14 | 
  15 | // Libraries.
  16 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  17 | import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
  18 | 
  19 | // External contracts.
  20 | import {CustomToken} from "./CustomToken.sol";
  21 | import {CustomTokenWethExtension} from "./CustomTokenWethExtension.sol";
  22 | import {IAgglayerBridge} from "../etc/IAgglayerBridge.sol";
  23 | import {MigrationManager} from "../primary-chain/MigrationManager.sol";
  24 | import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
  25 | import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
  26 | 
  27 | /// @title Native Converter
  28 | /// @author See https://github.com/agglayer/vault-bridge
  29 | /// @notice Native Converter is an optional contract on Secondary Chains that converts the underlying token (usually the bridge-wrapped version of the original underlying token from Primary Chain) to Custom Token, and vice versa, on demand. It can also migrate backing for Custom Token it has minted to Primary Chain, where vbToken will be minted and locked in Agglayer Bridge. Please refer to `migrateBackingToPrimaryChain` for more information.
  30 | /// @dev A base contract used to create Native Converters.
  31 | /// @dev @note (ATTENTION) This contract MUST have mint and burn permission on Custom Token. Please refer to `CustomToken.sol` for more information.
  32 | /// @dev @note IMPORTANT: The underlying token MUST NOT be a rebasing token, and MUST NOT have transfer hooks (i.e., enable reentrancy); it MAY have a transfer fee.
  33 | abstract contract NativeConverter is
  34 |     Initializable,
  35 |     AccessControlUpgradeable,
  36 |     PausableUpgradeable,
  37 |     ReentrancyGuardUpgradeable,
  38 |     ERC20PermitUser,
  39 |     InitializationCounterUpgradeable,
  40 |     Versioned
  41 | {
  42 |     // Libraries.
  43 |     using SafeERC20 for IERC20;
  44 |     using SafeERC20 for CustomToken;
  45 | 
  46 |     /// @dev Storage of Native Converter contract.
  47 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  48 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.NativeConverter.storage
  49 |     struct NativeConverterStorage {
  50 |         CustomToken customToken;
  51 |         IERC20 underlyingToken;
  52 |         uint256 backingOnSecondaryChain;
  53 |         uint32 agglayerId;
  54 |         IAgglayerBridge bridge;
  55 |         uint32 primaryChainAgglayerId;
  56 |         uint256 nonMigratableBackingPercentage;
  57 |         address migrationManager;
  58 |         bool _underlyingTokenIsNotMintable;
  59 |         mapping(uint256 migratedBacking => uint256 times) _migrationsInProgress;
  60 |         uint256 _migrationsInProgressCount;
  61 |         uint256 _totalMigratedBackingInProgress;
  62 |     }
  63 | 
  64 |     /// @dev The storage slot at which Native Converter storage starts, following the EIP-7201 standard.
  65 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.NativeConverter.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  66 |     bytes32 private constant _NATIVE_CONVERTER_STORAGE =
  67 |         hex"a14770e0debfe4b8406a01c33ee3a7bbe0acc66b3bde7c71854bf7d080a9c600";
  68 | 
  69 |     // Basic roles.
  70 |     // @remind Document.
  71 |     bytes32 public constant MIGRATOR_ROLE = keccak256("MIGRATOR_ROLE");
  72 |     bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
  73 | 
  74 |     // Errors.
  75 |     error Unauthorized();
  76 |     error InvalidOwner();
  77 |     error InvalidCustomToken();
  78 |     error InvalidUnderlyingToken();
  79 |     error InvalidAgglayerBridge();
  80 |     error InvalidPrimaryChainAgglayerId();
  81 |     error InvalidMigrationManager();
  82 |     error NonMatchingTokenDecimals(uint8 customTokenDecimals, uint8 underlyingTokenDecimals);
  83 |     error InvalidAssets();
  84 |     error InvalidReceiver();
  85 |     error InvalidPermitData();
  86 |     error InvalidShares();
  87 |     error InvalidNonMigratableBackingPercentage();
  88 |     error AssetsTooLarge(uint256 availableAssets, uint256 requestedAssets);
  89 |     error InvalidDestinationNetworkId();
  90 |     error CannotSetCustomTokenIfBackingOnSecondaryChainIsNotZero();
  91 |     error CannotSetCustomTokenIfGasBackingOnSecondaryChainIsNotZero();
  92 |     error CannotSetCustomTokenIfMigrationsInProgressCountIsNotZero();
  93 | 
  94 |     // Events.
  95 |     event MigrationStarted(uint256 indexed mintedCustomToken, uint256 indexed migratedBacking);
  96 |     event NonMigratableBackingPercentageSet(uint256 nonMigratableBackingPercentage);
  97 |     event MigrationInProgressAdded(uint256 indexed migratedBacking);
  98 |     event MigrationInProgressRemoved(uint256 indexed mintedCustomToken);
  99 | 
 100 |     // -----================= ::: MODIFIERS ::: =================-----
 101 | 
 102 |     /// @dev Checks if the sender is the yield recipient.
 103 |     modifier onlyCustomToken() {
 104 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 105 |         require(msg.sender == address($.customToken), Unauthorized());
 106 |         _;
 107 |     }
 108 | 
 109 |     // -----================= ::: SETUP ::: =================-----
 110 | 
 111 |     /// @dev The `customToken` and `underlyingToken` MUST have the same number of decimals. @note (ATTENTION) The decimals of the `customToken` and `underlyingToken` will default to `18` if they revert on `decimals`.
 112 |     /// @param owner_ (ATTENTION) This address will be granted the `DEFAULT_ADMIN_ROLE`, as well as all basic roles. Roles can be modified at any time.
 113 |     /// @param customToken_ The upgraded version of the bridged vbToken. Native Converter must be able to mint and burn this token. Please refer to `CustomToken.sol` for more information.
 114 |     /// @param underlyingToken_ The token that represents the original underlying token on Secondary Chain. @note IMPORTANT: This token MUST be either the bridge-wrapped version of the original underlying token, or the original underlying token must be custom mapped to this token on Agglayer Bridge on Secondary Chain.
 115 |     /// @param nonMigratableBackingPercentage_ The percentage of backing that should remain in Native Converter when migrating backing to Primary Chain, based on the total supply of Custom Token. `1e18` is 100%. It is possible to game the system by manipulating the total supply of Custom Token, so this is more of a soft limit.
 116 |     /// @param migrationManager_ The address of the Migration Manager on Primary Chain.
 117 |     function __NativeConverter_init1(
 118 |         address owner_,
 119 |         address customToken_,
 120 |         address underlyingToken_,
 121 |         address agglayerBridge_,
 122 |         uint32 primaryChainAgglayerId_,
 123 |         uint256 nonMigratableBackingPercentage_,
 124 |         address migrationManager_
 125 |     ) internal onlyInitializing incrementsLocalInitializationCounter(1) {
 126 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 127 | 
 128 |         // Check the inputs.
 129 |         require(owner_ != address(0), InvalidOwner());
 130 |         require(customToken_ != address(0), InvalidCustomToken());
 131 |         require(underlyingToken_ != address(0), InvalidUnderlyingToken());
 132 |         require(agglayerBridge_ != address(0), InvalidAgglayerBridge());
 133 |         require(primaryChainAgglayerId_ != IAgglayerBridge(agglayerBridge_).networkID(), InvalidAgglayerBridge());
 134 |         require(migrationManager_ != address(0), InvalidMigrationManager());
 135 |         require(nonMigratableBackingPercentage_ <= 1e18, InvalidNonMigratableBackingPercentage());
 136 | 
 137 |         // Get Custom Token's decimals.
 138 |         uint8 customTokenDecimals;
 139 |         try IERC20Metadata(customToken_).decimals() returns (uint8 decimals) {
 140 |             customTokenDecimals = decimals;
 141 |         } catch {
 142 |             // Default to 18 decimals if Custom Token reverted.
 143 |             customTokenDecimals = 18;
 144 |         }
 145 | 
 146 |         // Get the underlying token's decimals.
 147 |         uint8 underlyingTokenDecimals;
 148 |         try IERC20Metadata(underlyingToken_).decimals() returns (uint8 decimals) {
 149 |             underlyingTokenDecimals = decimals;
 150 |         } catch {
 151 |             // Default to 18 decimals if the underlying token reverted.
 152 |             underlyingTokenDecimals = 18;
 153 |         }
 154 | 
 155 |         // Check the tokens' decimals.
 156 |         require(
 157 |             customTokenDecimals == underlyingTokenDecimals,
 158 |             NonMatchingTokenDecimals(customTokenDecimals, underlyingTokenDecimals)
 159 |         );
 160 | 
 161 |         // Initialize the inherited contracts.
 162 |         __AccessControl_init();
 163 |         __Pausable_init();
 164 |         __ReentrancyGuard_init();
 165 |         __Context_init();
 166 |         __ERC165_init();
 167 | 
 168 |         // Grant the basic roles.
 169 |         _grantRole(DEFAULT_ADMIN_ROLE, owner_);
 170 |         _grantRole(MIGRATOR_ROLE, owner_);
 171 |         _grantRole(PAUSER_ROLE, owner_);
 172 | 
 173 |         // Initialize the storage.
 174 |         $.customToken = CustomToken(customToken_);
 175 |         $.underlyingToken = IERC20(underlyingToken_);
 176 |         $.agglayerId = IAgglayerBridge(agglayerBridge_).networkID();
 177 |         $.bridge = IAgglayerBridge(agglayerBridge_);
 178 |         $.primaryChainAgglayerId = primaryChainAgglayerId_;
 179 |         $.migrationManager = migrationManager_;
 180 |         $.nonMigratableBackingPercentage = nonMigratableBackingPercentage_;
 181 |     }
 182 | 
 183 |     // @remind Document (the entire function).
 184 |     function __NativeConverter_init2() internal onlyInitializing incrementsLocalInitializationCounter(2) {
 185 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 186 | 
 187 |         $._underlyingTokenIsNotMintable = $.bridge.wrappedAddressIsNotMintable(address($.underlyingToken));
 188 |     }
 189 | 
 190 |     /*
 191 |     /// @dev How to add a new init step:
 192 |     function __NativeConverter_init3() internal onlyInitializing incrementsLocalInitializationCounter(3) {}
 193 |     */
 194 | 
 195 |     // @remind Document.
 196 |     function _NATIVE_CONVERTER_INIT_2_COMPATIBLE() internal pure virtual;
 197 | 
 198 |     // -----================= ::: STORAGE ::: =================-----
 199 | 
 200 |     /// @notice The upgraded version of the bridged vbToken.
 201 |     function customToken() public view returns (IERC20) {
 202 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 203 |         return $.customToken;
 204 |     }
 205 | 
 206 |     /// @notice The token that represent the original underlying token on Secondary Chain.
 207 |     function underlyingToken() public view returns (IERC20) {
 208 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 209 |         return $.underlyingToken;
 210 |     }
 211 | 
 212 |     /// @notice The amount of the underlying token that backs Custom Token minted by Native Converter on Secondary Chain that has not been migrated to Primary Chain.
 213 |     /// @dev The amount is used in accounting and may be different from Native Converter's underlying token balance. @note IMPORTANT: You may do as you wish with surplus underlying token balance, but you MUST NOT designate it as backing.
 214 |     function backingOnSecondaryChain() public view returns (uint256) {
 215 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 216 |         return $.backingOnSecondaryChain;
 217 |     }
 218 | 
 219 |     /// @notice The Agglayer ID of this network.
 220 |     function agglayerId() public view returns (uint32) {
 221 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 222 |         return $.agglayerId;
 223 |     }
 224 | 
 225 |     /// @notice Agglayer Bridge, which connects AggLayer networks.
 226 |     function bridge() public view returns (IAgglayerBridge) {
 227 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 228 |         return $.bridge;
 229 |     }
 230 | 
 231 |     /// @notice The Agglayer ID of Primary Chain.
 232 |     function primaryChainAgglayerId() public view returns (uint32) {
 233 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 234 |         return $.primaryChainAgglayerId;
 235 |     }
 236 | 
 237 |     /// @notice The percentage of backing that should remain in Native Converter when migrating backing to Primary Chain, based on the total supply of Custom Token.
 238 |     /// @dev It is possible to game the system by manipulating the total supply of Custom Token, so this is more of a soft limit.
 239 |     /// @return 1e18 is 100%.
 240 |     function nonMigratableBackingPercentage() public view returns (uint256) {
 241 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 242 |         return $.nonMigratableBackingPercentage;
 243 |     }
 244 | 
 245 |     /// @notice The address of the Migration Manager on Primary Chain.
 246 |     function migrationManager() public view returns (MigrationManager) {
 247 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 248 |         return MigrationManager(payable($.migrationManager));
 249 |     }
 250 | 
 251 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
 252 |     function _getNativeConverterStorage() private pure returns (NativeConverterStorage storage $) {
 253 |         assembly {
 254 |             $.slot := _NATIVE_CONVERTER_STORAGE
 255 |         }
 256 |     }
 257 | 
 258 |     // -----================= ::: PSEUDO VAULT ::: =================-----
 259 | 
 260 |     /// @notice Deposit a specific amount of the underlying token and get Custom Token.
 261 |     /// @param assets The amount of the underlying token to convert to Custom Token.
 262 |     /// @return shares The amount of Custom Token minted to the receiver.
 263 |     function convert(uint256 assets, address receiver) external whenNotPaused nonReentrant returns (uint256 shares) {
 264 |         return _convert(assets, receiver);
 265 |     }
 266 | 
 267 |     /// @notice Deposit a specific amount of the underlying token and get Custom Token.
 268 |     /// @param assets The amount of the underlying token to convert to Custom Token.
 269 |     /// @return shares The amount of Custom Token minted to the receiver.
 270 |     function _convert(uint256 assets, address receiver) internal returns (uint256 shares) {
 271 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 272 | 
 273 |         // Check the inputs.
 274 |         require(assets > 0, InvalidAssets());
 275 |         require(receiver != address(0), InvalidReceiver());
 276 | 
 277 |         // Transfer the underlying token from the sender to self.
 278 |         assets = _receiveUnderlyingToken(msg.sender, assets);
 279 | 
 280 |         // Update the backing data.
 281 |         $.backingOnSecondaryChain += assets;
 282 | 
 283 |         // Set the return value.
 284 |         shares = _convertToShares(assets);
 285 | 
 286 |         // Mint Custom Token to the receiver.
 287 |         _mintCustomToken(receiver, shares);
 288 |     }
 289 | 
 290 |     /// @notice Deposit a specific amount of the underlying token and get Custom Token.
 291 |     /// @dev Uses EIP-2612 permit to transfer the underlying token from the sender to self.
 292 |     /// @param assets The amount of the underlying token to convert to Custom Token.
 293 |     /// @return shares The amount of Custom Token minted to the receiver.
 294 |     function convertWithPermit(uint256 assets, address receiver, bytes calldata permitData)
 295 |         external
 296 |         whenNotPaused
 297 |         nonReentrant
 298 |         returns (uint256 shares)
 299 |     {
 300 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 301 | 
 302 |         // Check the input.
 303 |         require(permitData.length > 0, InvalidPermitData());
 304 | 
 305 |         // Use the permit.
 306 |         _permit(address($.underlyingToken), assets, permitData);
 307 | 
 308 |         return _convert(assets, receiver);
 309 |     }
 310 | 
 311 |     /// @notice How much Custom Token a specific user can burn. (Deconverting Custom Token burns it and unlocks the underlying token).
 312 |     function maxDeconvert(address owner) external view returns (uint256 maxShares) {
 313 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 314 | 
 315 |         // Return zero if the contract is paused.
 316 |         if (paused()) return 0;
 317 | 
 318 |         // Return zero if the balance is zero.
 319 |         uint256 shares = $.customToken.balanceOf(owner);
 320 |         if (shares == 0) return 0;
 321 | 
 322 |         return _simulateDeconvert(shares, false);
 323 |     }
 324 | 
 325 |     /// @dev Calculates the amount of Custom Token that can be deconverted right now.
 326 |     /// @param shares The maximum amount of Custom Token to simulate deconversion for.
 327 |     /// @param force Whether to revert if the all of the `shares` would not be deconverted.
 328 |     function _simulateDeconvert(uint256 shares, bool force) internal view returns (uint256 deconvertedShares) {
 329 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 330 | 
 331 |         // Check the input.
 332 |         require(shares > 0, InvalidShares());
 333 | 
 334 |         // Switch to the underlying token.
 335 |         uint256 assets = _convertToAssets(shares);
 336 | 
 337 |         // The amount that cannot be converted at the moment.
 338 |         uint256 remainingAssets = assets;
 339 | 
 340 |         // Simulate deconversion.
 341 |         uint256 backingOnSecondaryChain_ = $.backingOnSecondaryChain;
 342 |         if (backingOnSecondaryChain_ >= remainingAssets) return shares;
 343 |         remainingAssets -= backingOnSecondaryChain_;
 344 | 
 345 |         // Calculate the converted amount.
 346 |         uint256 convertedAssets = assets - remainingAssets;
 347 | 
 348 |         // Set the return value (the amount of Custom Token that can be deconverted right now).
 349 |         deconvertedShares = _convertToShares(convertedAssets);
 350 | 
 351 |         // Revert if all of the `shares` must have been deconverted and there is a remaining amount.
 352 |         if (force) require(remainingAssets == 0, AssetsTooLarge(convertedAssets, assets));
 353 |     }
 354 | 
 355 |     /// @notice Burn a specific amount of Custom Token to unlock a respective amount of the underlying token.
 356 |     /// @param shares The amount of Custom Token to deconvert to the underlying token.
 357 |     /// @return assets The amount of the underlying token unlocked to the receiver.
 358 |     function deconvert(uint256 shares, address receiver) external whenNotPaused nonReentrant returns (uint256 assets) {
 359 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 360 |         return _deconvert(shares, $.agglayerId, receiver, false);
 361 |     }
 362 | 
 363 |     /// @notice Burn a specific amount of Custom Token to unlock a respective amount of the underlying token, and bridge it to another network.
 364 |     /// @param shares The amount of Custom Token to deconvert to the underlying token.
 365 |     /// @return assets The amount of the underlying token unlocked to the receiver.
 366 |     function deconvertAndBridge(
 367 |         uint256 shares,
 368 |         address receiver,
 369 |         uint32 destinationNetworkId,
 370 |         bool forceUpdateGlobalExitRoot
 371 |     ) external whenNotPaused nonReentrant returns (uint256 assets) {
 372 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 373 | 
 374 |         // Check the input.
 375 |         require(destinationNetworkId != $.agglayerId, InvalidDestinationNetworkId());
 376 | 
 377 |         return _deconvert(shares, destinationNetworkId, receiver, forceUpdateGlobalExitRoot);
 378 |     }
 379 | 
 380 |     /// @notice Burn a specific amount of Custom Token to unlock a respective amount of the underlying token, and optionally bridge it to another network.
 381 |     /// @param shares The amount of Custom Token to deconvert to the underlying token.
 382 |     /// @return assets The amount of the underlying token unlocked to the receiver.
 383 |     function _deconvert(uint256 shares, uint32 destinationNetworkId, address receiver, bool forceUpdateGlobalExitRoot)
 384 |         internal
 385 |         returns (uint256 assets)
 386 |     {
 387 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 388 | 
 389 |         // Check the inputs.
 390 |         require(shares > 0, InvalidShares());
 391 |         require(receiver != address(0), InvalidReceiver());
 392 | 
 393 |         // Switch to the underlying token.
 394 |         // Set the return value.
 395 |         assets = _convertToAssets(shares);
 396 | 
 397 |         // Get the available backing.
 398 |         uint256 backingOnSecondaryChain_ = backingOnSecondaryChain();
 399 | 
 400 |         // Revert if there is not enough backing.
 401 |         require(backingOnSecondaryChain_ >= assets, AssetsTooLarge(backingOnSecondaryChain_, assets));
 402 | 
 403 |         // Update the backing data.
 404 |         $.backingOnSecondaryChain -= assets;
 405 | 
 406 |         // Burn Custom Token.
 407 |         _burnCustomToken(msg.sender, shares);
 408 | 
 409 |         // Withdraw the underlying token.
 410 |         if (destinationNetworkId == $.agglayerId) {
 411 |             // Withdraw to the receiver.
 412 |             _sendUnderlyingToken(receiver, assets);
 413 |         } else {
 414 |             // Bridge to the receiver.
 415 |             $.bridge
 416 |                 .bridgeAsset(
 417 |                     destinationNetworkId, receiver, assets, address($.underlyingToken), forceUpdateGlobalExitRoot, ""
 418 |                 );
 419 |         }
 420 |     }
 421 | 
 422 |     /// @dev Tells how much a specific amount of underlying token is worth in Custom Token.
 423 |     /// @dev The underlying token backs vbToken 1:1.
 424 |     /// @param assets The amount of the underlying token.
 425 |     /// @return shares The amount of Custom Token.
 426 |     function _convertToShares(uint256 assets) internal pure returns (uint256 shares) {
 427 |         // @note CAUTION! Changing this function will affect the conversion rate for the entire contract, and may introduce bugs.
 428 |         shares = assets;
 429 |     }
 430 | 
 431 |     /// @dev Tells how much a specific amount of Custom Token is worth in the underlying token.
 432 |     /// @dev vbToken is backed by the underlying token 1:1.
 433 |     /// @param shares The amount of Custom Token.
 434 |     /// @return assets The amount of the underlying token.
 435 |     function _convertToAssets(uint256 shares) internal pure returns (uint256 assets) {
 436 |         // @note CAUTION! Changing this function will affect the conversion rate for the entire contract, and may introduce bugs.
 437 |         assets = shares;
 438 |     }
 439 | 
 440 |     // -----================= ::: NATIVE CONVERTER ::: =================-----
 441 | 
 442 |     /// @notice The maximum amount of backing that can be migrated to Primary Chain.
 443 |     function migratableBacking() public view returns (uint256) {
 444 |         NativeConverterStorage storage $ = _getNativeConverterStorage();
 445 | 
 446 |         // Calculate the non-migratable backing