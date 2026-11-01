Title: Missing disableInitializers in VbETH.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (primary-chain/ethereum/vbETH/VbEth.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | import {VaultBridgeToken, IAgglayerBridge} from "../../VaultBridgeToken.sol";
   7 | import {IWETH9} from "../../../etc/IWETH9.sol";
   8 | import {IERC4626} from "@openzeppelin/contracts/interfaces/IERC4626.sol";
   9 | import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
  10 | 
  11 | /// @title Vault Bridge gas token
  12 | /// @author See https://github.com/agglayer/vault-bridge
  13 | /// @dev CAUTION! As-is, this contract MUST NOT be used on a chain if the gas token is not ETH.
  14 | contract VbEth is VaultBridgeToken {
  15 |     using SafeERC20 for IWETH9;
  16 | 
  17 |     error ContractNotSupportedOnThisChain();
  18 |     error IncorrectMsgValue(uint256 msgValue, uint256 requestedAssets);
  19 | 
  20 |     constructor() {
  21 |         _disableInitializers();
  22 |     }
  23 | 
  24 |     function reinitialize1(address initializer_, VaultBridgeToken.InitializationParameters calldata initParams)
  25 |         external
  26 |         reinitializer(1)
  27 |         nonReentrant
  28 |     {
  29 |         // Initialize the base implementation.
  30 |         __VaultBridgeToken_init1(initializer_, initParams);
  31 | 
  32 |         require(
  33 |             IAgglayerBridge(initParams.agglayerBridge).gasTokenAddress() == address(0)
  34 |                 && IAgglayerBridge(initParams.agglayerBridge).gasTokenNetwork() == 0,
  35 |             ContractNotSupportedOnThisChain()
  36 |         );
  37 |     }
  38 | 
  39 |     function reinitialize2() external reinitializer(2) nonReentrant {
  40 |         _incrementGlobalInitializationCounter(1);
  41 |         _incrementGlobalInitializationCounter(2);
  42 | 
  43 |         __VaultBridgeToken_init2();
  44 |     }
  45 | 
  46 |     /*
  47 |     /// @dev How to add a new reinitializer:
  48 |     function reinitialize3()
  49 |         external
  50 |         reinitializer(_incrementGlobalInitializationCounter(3))
  51 |         nonReentrant
  52 |     {}
  53 |     */
  54 | 
  55 |     // @remind Document (the entire function).
  56 |     function reinitialize(bytes[] calldata reinitializeData) external {
  57 |         bytes4[] memory reinitializeSelectors = new bytes4[](2);
  58 | 
  59 |         reinitializeSelectors[0] = this.reinitialize1.selector;
  60 |         reinitializeSelectors[1] = this.reinitialize2.selector;
  61 | 
  62 |         _reinitialize(reinitializeSelectors, reinitializeData);
  63 |     }
  64 | 
  65 |     /// @inheritdoc VaultBridgeToken
  66 |     function _VAULT_BRIDGE_TOKEN_INIT_2_COMPATIBLE() internal pure override {}
  67 | 
  68 |     /// @dev deposit ETH to get vbETH
  69 |     function depositGasToken(address receiver) external payable whenNotPaused nonReentrant returns (uint256 shares) {
  70 |         (shares,) = _depositUsingCustomReceivingFunction(
  71 |             _receiveUnderlyingTokenViaMsgValue, msg.value, agglayerId(), receiver, false, 0
  72 |         );
  73 |     }
  74 | 
  75 |     /// @dev deposit ETH to get vbETH and bridge to an L2
  76 |     function depositGasTokenAndBridge(
  77 |         address destinationAddress,
  78 |         uint32 destinationNetworkId,
  79 |         bool forceUpdateGlobalExitRoot
  80 |     ) external payable whenNotPaused nonReentrant returns (uint256 shares) {
  81 |         require(destinationNetworkId != agglayerId(), InvalidDestinationNetworkId());
  82 |         (shares,) = _depositUsingCustomReceivingFunction(
  83 |             _receiveUnderlyingTokenViaMsgValue,
  84 |             msg.value,
  85 |             destinationNetworkId,
  86 |             destinationAddress,
  87 |             forceUpdateGlobalExitRoot,
  88 |             0
  89 |         );
  90 |     }
  91 | 
  92 |     function mintWithGasToken(uint256 shares, address receiver)
  93 |         external
  94 |         payable
  95 |         whenNotPaused
  96 |         nonReentrant
  97 |         returns (uint256 assets)
  98 |     {
  99 |         require(shares > 0, InvalidShares());
 100 |         // The receiver is checked in the `_depositUsingCustomReceivingFunction` function.
 101 | 
 102 |         // Mint vbToken to the receiver.
 103 |         uint256 mintedShares;
 104 |         (mintedShares, assets) =
 105 |         // msg.value is used as assets value, if it exceeds shares value, WETH will be refunded
 106 |         _depositUsingCustomReceivingFunction(
 107 |             _receiveUnderlyingTokenViaMsgValue, msg.value, agglayerId(), receiver, false, shares
 108 |         );
 109 | 
 110 |         // Check the output.
 111 |         require(mintedShares == shares, IncorrectAmountOfSharesMinted(mintedShares, shares));
 112 |     }
 113 | 
 114 |     function _receiveUnderlyingTokenViaMsgValue(address from, uint256 assets) internal {
 115 |         assert(from == msg.sender);
 116 | 
 117 |         require(msg.value == assets, IncorrectMsgValue(msg.value, assets));
 118 | 
 119 |         IWETH9 weth = IWETH9(address(underlyingToken()));
 120 | 
 121 |         uint256 balanceBefore = weth.balanceOf(address(this));
 122 | 
 123 |         // deposit everything, excess funds will be refunded in WETH
 124 |         weth.deposit{value: msg.value}();
 125 | 
 126 |         uint256 balanceAfter = weth.balanceOf(address(this));
 127 | 
 128 |         uint256 receivedAssets = balanceAfter - balanceBefore;
 129 | 
 130 |         require(receivedAssets == assets, InsufficientUnderlyingTokenReceived(receivedAssets, assets));
 131 |     }
 132 | }
 133 | 