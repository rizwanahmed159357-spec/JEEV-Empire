Title: Missing disableInitializers in VaultBridgeTokenInitializer.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/VaultBridgeTokenInitializer.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {IVaultBridgeTokenInitializer} from "../etc/IVaultBridgeTokenInitializer.sol";
   8 | import {VaultBridgeToken} from "./VaultBridgeToken.sol";
   9 | 
  10 | // Libraries.
  11 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  12 | 
  13 | // External contracts.
  14 | import {IERC20Metadata} from "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
  15 | import {IERC4626} from "@openzeppelin/contracts/interfaces/IERC4626.sol";
  16 | import {IAgglayerBridge} from "../etc/IAgglayerBridge.sol";
  17 | import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
  18 | 
  19 | /// @title Vault Bridge Token Initializer (singleton)
  20 | /// @author See https://github.com/agglayer/vault-bridge
  21 | /// @notice A singleton contract used by Vault Bridge Token for initialization.
  22 | /// @dev This contract exists because of the contract size limit of the EVM.
  23 | contract VaultBridgeTokenInitializer is IVaultBridgeTokenInitializer, VaultBridgeToken {
  24 |     // Libraries.
  25 |     using SafeERC20 for IERC20;
  26 | 
  27 |     /// @dev The storage slot at which Vault Bridge Token storage starts, following the EIP-7201 standard.
  28 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.VaultBridgeToken.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  29 |     bytes32 private constant _VAULT_BRIDGE_TOKEN_STORAGE =
  30 |         hex"f082fbc4cfb4d172ba00d34227e208a31ceb0982bc189440d519185302e44700";
  31 | 
  32 |     // -----================= ::: SETUP ::: =================-----
  33 | 
  34 |     constructor() {
  35 |         _disableInitializers();
  36 |     }
  37 | 
  38 |     // -----================= ::: STORAGE ::: =================-----
  39 | 
  40 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
  41 |     function __getVaultBridgeTokenStorage() private pure returns (VaultBridgeTokenStorage storage $) {
  42 |         assembly {
  43 |             $.slot := _VAULT_BRIDGE_TOKEN_STORAGE
  44 |         }
  45 |     }
  46 | 
  47 |     // -----================= ::: VAULT BRIDGE TOKEN ::: =================-----
  48 | 
  49 |     /// @inheritdoc IVaultBridgeTokenInitializer
  50 |     function init1(VaultBridgeToken.InitializationParameters calldata initParams) external override onlyInitializing {
  51 |         VaultBridgeTokenStorage storage $ = __getVaultBridgeTokenStorage();
  52 | 
  53 |         // Check the inputs.
  54 |         require(initParams.owner != address(0), InvalidOwner());
  55 |         require(bytes(initParams.name).length > 0, InvalidName());
  56 |         require(bytes(initParams.symbol).length > 0, InvalidSymbol());
  57 |         require(initParams.underlyingToken != address(0), InvalidUnderlyingToken());
  58 |         require(initParams.minimumReservePercentage <= 1e18, InvalidMinimumReservePercentage());
  59 |         require(initParams.yieldVault != address(0), InvalidYieldVault());
  60 |         require(initParams.yieldRecipient != address(0), InvalidYieldRecipient());
  61 |         require(initParams.agglayerBridge != address(0), InvalidAgglayerBridge());
  62 |         require(initParams.migrationManager != address(0), InvalidMigrationManager());
  63 |         require(initParams.yieldVaultMaximumSlippagePercentage <= 1e18, InvalidYieldVaultMaximumSlippagePercentage());
  64 |         require(initParams.vaultBridgeTokenPart2 != address(0), InvalidVaultBridgeTokenPart2());
  65 |         require(
  66 |             keccak256(bytes(VaultBridgeToken(initParams.vaultBridgeTokenPart2).VAULT_BRIDGE_PROTOCOL()))
  67 |                 == keccak256(bytes(VAULT_BRIDGE_PROTOCOL())),
  68 |             InvalidVaultBridgeTokenPart2()
  69 |         );
  70 | 
  71 |         // Initialize the inherited contracts.
  72 |         __ERC20_init(initParams.name, initParams.symbol);
  73 |         __ERC20Permit_init(initParams.name);
  74 |         __AccessControl_init();
  75 |         __Pausable_init();
  76 |         __ReentrancyGuardTransient_init();
  77 |         __Context_init();
  78 |         __ERC165_init();
  79 |         __Nonces_init();
  80 | 
  81 |         // Grant the basic roles.
  82 |         _grantRole(DEFAULT_ADMIN_ROLE, initParams.owner);
  83 |         _grantRole(REBALANCER_ROLE, initParams.owner);
  84 |         _grantRole(YIELD_COLLECTOR_ROLE, initParams.owner);
  85 |         _grantRole(PAUSER_ROLE, initParams.owner);
  86 | 
  87 |         // Initialize the storage.
  88 |         $.underlyingToken = IERC20(initParams.underlyingToken);
  89 |         try IERC20Metadata(initParams.underlyingToken).decimals() returns (uint8 decimals_) {
  90 |             $.decimals = decimals_;
  91 |         } catch {
  92 |             // Default to 18 decimals if the underlying token reverted.
  93 |             $.decimals = 18;
  94 |         }
  95 |         $.minimumReservePercentage = initParams.minimumReservePercentage;
  96 |         $.yieldVault = IERC4626(initParams.yieldVault);
  97 |         $.yieldRecipient = initParams.yieldRecipient;
  98 |         $.agglayerId = IAgglayerBridge(initParams.agglayerBridge).networkID();
  99 |         $.agglayerBridge = IAgglayerBridge(initParams.agglayerBridge);
 100 |         $.minimumYieldVaultDeposit = initParams.minimumYieldVaultDeposit;
 101 |         $.migrationManager = initParams.migrationManager;
 102 |         $.yieldVaultMaximumSlippagePercentage = initParams.yieldVaultMaximumSlippagePercentage;
 103 |         $._vaultBridgeTokenPart2 = initParams.vaultBridgeTokenPart2;
 104 | 
 105 |         // Approve the yield vault and Agglayer Bridge.
 106 |         IERC20(initParams.underlyingToken).forceApprove(initParams.yieldVault, type(uint256).max);
 107 |         _approve(address(this), address(initParams.agglayerBridge), type(uint256).max);
 108 |     }
 109 | 
 110 |     /*
 111 |     /// @dev How to add a new init step:
 112 |     function init3() external onlyInitializing {}
 113 |     */
 114 | 
 115 |     /// @inheritdoc VaultBridgeToken
 116 |     function _VAULT_BRIDGE_TOKEN_INIT_2_COMPATIBLE() internal pure override {}
 117 | }
 118 | 