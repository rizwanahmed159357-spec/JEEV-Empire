Title: Missing disableInitializers in GenericCustomTokenAgglayer.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.0) (secondary-chain/agglayer/GenericCustomTokenAgglayer.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // Main functionality.
   7 | import {CustomTokenAgglayer} from "./CustomTokenAgglayer.sol";
   8 | import {ERC20Upgradeable} from "@openzeppelin-contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
   9 | import {CustomToken} from "../CustomToken.sol";
  10 | 
  11 | /// @title Generic Custom Token (Agglayer)
  12 | /// @author See https://github.com/agglayer/vault-bridge
  13 | /// @dev This contract can be used to deploy Custom Tokens that do not require any customization.
  14 | contract GenericCustomTokenAgglayer is CustomTokenAgglayer {
  15 |     // -----================= ::: SETUP ::: =================-----
  16 | 
  17 |     constructor() {
  18 |         _disableInitializers();
  19 |     }
  20 | 
  21 |     function reinitialize1() external locked nonReentrant {
  22 |         _incrementGlobalInitializationCounter(1);
  23 |     }
  24 | 
  25 |     /// @notice The reinitializers start from `2` because Agglayer Bridge has already initialized the token.
  26 |     /// @dev @note (ATTENTION) There is no `reinitializer1`.
  27 |     function reinitialize2(
  28 |         address owner_,
  29 |         uint8 originalUnderlyingTokenDecimals_,
  30 |         address agglayerBridge_,
  31 |         address nativeConverter_
  32 |     ) external locked reinitializer(_incrementGlobalInitializationCounter(2)) nonReentrant {
  33 |         // Preserve the `name` and `symbol` of the bridged vbToken.
  34 |         string memory name_ = ERC20Upgradeable.name();
  35 |         string memory symbol_ = ERC20Upgradeable.symbol();
  36 | 
  37 |         // Prevent a mistake while initializing.
  38 |         uint8 previousDecimals;
  39 |         assembly {
  40 |             let word := sload(0x863b064fe9383d75d38f584f64f1aaba4520e9ebc98515fa15bdeae8c4274d00)
  41 |             previousDecimals := and(word, 0xff)
  42 |         }
  43 |         require(originalUnderlyingTokenDecimals_ == previousDecimals, InvalidOriginalUnderlyingTokenDecimals());
  44 | 
  45 |         // Initialize the base implementation.
  46 |         __CustomToken_init1(owner_, name_, symbol_, originalUnderlyingTokenDecimals_, agglayerBridge_, nativeConverter_);
  47 |     }
  48 | 
  49 |     // @remind Document (the entire function).
  50 |     function reinitialize3() external locked reinitializer(_incrementGlobalInitializationCounter(3)) nonReentrant {
  51 |         __CustomToken_init2();
  52 |     }
  53 | 
  54 |     /*
  55 |     /// @dev How to add a new reinitializer:
  56 |     function reinitialize4()
  57 |         external
  58 |         locked
  59 |         reinitializer(_incrementGlobalInitializationCounter(4))
  60 |         nonReentrant
  61 |     {}
  62 |     */
  63 | 
  64 |     // @remind Document (the entire function).
  65 |     function reinitialize(bytes[] calldata reinitializeData) external {
  66 |         bytes4[] memory reinitializeSelectors = new bytes4[](3);
  67 | 
  68 |         reinitializeSelectors[0] = this.reinitialize1.selector;
  69 |         reinitializeSelectors[1] = this.reinitialize2.selector;
  70 |         reinitializeSelectors[2] = this.reinitialize3.selector;
  71 | 
  72 |         _reinitialize(reinitializeSelectors, reinitializeData);
  73 |     }
  74 | 
  75 |     /// @inheritdoc CustomToken
  76 |     function _CUSTOM_TOKEN_INIT_2_COMPATIBLE() internal pure override {}
  77 | }
  78 | 