Title: Missing disableInitializers in CustomTokenWethExtension.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.0) (secondary-chain/CustomTokenWethExtension.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // @remind Document the entire file.
   7 | 
   8 | // Main functionality.
   9 | import {CustomToken} from "./CustomToken.sol";
  10 | 
  11 | // External contracts.
  12 | import {IAgglayerBridge} from "../etc/IAgglayerBridge.sol";
  13 | import {NativeConverter} from "./NativeConverter.sol";
  14 | 
  15 | /// @title Custom Token WETH Extension
  16 | /// @author See https://github.com/agglayer/vault-bridge
  17 | abstract contract CustomTokenWethExtension is CustomToken {
  18 |     /// @dev Storage of Custom Token WETH Extension.
  19 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  20 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.CustomTokenWethExtension.storage
  21 |     struct CustomTokenWethExtensionStorage {
  22 |         bool _gasTokenIsEth;
  23 |         uint256 gasBackingOnSecondaryChain;
  24 |         bool wethFunctionalityEnabled;
  25 |     }
  26 | 
  27 |     /// @dev The storage slot at which Custom Token WETH Extension storage starts, following the EIP-7201 standard.
  28 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.CustomTokenWethExtension.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  29 |     bytes32 private constant _CUSTOM_TOKEN_WETH_EXTENSION_STORAGE =
  30 |         hex"79530e5f68ac2fe03ca888330cb59cd18fe7ab48bdc97271c9f69b4c84c28700";
  31 | 
  32 |     error FunctionNotSupportedOnThisChain();
  33 |     error FunctionNotEnabledOnThisChain();
  34 |     error AssetsTooLarge(uint256 availableAssets, uint256 requestedAssets);
  35 |     error WithdrawalFailed();
  36 |     error WethFunctionalityCannotBeEnabledIfGasTokenIsNotEth();
  37 | 
  38 |     event Deposit(address indexed from, uint256 value);
  39 |     event Withdrawal(address indexed to, uint256 value);
  40 |     event WethFunctionalityEnabledSet(bool enabled);
  41 | 
  42 |     modifier onlyNativeConverter() {
  43 |         require(msg.sender == nativeConverter(), Unauthorized());
  44 |         _;
  45 |     }
  46 | 
  47 |     modifier onlyIfGasTokenIsEth() {
  48 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
  49 |         require($._gasTokenIsEth, FunctionNotSupportedOnThisChain());
  50 |         _;
  51 |     }
  52 | 
  53 |     modifier onlyIfWethFunctionalityEnabled() {
  54 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
  55 |         require($.wethFunctionalityEnabled, FunctionNotEnabledOnThisChain());
  56 |         _;
  57 |     }
  58 | 
  59 |     function __CustomTokenWethExtension_init2_ext1(bool gasTokenIsEth_, bool wethFunctionalityEnabled_)
  60 |         internal
  61 |         onlyInitializing
  62 |         incrementsExtensionInitializationCounter(2, Extension.WETH, 1)
  63 |     {
  64 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
  65 | 
  66 |         $._gasTokenIsEth = gasTokenIsEth_;
  67 |         $.wethFunctionalityEnabled = wethFunctionalityEnabled_;
  68 |     }
  69 | 
  70 |     /*
  71 |     /// @dev How to add a new ext step:
  72 |     function __CustomTokenWethExtension_initX_ext2()
  73 |         internal
  74 |         onlyInitializing
  75 |         incrementsExtensionInitializationCounter(X, Extension.WETH, 2)
  76 |     {}
  77 |     */
  78 | 
  79 |     function _CUSTOM_TOKEN_WETH_EXTENSION_INIT_2_EXT_1_COMPATIBLE() internal pure virtual;
  80 | 
  81 |     function gasBackingOnSecondaryChain() public view returns (uint256) {
  82 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
  83 |         return $.gasBackingOnSecondaryChain;
  84 |     }
  85 | 
  86 |     function wethFunctionalityEnabled() public view returns (bool) {
  87 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
  88 |         return $.wethFunctionalityEnabled;
  89 |     }
  90 | 
  91 |     receive() external payable whenNotPaused onlyIfGasTokenIsEth onlyIfWethFunctionalityEnabled nonReentrant {
  92 |         _deposit();
  93 |     }
  94 | 
  95 |     /// @notice Same as WETH9 deposit function.
  96 |     function deposit() external payable whenNotPaused onlyIfGasTokenIsEth onlyIfWethFunctionalityEnabled nonReentrant {
  97 |         _deposit();
  98 |     }
  99 | 
 100 |     function _deposit() internal {
 101 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
 102 |         $.gasBackingOnSecondaryChain += msg.value;
 103 |         _mint(msg.sender, msg.value);
 104 |         emit Deposit(msg.sender, msg.value);
 105 |     }
 106 | 
 107 |     /// @notice Same as WETH9 withdraw function, but liqudity is guaranteed only up to a certain percentage.
 108 |     function withdraw(uint256 value) external whenNotPaused onlyIfGasTokenIsEth nonReentrant {
 109 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
 110 |         require(value <= $.gasBackingOnSecondaryChain, AssetsTooLarge($.gasBackingOnSecondaryChain, value));
 111 |         $.gasBackingOnSecondaryChain -= value;
 112 |         _burn(msg.sender, value);
 113 |         (bool ok,) = msg.sender.call{value: value}("");
 114 |         require(ok, WithdrawalFailed());
 115 |         emit Withdrawal(msg.sender, value);
 116 |     }
 117 | 
 118 |     function moveGasBackingToNativeConverter(uint256 amount)
 119 |         external
 120 |         onlyIfGasTokenIsEth
 121 |         onlyNativeConverter
 122 |         nonReentrant
 123 |     {
 124 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
 125 |         require(amount <= $.gasBackingOnSecondaryChain, AssetsTooLarge($.gasBackingOnSecondaryChain, amount));
 126 |         $.gasBackingOnSecondaryChain -= amount;
 127 |         (bool ok,) = nativeConverter().call{value: amount}("");
 128 |         require(ok);
 129 |     }
 130 | 
 131 |     function setWethFunctionalityEnabled(bool wethFunctionalityEnabled_) external virtual onlyRole(DEFAULT_ADMIN_ROLE) {
 132 |         CustomTokenWethExtensionStorage storage $ = _getCustomTokenWethExtensionStorage();
 133 |         if (wethFunctionalityEnabled_) require($._gasTokenIsEth, WethFunctionalityCannotBeEnabledIfGasTokenIsNotEth());
 134 |         $.wethFunctionalityEnabled = wethFunctionalityEnabled_;
 135 |         emit WethFunctionalityEnabledSet(wethFunctionalityEnabled_);
 136 |     }
 137 | 
 138 |     function _getCustomTokenWethExtensionStorage() private pure returns (CustomTokenWethExtensionStorage storage $) {
 139 |         assembly {
 140 |             $.slot := _CUSTOM_TOKEN_WETH_EXTENSION_STORAGE
 141 |         }
 142 |     }
 143 | }
 144 | 