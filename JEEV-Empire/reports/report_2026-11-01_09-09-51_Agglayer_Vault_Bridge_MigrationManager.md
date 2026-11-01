Title: Missing disableInitializers in MigrationManager.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/MigrationManager.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | /// @dev Main functionality.
   7 | import {IBridgeMessageReceiver} from "../etc/IBridgeMessageReceiver.sol";
   8 | 
   9 | /// @dev Other functionality.
  10 | import {Initializable} from "@openzeppelin-contracts-upgradeable/proxy/utils/Initializable.sol";
  11 | import {AccessControlUpgradeable} from "@openzeppelin-contracts-upgradeable/access/AccessControlUpgradeable.sol";
  12 | import {PausableUpgradeable} from "@openzeppelin-contracts-upgradeable/utils/PausableUpgradeable.sol";
  13 | import {
  14 |     ReentrancyGuardTransientUpgradeable
  15 | } from "@openzeppelin-contracts-upgradeable/utils/ReentrancyGuardTransientUpgradeable.sol";
  16 | import {InitializationCounterUpgradeable} from "../etc/InitializationCounterUpgradeable.sol";
  17 | import {Versioned} from "../etc/Versioned.sol";
  18 | 
  19 | /// @dev Libraries.
  20 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  21 | 
  22 | /// @dev External contracts.
  23 | import {VaultBridgeToken} from "./VaultBridgeToken.sol";
  24 | import {IAgglayerBridge} from "../etc/IAgglayerBridge.sol";
  25 | import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
  26 | import {IWETH9} from "../etc/IWETH9.sol";
  27 | 
  28 | /// @title Migration Manager (singleton)
  29 | /// @author See https://github.com/agglayer/vault-bridge
  30 | /// @notice Migration Manager is a singleton contract on Primary Chain.
  31 | /// @notice Backing for Custom Tokens minted by Native Converters on Secondary Chains can be migrated to Migration Manager on Primary Chain. Migration Manager completes migrations by calling `completeMigration` on the corresponidng vbToken, which mints vbToken and bridges it to address zero on the Secondary Chains, effectively locking the backing in Agglayer Bridge. Please refer to `onMessageReceived` for more information.
  32 | /// @dev This contract exists to prevent manipulation of vbTokens' internal accounting through reentrancy (specifically, claiming assets on Agglayer Bridge to vbToken mid-execution).
  33 | contract MigrationManager is
  34 |     IBridgeMessageReceiver,
  35 |     Initializable,
  36 |     AccessControlUpgradeable,
  37 |     PausableUpgradeable,
  38 |     ReentrancyGuardTransientUpgradeable,
  39 |     InitializationCounterUpgradeable,
  40 |     Versioned
  41 | {
  42 |     // Libraries.
  43 |     using SafeERC20 for IERC20;
  44 | 
  45 |     /// @dev Used in cross-chain communication.
  46 |     enum CrossChainInstruction {
  47 |         _0_COMPLETE_MIGRATION,
  48 |         _1_WRAP_GAS_TOKEN_AND_COMPLETE_MIGRATION
  49 |     }
  50 | 
  51 |     /// @dev Used for mapping Native Converters to vbTokens.
  52 |     struct TokenPair {
  53 |         VaultBridgeToken vbToken;
  54 |         IERC20 underlyingToken;
  55 |     }
  56 | 
  57 |     /// @dev Storage of the Migration Manager contract.
  58 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  59 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.MigrationManager.storage
  60 |     struct MigrationManagerStorage {
  61 |         IAgglayerBridge agglayerBridge;
  62 |         uint32 _agglayerId;
  63 |         mapping(uint32 secondaryChainAgglayerId => mapping(address nativeConverter => TokenPair tokenPair))
  64 |             nativeConvertersConfiguration;
  65 |         IWETH9 _wrappedGasToken;
  66 |     }
  67 | 
  68 |     /// @dev The storage slot at which Migration Manager storage starts, following the EIP-7201 standard.
  69 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.MigrationManager.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  70 |     bytes32 private constant _MIGRATION_MANAGER_STORAGE =
  71 |         hex"30cf29e424d82bdf294fbec113ef39ac73137edfdb802b37ef3fc9ad433c5000";
  72 | 
  73 |     // Basic roles.
  74 |     // @remind Document.
  75 |     bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
  76 | 
  77 |     // Errors.
  78 |     error InvalidOwner();
  79 |     error InvalidAgglayerBridge();
  80 |     error InvalidWrappedGasToken();
  81 |     error NonMatchingInputLengths();
  82 |     error InvalidSecondaryChainAgglayerId();
  83 |     error InvalidNativeConverter();
  84 |     error InvalidUnderlyingToken();
  85 |     error Unauthorized();
  86 |     error InsufficientUnderlyingTokenBalanceAfterWrapping(uint256 newBalance, uint256 expectedBalance);
  87 | 
  88 |     // Events.
  89 |     event NativeConverterConfigured(
  90 |         uint32 indexed secondaryChainAgglayerId, address indexed nativeConverter, address indexed vbToken
  91 |     );
  92 | 
  93 |     // -----================= ::: MODIFIERS ::: =================-----
  94 | 
  95 |     /// @dev Checks if the sender is Agglayer Bridge.
  96 |     modifier onlyAgglayerBridge() {
  97 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
  98 |         require(msg.sender == address($.agglayerBridge), Unauthorized());
  99 |         _;
 100 |     }
 101 | 
 102 |     // -----================= ::: SOLIDITY ::: =================-----
 103 | 
 104 |     receive() external payable {}
 105 | 
 106 |     // -----================= ::: SETUP ::: =================-----
 107 | 
 108 |     constructor() {
 109 |         _disableInitializers();
 110 |     }
 111 | 
 112 |     /// @notice Initializes the Migration Manager contract.
 113 |     /// @param owner_ (ATTENTION) This address will be granted the `DEFAULT_ADMIN_ROLE`, as well as all basic roles. Roles can be modified at any time.
 114 |     function reinitialize1(address owner_, address agglayerBridge_) external reinitializer(1) nonReentrant {
 115 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 116 | 
 117 |         // Check the inputs.
 118 |         require(owner_ != address(0), InvalidOwner());
 119 |         require(agglayerBridge_ != address(0), InvalidAgglayerBridge());
 120 | 
 121 |         // Initialize the inherited contracts.
 122 |         __AccessControl_init();
 123 |         __Pausable_init();
 124 |         __ReentrancyGuardTransient_init();
 125 |         __Context_init();
 126 |         __ERC165_init();
 127 | 
 128 |         // Grant the basic roles.
 129 |         _grantRole(DEFAULT_ADMIN_ROLE, owner_);
 130 |         _grantRole(PAUSER_ROLE, owner_);
 131 | 
 132 |         // Initialize the storage.
 133 |         $.agglayerBridge = IAgglayerBridge(agglayerBridge_);
 134 |         $._agglayerId = $.agglayerBridge.networkID();
 135 |     }
 136 | 
 137 |     // @remind Document (the entire function).
 138 |     /// @param wrappedGasToken_ The address of the wrapped gas token (e.g., WETH, if the gas token is ETH). Must be the same as the underlying token of the corresponding vbToken (e.g., of vbETH, if the gas token is ETH).
 139 |     function reinitialize2(address wrappedGasToken_) external reinitializer(2) nonReentrant {
 140 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 141 | 
 142 |         _incrementGlobalInitializationCounter(1);
 143 |         _incrementGlobalInitializationCounter(2);
 144 | 
 145 |         require(wrappedGasToken_ != address(0), InvalidWrappedGasToken());
 146 | 
 147 |         $._wrappedGasToken = IWETH9(wrappedGasToken_);
 148 |     }
 149 | 
 150 |     /*
 151 |     /// @dev How to add a new reinitializer:
 152 |     function reinitialize3()
 153 |         external
 154 |         reinitializer(_incrementGlobalInitializationCounter(3))
 155 |         nonReentrant
 156 |     {}
 157 |     */
 158 | 
 159 |     // @remind Document (the entire function).
 160 |     function reinitialize(bytes[] calldata reinitializeData) external {
 161 |         bytes4[] memory reinitializeSelectors = new bytes4[](2);
 162 | 
 163 |         reinitializeSelectors[0] = this.reinitialize1.selector;
 164 |         reinitializeSelectors[1] = this.reinitialize2.selector;
 165 | 
 166 |         _reinitialize(reinitializeSelectors, reinitializeData);
 167 |     }
 168 | 
 169 |     // -----================= ::: STORAGE ::: =================-----
 170 | 
 171 |     /// @notice Agglayer Bridge, which connects AggLayer networks.
 172 |     function agglayerBridge() public view returns (IAgglayerBridge) {
 173 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 174 |         return $.agglayerBridge;
 175 |     }
 176 | 
 177 |     /// @notice Tells which vbToken Native Converter on Secondary Chain belongs to.
 178 |     /// @param secondaryChainAgglayerId Secondary Chain's Agglayer ID.
 179 |     /// @param nativeConverter The address of Native Converter on Secondary Chain.
 180 |     function nativeConvertersConfiguration(uint32 secondaryChainAgglayerId, address nativeConverter)
 181 |         public
 182 |         view
 183 |         returns (TokenPair memory tokenPair)
 184 |     {
 185 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 186 |         return $.nativeConvertersConfiguration[secondaryChainAgglayerId][nativeConverter];
 187 |     }
 188 | 
 189 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
 190 |     function _getMigrationManagerStorage() private pure returns (MigrationManagerStorage storage $) {
 191 |         assembly {
 192 |             $.slot := _MIGRATION_MANAGER_STORAGE
 193 |         }
 194 |     }
 195 | 
 196 |     // -----================= ::: MIGRATION MANAGER ::: =================-----
 197 | 
 198 |     /// @notice Maps Native Converters on Secondary Chains to vbToken and underlying token on Primary Chain.
 199 |     /// @dev CAUTION! Misconfiguration could allow an attacker to gain unauthorized access to vbToken and other contracts.
 200 |     /// @notice This function can be called by the owner only.
 201 |     /// @param secondaryChainAgglayerIds The Secondary Chains' Agglayer IDs.
 202 |     /// @param nativeConverters The addresses of Native Converters on Secondary Chains.
 203 |     /// @param vbToken The address of vbToken on Primary Chain Native Converter belongs to. Set to address zero to unset the tokens. You can override tokens without unsetting them first.
 204 |     function configureNativeConverters(
 205 |         uint32[] calldata secondaryChainAgglayerIds,
 206 |         address[] calldata nativeConverters,
 207 |         address payable vbToken
 208 |     ) external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 209 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 210 | 
 211 |         // Check the inputs.
 212 |         require(secondaryChainAgglayerIds.length == nativeConverters.length, NonMatchingInputLengths());
 213 | 
 214 |         // Cache Primary Chain Agglayer ID.
 215 |         uint32 agglayerId = $._agglayerId;
 216 | 
 217 |         for (uint256 i; i < secondaryChainAgglayerIds.length; ++i) {
 218 |             // Cache the inputs.
 219 |             uint32 secondaryChainAgglayerId = secondaryChainAgglayerIds[i];
 220 |             address nativeConverter = nativeConverters[i];
 221 | 
 222 |             // Check the inputs.
 223 |             require(secondaryChainAgglayerId != agglayerId, InvalidSecondaryChainAgglayerId());
 224 |             require(nativeConverter != address(0), InvalidNativeConverter());
 225 | 
 226 |             // Cache the current tokens.
 227 |             TokenPair memory oldTokens = $.nativeConvertersConfiguration[secondaryChainAgglayerId][nativeConverter];
 228 | 
 229 |             // Set or override tokens.
 230 |             /* Set tokens. */
 231 |             if (vbToken != address(0)) {
 232 |                 // Cache the tokens.
 233 |                 IERC20 underlyingToken = VaultBridgeToken(vbToken).underlyingToken();
 234 | 
 235 |                 // Check the input.
 236 |                 require(address(underlyingToken) != address(0), InvalidUnderlyingToken());
 237 | 
 238 |                 // Revoke the approval of the old vbToken if tokens were already set.
 239 |                 if (address(oldTokens.vbToken) != address(0)) {
 240 |                     oldTokens.underlyingToken.forceApprove(address(oldTokens.vbToken), 0);
 241 |                 }
 242 | 
 243 |                 // Set the tokens.
 244 |                 $.nativeConvertersConfiguration[secondaryChainAgglayerId][nativeConverter] =
 245 |                     TokenPair(VaultBridgeToken(vbToken), underlyingToken);
 246 | 
 247 |                 // Approve vbToken.
 248 |                 underlyingToken.forceApprove(vbToken, type(uint256).max);
 249 |             }
 250 |             /* Unset tokens. */
 251 |             else {
 252 |                 // Revoke the approval of vbToken.
 253 |                 oldTokens.underlyingToken.forceApprove(address(oldTokens.vbToken), 0);
 254 | 
 255 |                 // Unset the tokens.
 256 |                 delete $.nativeConvertersConfiguration[secondaryChainAgglayerId][nativeConverter];
 257 |             }
 258 | 
 259 |             // Emit the event.
 260 |             emit NativeConverterConfigured(secondaryChainAgglayerId, nativeConverter, vbToken);
 261 |         }
 262 |     }
 263 | 
 264 |     /// @dev When Native Converter migrates backing, it calls both `bridgeAsset` and `bridgeMessage` on Agglayer Bridge to `migrateBackingToPrimaryChain`.
 265 |     /// @dev The asset must be claimed before the message on Agglayer Bridge.
 266 |     /// @dev The message tells vbToken how much Custom Token must be backed by vbToken, which is minted and bridged to address zero on the respective Secondary Chain. This action provides liquidity when bridging Custom Token to from Secondary Chains to Primary Chain and increments the pessimistic proof.
 267 |     /// @dev This function can be called by Agglayer Bridge only.
 268 |     function onMessageReceived(address originAddress, uint32 originNetwork, bytes memory data)
 269 |         external
 270 |         payable
 271 |         whenNotPaused
 272 |         onlyAgglayerBridge
 273 |         nonReentrant
 274 |     {
 275 |         MigrationManagerStorage storage $ = _getMigrationManagerStorage();
 276 | 
 277 |         // Decode the cross-chain instruction.
 278 |         (CrossChainInstruction instruction, bytes memory instructionData) =
 279 |             abi.decode(data, (CrossChainInstruction, bytes));
 280 | 
 281 |         // Dispatch.
 282 |         /* Complete migration. */
 283 |         if (
 284 |             instruction == CrossChainInstruction._0_COMPLETE_MIGRATION
 285 |                 || instruction == CrossChainInstruction._1_WRAP_GAS_TOKEN_AND_COMPLETE_MIGRATION
 286 |         ) {
 287 |             // Cache vbToken.
 288 |             VaultBridgeToken vbToken = $.nativeConvertersConfiguration[originNetwork][originAddress].vbToken;
 289 | 
 290 |             // Check the input.
 291 |             require(address(vbToken) != address(0), Unauthorized());
 292 | 
 293 |             // Decode the amounts.
 294 |             (uint256 shares, uint256 assets) = abi.decode(instructionData, (uint256, uint256));
 295 | 
 296 |             // Wrap the gas token if instructed.
 297 |             if (instruction == CrossChainInstruction._1_WRAP_GAS_TOKEN_AND_COMPLETE_MIGRATION) {
 298 |                 // Cache the underlying token.
 299 |                 IERC20 underlyingToken = $.nativeConvertersConfiguration[originNetwork][originAddress].underlyingToken;
 300 | 
 301 |                 // Check the input.
 302 |                 require(address(underlyingToken) == address($._wrappedGasToken), Unauthorized());
 303 | 
 304 |                 // Cache the previous balance.
 305 |                 uint256 previousBalance = underlyingToken.balanceOf(address(this));
 306 | 
 307 |                 // Wrap the gas token.
 308 |                 $._wrappedGasToken.deposit{value: assets}();
 309 | 
 310 |                 // Cache the result.
 311 |                 uint256 expectedBalance = previousBalance + assets;
 312 |                 uint256 newBalance = underlyingToken.balanceOf(address(this));
 313 | 
 314 |                 // Check the result.
 315 |                 require(
 316 |                     newBalance == expectedBalance,
 317 |                     InsufficientUnderlyingTokenBalanceAfterWrapping(newBalance, expectedBalance)
 318 |                 );
 319 |             }
 320 | 
 321 |             // Complete the migration.
 322 |             vbToken.completeMigration(originNetwork, shares, assets);
 323 |         }
 324 |     }
 325 | 
 326 |     // -----================= ::: ADMIN ::: =================-----
 327 | 
 328 |     /// @notice Prevents usage of functions with the `whenNotPaused` modifier.
 329 |     /// @notice This function can be called by the owner only.
 330 |     function pause() external onlyRole(PAUSER_ROLE) nonReentrant {
 331 |         _pause();
 332 |     }
 333 | 
 334 |     /// @notice Allows usage of functions with the `whenNotPaused` modifier.
 335 |     /// @notice This function can be called by the owner only.
 336 |     function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) nonReentrant {
 337 |         _unpause();
 338 |     }
 339 | }
 340 | 