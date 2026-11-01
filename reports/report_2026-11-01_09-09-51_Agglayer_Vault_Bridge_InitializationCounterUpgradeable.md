Title: Missing disableInitializers in InitializationCounterUpgradeable.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: LicenseRef-PolygonLabs-Source-Available
   2 | // Vault Bridge (last updated v1.1.0) (etc/InitializationCounterUpgradeable.sol)
   3 | 
   4 | pragma solidity 0.8.29;
   5 | 
   6 | // @remind Document (the entire contract).
   7 | /// @author See https://github.com/agglayer/vault-bridge
   8 | abstract contract InitializationCounterUpgradeable {
   9 |     enum Extension {
  10 |         WETH
  11 |     }
  12 | 
  13 |     /// @dev Storage of Initialization Counter contract.
  14 |     /// @dev It's implemented on a custom ERC-7201 namespace to reduce the risk of storage collisions when using with upgradeable contracts.
  15 |     /// @custom:storage-location erc7201:agglayer.vault-bridge.InitializationCounterUpgradeable.storage
  16 |     struct InitializationCounterUpgradeableStorage {
  17 |         uint64 _localInitializationCounter;
  18 |         mapping(Extension => uint64) _extensionInitializationCounter;
  19 |         uint64 globalInitializationCounter;
  20 |         bool _unlocked;
  21 |     }
  22 | 
  23 |     /// @dev The storage slot at which Initialization Counter storage starts, following the EIP-7201 standard.
  24 |     /// @dev Calculated as `keccak256(abi.encode(uint256(keccak256("agglayer.vault-bridge.InitializationCounterUpgradeable.storage")) - 1)) & ~bytes32(uint256(0xff))`.
  25 |     bytes32 private constant _INITIALIZATION_COUNTER_UPGRADEABLE_STORAGE =
  26 |         hex"8d679e361eeeac0b879fa197c8b3bda76a3db4f57c9f89335c04a065390bbb00";
  27 | 
  28 |     // Errors.
  29 |     error ReinitializersLocked();
  30 |     error IncorrectInitializationOrder(
  31 |         uint64 expectedGlobalInitializationCounterValue, uint64 actualGlobalInitializationCounterValue
  32 |     );
  33 |     error AlreadyReinitialized();
  34 |     error InvalidReinitializeDataLength(uint256 expectedLength, uint256 actualLength);
  35 |     error Eip1967NotDetected();
  36 |     error UnknownReinitializeSelector(bytes4 selector);
  37 | 
  38 |     // -----================= ::: STORAGE ::: =================-----
  39 | 
  40 |     // @remind Document.
  41 |     function globalInitializationCounter() public view returns (uint64) {
  42 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
  43 |         return $.globalInitializationCounter;
  44 |     }
  45 | 
  46 |     /// @dev Returns a pointer to the ERC-7201 storage namespace.
  47 |     function _getInitializationCounterUpgradeableStorage()
  48 |         private
  49 |         pure
  50 |         returns (InitializationCounterUpgradeableStorage storage $)
  51 |     {
  52 |         assembly {
  53 |             $.slot := _INITIALIZATION_COUNTER_UPGRADEABLE_STORAGE
  54 |         }
  55 |     }
  56 | 
  57 |     // -----================= ::: INITIALIZATION COUNTER ::: =================-----
  58 | 
  59 |     // @remind Document (the entire modifier).
  60 |     modifier incrementsLocalInitializationCounter(uint64 expectedNewLocalInitializationCounterValue) {
  61 |         _incrementLocalInitializationCounter(expectedNewLocalInitializationCounterValue);
  62 |         _;
  63 |     }
  64 | 
  65 |     function _incrementLocalInitializationCounter(uint64 expectedNewLocalInitializationCounterValue) private {
  66 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
  67 | 
  68 |         uint64 actualNewLocalInitializationCounterValue = $._localInitializationCounter + 1;
  69 | 
  70 |         assert(expectedNewLocalInitializationCounterValue == actualNewLocalInitializationCounterValue);
  71 | 
  72 |         $._localInitializationCounter++;
  73 |     }
  74 | 
  75 |     // @remind Document (the entire function).
  76 |     function _incrementGlobalInitializationCounter(uint64 expectedNewGlobalInitializationCounterValue)
  77 |         internal
  78 |         returns (uint64)
  79 |     {
  80 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
  81 | 
  82 |         uint64 actualNewGlobalInitializationCounterValue = $.globalInitializationCounter + 1;
  83 | 
  84 |         require(
  85 |             expectedNewGlobalInitializationCounterValue == actualNewGlobalInitializationCounterValue,
  86 |             IncorrectInitializationOrder(
  87 |                 expectedNewGlobalInitializationCounterValue, actualNewGlobalInitializationCounterValue
  88 |             )
  89 |         );
  90 | 
  91 |         $.globalInitializationCounter++;
  92 | 
  93 |         return expectedNewGlobalInitializationCounterValue;
  94 |     }
  95 | 
  96 |     // @remind Document (the entire modifier).
  97 |     modifier locked() {
  98 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
  99 |         require($._unlocked, ReinitializersLocked());
 100 |         _;
 101 |     }
 102 | 
 103 |     modifier incrementsExtensionInitializationCounter(
 104 |         uint64 requiredLocalInitializationCounterValue,
 105 |         Extension extension,
 106 |         uint64 expectedNewExtensionInitializationCounterValue
 107 |     ) {
 108 |         _incrementExtensionInitializationCounter(
 109 |             requiredLocalInitializationCounterValue, extension, expectedNewExtensionInitializationCounterValue
 110 |         );
 111 |         _;
 112 |     }
 113 | 
 114 |     function _incrementExtensionInitializationCounter(
 115 |         uint64 requiredLocalInitializationCounterValue,
 116 |         Extension extension,
 117 |         uint64 expectedNewExtensionInitializationCounterValue
 118 |     ) private {
 119 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
 120 | 
 121 |         assert($._localInitializationCounter == requiredLocalInitializationCounterValue);
 122 | 
 123 |         uint64 actualNewExtensionInitializationCounterValue = $._extensionInitializationCounter[extension] + 1;
 124 | 
 125 |         assert(expectedNewExtensionInitializationCounterValue == actualNewExtensionInitializationCounterValue);
 126 | 
 127 |         $._extensionInitializationCounter[extension]++;
 128 |     }
 129 | 
 130 |     // @remind Document (the entire function).
 131 |     function _reinitialize(bytes4[] memory reinitializeSelectors, bytes[] calldata reinitializeData) internal {
 132 |         InitializationCounterUpgradeableStorage storage $ = _getInitializationCounterUpgradeableStorage();
 133 | 
 134 |         assert(reinitializeSelectors.length > 0);
 135 | 
 136 |         uint64 globalInitializationCounter_ = $.globalInitializationCounter;
 137 | 
 138 |         uint256 expectedReinitializeDataLength = reinitializeSelectors.length - globalInitializationCounter_;
 139 |         uint256 actualReinitializeDataLength = reinitializeData.length;
 140 | 
 141 |         require(expectedReinitializeDataLength > 0, AlreadyReinitialized());
 142 | 
 143 |         require(
 144 |             actualReinitializeDataLength == expectedReinitializeDataLength,
 145 |             InvalidReinitializeDataLength(expectedReinitializeDataLength, actualReinitializeDataLength)
 146 |         );
 147 | 
 148 |         address implementation;
 149 | 
 150 |         assembly {
 151 |             implementation := sload(0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc)
 152 |         }
 153 | 
 154 |         require(implementation != address(0), Eip1967NotDetected());
 155 | 
 156 |         for (uint256 i; i < reinitializeData.length; ++i) {
 157 |             bytes4 selector = bytes4(reinitializeData[i]);
 158 | 
 159 |             require(
 160 |                 selector == reinitializeSelectors[i + globalInitializationCounter_],
 161 |                 UnknownReinitializeSelector(selector)
 162 |             );
 163 | 
 164 |             assert(selector != bytes4(0));
 165 | 
 166 |             $._unlocked = true;
 167 | 
 168 |             (bool ok, bytes memory data) = implementation.delegatecall(reinitializeData[i]);
 169 | 
 170 |             $._unlocked = false;
 171 | 
 172 |             if (!ok) {
 173 |                 assembly {
 174 |                     revert(add(32, data), mload(data))
 175 |                 }
 176 |             }
 177 |         }
 178 |     }
 179 | }
 180 | 