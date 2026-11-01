Title: Missing disableInitializers in IAgglayerBridge.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.0.0) (etc/IAgglayerBridge.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | /// @author See https://github.com/agglayer/vault-bridge
   7 | interface IAgglayerBridge {
   8 |     function networkID() external view returns (uint32);
   9 |     function gasTokenAddress() external view returns (address);
  10 |     function gasTokenNetwork() external view returns (uint32);
  11 |     function bridgeAsset(
  12 |         uint32 destinationNetwork,
  13 |         address destinationAddress,
  14 |         uint256 amount,
  15 |         address token,
  16 |         bool forceUpdateGlobalExitRoot,
  17 |         bytes calldata permitData
  18 |     ) external payable;
  19 |     function claimAsset(
  20 |         bytes32[32] calldata smtProofLocalExitRoot,
  21 |         bytes32[32] calldata smtProofRollupExitRoot,
  22 |         uint256 globalIndex,
  23 |         bytes32 mainnetExitRoot,
  24 |         bytes32 rollupExitRoot,
  25 |         uint32 originNetwork,
  26 |         address originTokenAddress,
  27 |         uint32 destinationNetwork,
  28 |         address destinationAddress,
  29 |         uint256 amount,
  30 |         bytes calldata metadata
  31 |     ) external;
  32 |     function claimMessage(
  33 |         bytes32[32] calldata smtProofLocalExitRoot,
  34 |         bytes32[32] calldata smtProofRollupExitRoot,
  35 |         uint256 globalIndex,
  36 |         bytes32 mainnetExitRoot,
  37 |         bytes32 rollupExitRoot,
  38 |         uint32 originNetwork,
  39 |         address originAddress,
  40 |         uint32 destinationNetwork,
  41 |         address destinationAddress,
  42 |         uint256 amount,
  43 |         bytes calldata metadata
  44 |     ) external;
  45 |     function bridgeMessage(
  46 |         uint32 destinationNetwork,
  47 |         address destinationAddress,
  48 |         bool forceUpdateGlobalExitRoot,
  49 |         bytes calldata metadata
  50 |     ) external payable;
  51 |     function wrappedAddressIsNotMintable(address wrappedAddress) external view returns (bool isNotMintable);
  52 |     function localBalanceTree(bytes32 tokenInfoHash) external view returns (uint256);
  53 | }
  54 | 