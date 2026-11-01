Title: Missing check in VaultBridgeToken.sol
Severity: High
Risk: Funds at risk due to missing validation
Description: At Line 41 abstract contract. At Line 58 struct.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/VaultBridgeToken.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {IERC4626} from "@openzeppelin/contracts/interfaces/IERC4626.sol";
   8 | import {
   9 |     ERC20PermitUpgradeable
  10 | } from "@openzeppelin-contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
  11 | import {IVaultBridgeTokenInitializer} from "../etc/IVaultBridgeTokenInitializer.sol";
  12 | 
  13 | // Other functionality.
  14 | import {Initializable} from "@openzeppelin-contracts-upgradeable/proxy/utils/Initializable.sol";
  15 | import {AccessControlUpgradeable} from "@openzeppelin-contracts-upgradeable/access/AccessControlUpgradeable.sol";
  16 | import {PausableUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/PausableUpgradeable.sol";
  17 | import {
  18 |     ReentrancyGuardTransientUpgradeable
  19 | } from "@openzeppelin-contracts-upgradeable/utils/ReentrancyGuardTransientUpgradeable.sol";
  20 | import {ERC20PermitUser} from "../etc/ERC20PermitUser.sol";
  21 | import {InitializationCounterUpgradeable} from "../etc/InitializationCounterUpgradeable.sol";
  22 | import {Versioned} from "../etc/Versioned.sol";
  23 | 
  24 | // Libraries.
  25 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  26 | import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
  27 | 
  28 | // External contracts.
  29 | import {IAgglayerBridge} from "../etc/IAgglayerBridge.sol";
  30 | import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
  31 | 
  32 | // Other.
  33 | import {ERC20Upgradeable} from "@openzeppelin-contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
  34 | import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
  35 | 
  36 | /// @title Vault Bridge Token
  37 | /// @author See https://github.com/agglayer/vault-bridge
  38 | /// @notice A vbToken is an ERC-20 token, ERC-4626 vault, and Agglayer Bridge extension, enabling deposits and bridging of select assets, such as WBTC, WETH, USDT, USDC, and USDS, while putting the assets to work to produce yield.
  39 | /// @dev A base contract used to create vbTokens.
  40 | /// @dev @note IMPORTANT: In order to not drive the complexity of the Vault Bridge protocol up, vbToken MUST NOT have transfer, deposit, or withdrawal fees. The underlying token on Primary Chain MUST NOT have a transfer fee; this contract will revert if it detects a transfer fee. The underlying token and Custom Token on Secondary Chains MAY have transfer fees. The yield vault SHOULD NOT have deposit and/or withdrawal fees; however, it is expected that produced yield will offset any costs incurred when depositing to and withdrawing from the yield vault for the purpose of producing yield or rebalancing the internal reserve. The price of the yield vault's shares MUST NOT decrease (e.g., there is no bad debt realization); still, this contract implements solvency checks for protection with a configurable slippage parameter. Additionally, the underlying token MUST NOT be a rebasing token, and MUST NOT have transfer hooks (i.e., does not enable reentrancy/crossentrancy).
  41 | abstract contract VaultBridgeToken is
  42 |     Initializable,
  43 |     AccessControlUpgradeable,
  44 |     PausableUpgradeable,
  45 |     ReentrancyGuardTransientUpgradeable,
  46 |     IERC4626,
  47 |     ERC20PermitUpgradeable,
  48 |     ERC20PermitUser,
  49 |     InitializationCounterUpgradeable,
  50 |     Versioned
  51 | {
  52 |     // Libraries.
  53 |     using SafeERC20 for IERC20;
  54 | 
  55 |     /// @dev Storage of Vault Bridge Token contract.
  56 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  57 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.VaultBridgeToken.storage
  58 |     struct VaultBridgeTokenStorage {
  59 |         IERC20 underlyingToken;
  60 |         uint8 decimals;
  61 |         uint256 minimumReservePercentage;
  62 |         uint256 reservedAssets;
  63 |         IERC4626 yieldVault;
  64 |         address yieldRecipient;
  65 |         uint256 _netCollectedYield;
  66 |         uint32 agglayerId;
  67 |         IAgglayerBridge agglayerBridge;
  68 |         uint256 migrationFeesFund;
  69 |         uint256 minimumYieldVaultDeposit;
  70 |         address migrationManager;
  71 |         uint256 yieldVaultMaximumSlippagePercentage;
  72 |         address _vaultBridgeTokenPart2;
  73 |     }
  74 | 
  75 |     /// @dev Parameters for initializing Vault Bridge Token contract.
  76 |     /// @dev @note (ATTENTION) `decimals` will match the underlying token. Defaults to 18 decimals if the underlying token reverts on `decimals`.
  77 |     /// @param owner (ATTENTION) This address will be granted the `DEFAULT_ADMIN_ROLE`, as well as all basic roles. Roles can be modified at any time.
  78 |     /// @param minimumReservePercentage vbTokens can maintain an internal reserve of the underlying token for serving withdrawals from first (as opposed to staking all assets). `1e18` is 100%. @note (ATTENTION) Automatic reserve rebalancing will be disabled for values greater than `1e18` (100%).
  79 |     /// @param yieldVault An external, ERC-4246 compliant vault into which the underlying token is deposited to produce yield.
  80 |     /// @param yieldRecipient The address that receives yield produced by the yield vault. The yield collector collects yield, while the yield recipient receives it.
  81 |     /// @param minimumYieldVaultDeposit The minimum amount of the underlying token that triggers a yield vault deposit. Amounts below this value will be reserved regardless of the reserve percentage, in order to save gas for users. The limit does not apply when rebalancing the reserve. Set to `0` to disable.
  82 |     /// @param yieldVaultMaximumSlippagePercentage The maximum slippage percentage when depositing into or withdrawing from the yield vault. @note IMPORTANT: Any losses incurred due to slippage (and not fully covered by produced yield) will need to be covered by whomever is responsible for this contract. `1e18` is 100%. The recommended value is `0.01e18` (1%).
  83 |     struct InitializationParameters {
  84 |         address owner;
  85 |         string name;
  86 |         string symbol;
  87 |         address underlyingToken;
  88 |         uint256 minimumReservePercentage;
  89 |         address yieldVault;
  90 |         address yieldRecipient;
  91 |         address agglayerBridge;
  92 |         uint256 minimumYieldVaultDeposit;
  93 |         address migrationManager;
  94 |         uint256 yieldVaultMaximumSlippagePercentage;
  95 |         address vaultBridgeTokenPart2;
  96 |     }
  97 | 
  98 |     // Basic roles.
  99 |     // @remind Document.
 100 |     bytes32 public constant REBALANCER_ROLE = keccak256("REBALANCER_ROLE");
 101 |     bytes32 public constant YIELD_COLLECTOR_ROLE = keccak256("YIELD_COLLECTOR_ROLE");
 102 |     bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
 103 | 
 104 |     /// @dev The storage slot at which Vault Bridge Token storage starts, following the EIP-7201 standard.
 105 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.VaultBridgeToken.storage")) - 1)) & ~bytes32(uint256(0xff))`.
 106 |     bytes32 private constant _VAULT_BRIDGE_TOKEN_STORAGE =
 107 |         hex"f082fbc4cfb4d172ba00d34227e208a31ceb0982bc189440d519185302e44700";
 108 | 
 109 |     // Errors.
 110 |     error Unauthorized();
 111 |     error InvalidInitializer();
 112 |     error InvalidOwner();
 113 |     error InvalidName();
 114 |     error InvalidSymbol();
 115 |     error InvalidUnderlyingToken();
 116 |     error InvalidMinimumReservePercentage();
 117 |     error InvalidYieldVault();
 118 |     error InvalidYieldRecipient();
 119 |     error InvalidAgglayerBridge();
 120 |     error InvalidMigrationManager();
 121 |     error InvalidYieldVaultMaximumSlippagePercentage();
 122 |     error InvalidVaultBridgeTokenPart2();
 123 |     error InvalidAssets();
 124 |     error InvalidDestinationNetworkId();
 125 |     error InvalidReceiver();
 126 |     error InvalidPermitData();
 127 |     error InvalidShares();
 128 |     error IncorrectAmountOfSharesMinted(uint256 mintedShares, uint256 requiredShares);
 129 |     error AssetsTooLarge(uint256 availableAssets, uint256 requestedAssets);
 130 |     error IncorrectAmountOfSharesRedeemed(uint256 redeemedShares, uint256 requiredShares);
 131 |     error CannotRebalanceReserve();
 132 |     error NoNeedToRebalanceReserve();
 133 |     error NoYield();
 134 |     error InvalidOriginNetwork();
 135 |     error CannotCompleteMigration(uint256 requiredAssets, uint256 receivedAssets, uint256 assetsInMigrationFund);
 136 |     error YieldVaultRedemptionFailed(uint256 sharesToRedeem, uint256 redemptionLimit);
 137 |     error MinimumYieldVaultDepositNotMet(uint256 assetsToDeposit, uint256 minimumYieldVaultDeposit);
 138 |     error YieldVaultDepositFailed(uint256 assetsToDeposit, uint256 depositLimit);
 139 |     error InsufficientYieldVaultSharesMinted(uint256 depositedAssets, uint256 mintedShares);
 140 |     error UnknownError(bytes data);
 141 |     error YieldVaultWithdrawalFailed(uint256 assetsToWithdraw, uint256 withdrawalLimit);
 142 |     error ExcessiveYieldVaultSharesBurned(uint256 burnedShares, uint256 withdrawnAssets);
 143 |     error InsufficientUnderlyingTokenReceived(uint256 receivedAssets, uint256 requestedAssets);
 144 |     error UnknownFunction(bytes4 functionSelector);
 145 | 
 146 |     // Events.
 147 |     event ReserveRebalanced(uint256 oldReservedAssets, uint256 newReservedAssets, uint256 reservePercentage);
 148 |     event YieldCollected(address indexed yieldRecipient, uint256 vbTokenAmount);
 149 |     event Burned(uint256 vbTokenAmount);
 150 |     event DonatedAsYield(address indexed who, uint256 assets);
 151 |     event DonatedForCompletingMigration(address indexed who, uint256 assets);
 152 |     event MigrationCompleted(
 153 |         uint32 indexed originNetwork,
 154 |         uint256 indexed shares,
 155 |         uint256 indexed assets,
 156 |         uint256 migrationFeesFundUtilization
 157 |     );
 158 |     event YieldRecipientSet(address indexed yieldRecipient);
 159 |     event MinimumReservePercentageSet(uint256 minimumReservePercentage);
 160 |     event YieldVaultDrained(uint256 redeemedShares, uint256 receivedAssets);
 161 |     event YieldVaultSet(address yieldVault);
 162 |     event YieldVaultMaximumSlippagePercentageSet(uint256 slippagePercentage);
 163 | 
 164 |     // -----================= ::: MODIFIERS ::: =================-----
 165 | 
 166 |     /// @dev Checks if the sender is the yield recipient.
 167 |     modifier onlyYieldRecipient() {
 168 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 169 |         require(msg.sender == $.yieldRecipient, Unauthorized());
 170 |         _;
 171 |     }
 172 | 
 173 |     /// @dev Checks if the sender is Migration Manager.
 174 |     modifier onlyMigrationManager() {
 175 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 176 |         require(msg.sender == $.migrationManager, Unauthorized());
 177 |         _;
 178 |     }
 179 | 
 180 |     /// @dev Checks if the sender is the vbToken itself.
 181 |     modifier onlySelf() {
 182 |         require(msg.sender == address(this), Unauthorized());
 183 |         _;
 184 |     }
 185 | 
 186 |     /// @dev Delegates the call to `VaultBridgeTokenPart2`.
 187 |     modifier delegatedToPart2() {
 188 |         _;
 189 |         _delegateToPart2();
 190 |     }
 191 | 
 192 |     // -----================= ::: SETUP ::: =================-----
 193 | 
 194 |     /// @param initializer_ The address of `VaultBridgeTokenInitializer`.
 195 |     /// @param initParams Please refer to `InitializationParameters` for more information.
 196 |     function __VaultBridgeToken_init1(address initializer_, InitializationParameters calldata initParams)
 197 |         internal
 198 |         onlyInitializing
 199 |     {
 200 |         // Check the input.
 201 |         require(initializer_ != address(0), InvalidInitializer());
 202 | 
 203 |         // Verify the version of the initializer.
 204 |         // The version string must be the same as that of this contract.
 205 |         require(
 206 |             keccak256(bytes(VaultBridgeToken(initializer_).VAULT_BRIDGE_PROTOCOL()))
 207 |                 == keccak256(bytes(VAULT_BRIDGE_PROTOCOL())),
 208 |             InvalidInitializer()
 209 |         );
 210 | 
 211 |         // Initialize the contract using the external initializer.
 212 |         (bool ok, bytes memory data) =
 213 |             initializer_.delegatecall(abi.encodeCall(IVaultBridgeTokenInitializer.init1, (initParams)));
 214 | 
 215 |         // Check the result.
 216 |         if (!ok) {
 217 |             // If the call failed, bubble up the revert data.
 218 |             assembly ("memory-safe") {
 219 |                 revert(add(32, data), mload(data))
 220 |             }
 221 |         }
 222 |     }
 223 | 
 224 |     // @remind Document.
 225 |     function __VaultBridgeToken_init2()
 226 |         internal
 227 |         onlyInitializing
 228 |         incrementsLocalInitializationCounter(1)
 229 |         incrementsLocalInitializationCounter(2)
 230 |     {
 231 |         // Empty function body.
 232 |     }
 233 | 
 234 |     /*
 235 |     /// @dev How to add a new init step:
 236 |     function __VaultBridgeToken_init3() internal onlyInitializing incrementsLocalInitializationCounter(3) {}
 237 |     */
 238 | 
 239 |     // @remind Document.
 240 |     function _VAULT_BRIDGE_TOKEN_INIT_2_COMPATIBLE() internal pure virtual;
 241 | 
 242 |     // -----================= ::: STORAGE ::: =================-----
 243 | 
 244 |     /// @notice The underlying token that backs vbToken.
 245 |     function underlyingToken() public view returns (IERC20) {
 246 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 247 |         return $.underlyingToken;
 248 |     }
 249 | 
 250 |     /// @notice The number of decimals of vbToken.
 251 |     /// @notice The number of decimals is the same as that of the underlying token, or `18` if the underlying token reverted on `decimals`.
 252 |     function decimals() public view override(ERC20Upgradeable, IERC20Metadata) returns (uint8) {
 253 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 254 |         return $.decimals;
 255 |     }
 256 | 
 257 |     /// @notice vbTokens can maintain an internal reserve of the underlying token for serving withdrawals from first (as opposed to staking all assets).
 258 |     /// @notice The owner can rebalance the reserve by calling `rebalanceReserve` when it is below or above the `minimumReservePercentage`. The reserve may also be rebalanced automatically on deposits and withdrawals.
 259 |     /// @return 1e18 is 100%.
 260 |     function minimumReservePercentage() public view returns (uint256) {
 261 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 262 |         return $.minimumReservePercentage;
 263 |     }
 264 | 
 265 |     /// @notice vbTokens can maintain an internal reserve of the underlying token for serving withdrawals from first (as opposed to staking all assets).
 266 |     /// @notice How much of the underlying token is in the internal reserve.
 267 |     function reservedAssets() public view returns (uint256) {
 268 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 269 |         return $.reservedAssets;
 270 |     }
 271 | 
 272 |     /// @notice An external, ERC-4246 compliant vault into which the underlying token is deposited to produce yield.
 273 |     function yieldVault() public view returns (IERC4626) {
 274 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 275 |         return $.yieldVault;
 276 |     }
 277 | 
 278 |     /// @notice The address that receives yield produced by the yield vault.
 279 |     /// @notice The yield collector collects yield, while the yield recipient receives it.
 280 |     function yieldRecipient() public view returns (address) {
 281 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 282 |         return $.yieldRecipient;
 283 |     }
 284 | 
 285 |     /// @notice The Agglayer ID of this network.
 286 |     function agglayerId() public view returns (uint32) {
 287 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 288 |         return $.agglayerId;
 289 |     }
 290 | 
 291 |     /// @notice Agglayer Bridge, which connects AggLayer networks.
 292 |     function agglayerBridge() public view returns (IAgglayerBridge) {
 293 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 294 |         return $.agglayerBridge;
 295 |     }
 296 | 
 297 |     /// @notice A dedicated fund for covering any fees on Secondary Chain during a migration of backing to Primary Chain. Please refer to `completeMigration` for more information.
 298 |     function migrationFeesFund() public view returns (uint256) {
 299 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 300 |         return $.migrationFeesFund;
 301 |     }
 302 | 
 303 |     /// @notice The minimum amount of the underlying token that triggers a yield vault deposit.
 304 |     /// @dev Amounts below this value will be reserved regardless of the reserve percentage, in order to save gas for users.
 305 |     /// @dev The limit does not apply when rebalancing the reserve.
 306 |     function minimumYieldVaultDeposit() public view returns (uint256) {
 307 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 308 |         return $.minimumYieldVaultDeposit;
 309 |     }
 310 | 
 311 |     /// @notice The address of Migration Manager. Please refer to `MigrationManager.sol` for more information.
 312 |     function migrationManager() public view returns (address) {
 313 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 314 |         return $.migrationManager;
 315 |     }
 316 | 
 317 |     /// @notice The maximum slippage percentage when depositing into or withdrawing from the yield vault.
 318 |     /// @return 1e18 is 100%.
 319 |     function yieldVaultMaximumSlippagePercentage() public view returns (uint256) {
 320 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 321 |         return $.yieldVaultMaximumSlippagePercentage;
 322 |     }
 323 | 
 324 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
 325 |     function _getVaultBridgeTokenStorage() private pure returns (VaultBridgeTokenStorage storage $) {
 326 |         assembly {
 327 |             $.slot := _VAULT_BRIDGE_TOKEN_STORAGE
 328 |         }
 329 |     }
 330 | 
 331 |     // -----================= ::: ERC-4626 ::: =================-----
 332 | 
 333 |     /// @notice The underlying token that backs vbToken.
 334 |     function asset() public view returns (address assetTokenAddress) {
 335 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 336 |         return address($.underlyingToken);
 337 |     }
 338 | 
 339 |     /// @notice The total backing of vbToken in the underlying token in real-time.
 340 |     function totalAssets() public view returns (uint256 totalManagedAssets) {
 341 |         return stakedAssets() + reservedAssets();
 342 |     }
 343 | 
 344 |     /// @notice Tells how much a specific amount of underlying token is worth in vbToken.
 345 |     /// @dev The underlying token backs vbToken 1:1.
 346 |     function convertToShares(uint256 assets) public pure returns (uint256 shares) {
 347 |         // @note CAUTION! Changing this function will affect the conversion rate for the entire contract, and may introduce bugs.
 348 |         shares = assets;
 349 |     }
 350 | 
 351 |     /// @notice Tells how much a specific amount of vbToken is worth in the underlying token.
 352 |     /// @dev vbToken is backed by the underlying token 1:1.
 353 |     function convertToAssets(uint256 shares) public pure returns (uint256 assets) {
 354 |         // @note CAUTION! Changing this function will affect the conversion rate for the entire contract, and may introduce bugs.
 355 |         assets = shares;
 356 |     }
 357 | 
 358 |     /// @notice How much underlying token can deposited for a specific user right now. (Depositing the underlying token mints vbToken).
 359 |     function maxDeposit(address) external view returns (uint256 maxAssets) {
 360 |         return paused() ? 0 : type(uint256).max;
 361 |     }
 362 | 
 363 |     /// @notice How much vbToken would be minted if a specific amount of the underlying token were deposited right now.
 364 |     function previewDeposit(uint256 assets) external view whenNotPaused returns (uint256 shares) {
 365 |         // Check the input.
 366 |         require(assets > 0, InvalidAssets());
 367 | 
 368 |         return convertToShares(assets);
 369 |     }
 370 | 
 371 |     /// @notice Deposit a specific amount of the underlying token and mint vbToken.
 372 |     function deposit(uint256 assets, address receiver) external whenNotPaused nonReentrant returns (uint256 shares) {
 373 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 374 |         (shares,) = _deposit(assets, $.agglayerId, receiver, false, 0);
 375 |     }
 376 | 
 377 |     /// @notice Deposit a specific amount of the underlying token, and bridge minted vbToken to another network.
 378 |     /// @dev The `receiver` in the ERC-4626 `Deposit` event will be this contract.
 379 |     function depositAndBridge(
 380 |         uint256 assets,
 381 |         address receiver,
 382 |         uint32 destinationNetworkId,
 383 |         bool forceUpdateGlobalExitRoot
 384 |     ) external whenNotPaused nonReentrant returns (uint256 shares) {
 385 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 386 | 
 387 |         // Check the input.
 388 |         require(destinationNetworkId != $.agglayerId, InvalidDestinationNetworkId());
 389 | 
 390 |         (shares,) = _deposit(assets, destinationNetworkId, receiver, forceUpdateGlobalExitRoot, 0);
 391 |     }
 392 | 
 393 |     /// @notice Locks the underlying token, mints vbToken, and optionally bridges it to another network.
 394 |     /// @param maxShares Caps the amount of vbToken that is minted. Unused underlying token will be refunded to the sender. Set to `0` to disable.
 395 |     /// @dev If bridging to another network, the `receiver` in the ERC-4626 `Deposit` event will be this contract.
 396 |     function _deposit(
 397 |         uint256 assets,
 398 |         uint32 destinationNetworkId,
 399 |         address receiver,
 400 |         bool forceUpdateGlobalExitRoot,
 401 |         uint256 maxShares
 402 |     ) internal returns (uint256 shares, uint256 spentAssets) {
 403 |         return _depositUsingCustomReceivingFunction(
 404 |             _receiveUnderlyingToken, assets, destinationNetworkId, receiver, forceUpdateGlobalExitRoot, maxShares
 405 |         );
 406 |     }
 407 | 
 408 |     /// @notice Locks the underlying token, mints vbToken, and optionally bridges it to another network.
 409 |     /// @param receiveUnderlyingToken A custom function to use for receiving the underlying token from the sender. @note CAUTION! This function MUST NOT introduce reentrancy/crossentrancy vulnerabilities. @note IMPORTANT: The function MUST detect and revert if there was a transfer fee.
 410 |     /// @param maxShares Caps the amount of vbToken that is minted. Unused underlying token will be refunded to the sender. Set to `0` to disable.
 411 |     /// @dev If bridging to another network, the `receiver` in the ERC-4626 `Deposit` event will be this contract.
 412 |     function _depositUsingCustomReceivingFunction(
 413 |         function(address, uint256) internal receiveUnderlyingToken,
 414 |         uint256 assets,
 415 |         uint32 destinationNetworkId,
 416 |         address receiver,
 417 |         bool forceUpdateGlobalExitRoot,
 418 |         uint256 maxShares
 419 |     ) internal returns (uint256 shares, uint256 spentAssets) {
 420 |         VaultBridgeTokenStorage storage $ = _getVaultBridgeTokenStorage();
 421 | 
 422 |         // Check the inputs.
 423 |         require(assets > 0, InvalidAssets());
 424 |         require(receiver != address(0), InvalidReceiver());
 425 |         require(receiver != address(this), InvalidReceiver());
 426 | 
 427 |         // Transfer the underlyi