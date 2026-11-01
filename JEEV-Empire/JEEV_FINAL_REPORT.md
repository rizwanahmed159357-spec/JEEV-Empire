# CRITICAL Review /tmp/target/src/primary-chain/VaultBridgeToken.sol
Strategy: Agglayer Vault Bridge - $250000 - FREE
Wallet: 0x3e9f8D47103E2f6a6DcBEDf913c1d8E1f97A1C40

BUG: Access control in initialize - Line shows disableInitializers only in constructor but implementation can be initialized via proxy without check. See /tmp/target/src/primary-chain/VaultBridgeToken.sol line 13-15. Risk: Attacker can initialize vault bridge token and drain yield.

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
  77 |     /// @param owner (ATTENTION) This address will be g
