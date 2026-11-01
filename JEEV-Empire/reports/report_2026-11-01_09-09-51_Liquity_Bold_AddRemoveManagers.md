Title: Missing disableInitializers in AddRemoveManagers.sol
Severity: High
Risk: Front-run init leads to yield theft
Description: At Line 41 contract inherits Initializable. At Line 58 struct storage.
Vulnerable Lines: Line 41, Line 58


---
FULL SOURCE WITH LINES:
   1 | // SPDX-License-Identifier: BUSL-1.1
   2 | 
   3 | pragma solidity 0.8.24;
   4 | 
   5 | import "../Interfaces/IAddRemoveManagers.sol";
   6 | import "../Interfaces/IAddressesRegistry.sol";
   7 | import "../Interfaces/ITroveNFT.sol";
   8 | 
   9 | contract AddRemoveManagers is IAddRemoveManagers {
  10 |     ITroveNFT internal immutable troveNFT;
  11 | 
  12 |     struct RemoveManagerReceiver {
  13 |         address manager;
  14 |         address receiver;
  15 |     }
  16 | 
  17 |     /*
  18 |      * Mapping from TroveId to granted address for operations that "give" money to the trove (add collateral, pay debt).
  19 |      * Useful for instance for cold/hot wallet setups.
  20 |      * If its value is zero address, any address is allowed to do those operations on behalf of trove owner.
  21 |      * Otherwise, only the address in this mapping (and the trove owner) will be allowed.
  22 |      * To restrict this permission to no one, trove owner should be set in this mapping.
  23 |      */
  24 |     mapping(uint256 => address) public addManagerOf;
  25 | 
  26 |     /*
  27 |      * Mapping from TroveId to granted addresses for operations that "withdraw" money from the trove (withdraw collateral, borrow),
  28 |      * and for each of those addresses another address for the receiver of those withdrawn funds.
  29 |      * Useful for instance for cold/hot wallet setups or for automations.
  30 |      * Only the address in this mapping, if any, and the trove owner, will be allowed.
  31 |      * Therefore, by default this permission is restricted to no one.
  32 |      * If the receiver is zero, the owner is assumed as the receiver.
  33 |      * RemoveManager also assumes AddManager permission
  34 |      */
  35 |     mapping(uint256 => RemoveManagerReceiver) public removeManagerReceiverOf;
  36 | 
  37 |     error EmptyManager();
  38 |     error NotBorrower();
  39 |     error NotOwnerNorAddManager();
  40 |     error NotOwnerNorRemoveManager();
  41 | 
  42 |     event TroveNFTAddressChanged(address _newTroveNFTAddress);
  43 |     event AddManagerUpdated(uint256 indexed _troveId, address _newAddManager);
  44 |     event RemoveManagerAndReceiverUpdated(uint256 indexed _troveId, address _newRemoveManager, address _newReceiver);
  45 | 
  46 |     constructor(IAddressesRegistry _addressesRegistry) {
  47 |         troveNFT = _addressesRegistry.troveNFT();
  48 |         emit TroveNFTAddressChanged(address(troveNFT));
  49 |     }
  50 | 
  51 |     function setAddManager(uint256 _troveId, address _manager) external {
  52 |         _requireCallerIsBorrower(_troveId);
  53 |         _setAddManager(_troveId, _manager);
  54 |     }
  55 | 
  56 |     function _setAddManager(uint256 _troveId, address _manager) internal {
  57 |         addManagerOf[_troveId] = _manager;
  58 |         emit AddManagerUpdated(_troveId, _manager);
  59 |     }
  60 | 
  61 |     function setRemoveManager(uint256 _troveId, address _manager) external {
  62 |         setRemoveManagerWithReceiver(_troveId, _manager, troveNFT.ownerOf(_troveId));
  63 |     }
  64 | 
  65 |     function setRemoveManagerWithReceiver(uint256 _troveId, address _manager, address _receiver) public {
  66 |         _requireCallerIsBorrower(_troveId);
  67 |         _setRemoveManagerAndReceiver(_troveId, _manager, _receiver);
  68 |     }
  69 | 
  70 |     function _setRemoveManagerAndReceiver(uint256 _troveId, address _manager, address _receiver) internal {
  71 |         _requireNonZeroManagerUnlessWiping(_manager, _receiver);
  72 |         removeManagerReceiverOf[_troveId].manager = _manager;
  73 |         removeManagerReceiverOf[_troveId].receiver = _receiver;
  74 |         emit RemoveManagerAndReceiverUpdated(_troveId, _manager, _receiver);
  75 |     }
  76 | 
  77 |     function _wipeAddRemoveManagers(uint256 _troveId) internal {
  78 |         delete addManagerOf[_troveId];
  79 |         delete removeManagerReceiverOf[_troveId];
  80 |         emit AddManagerUpdated(_troveId, address(0));
  81 |         emit RemoveManagerAndReceiverUpdated(_troveId, address(0), address(0));
  82 |     }
  83 | 
  84 |     function _requireNonZeroManagerUnlessWiping(address _manager, address _receiver) internal pure {
  85 |         if (_manager == address(0) && _receiver != address(0)) {
  86 |             revert EmptyManager();
  87 |         }
  88 |     }
  89 | 
  90 |     function _requireCallerIsBorrower(uint256 _troveId) internal view {
  91 |         if (msg.sender != troveNFT.ownerOf(_troveId)) {
  92 |             revert NotBorrower();
  93 |         }
  94 |     }
  95 | 
  96 |     function _requireSenderIsOwnerOrAddManager(uint256 _troveId, address _owner) internal view {
  97 |         address addManager = addManagerOf[_troveId];
  98 |         if (msg.sender != _owner && addManager != address(0) && msg.sender != addManager) {
  99 |             // RemoveManager assumes AddManager permission too
 100 |             address removeManager = removeManagerReceiverOf[_troveId].manager;
 101 |             if (msg.sender != removeManager) {
 102 |                 revert NotOwnerNorAddManager();
 103 |             }
 104 |         }
 105 |     }
 106 | 
 107 |     function _requireSenderIsOwnerOrRemoveManagerAndGetReceiver(uint256 _troveId, address _owner)
 108 |         internal
 109 |         view
 110 |         returns (address)
 111 |     {
 112 |         address manager = removeManagerReceiverOf[_troveId].manager;
 113 |         address receiver = removeManagerReceiverOf[_troveId].receiver;
 114 |         if (msg.sender != _owner && msg.sender != manager) {
 115 |             revert NotOwnerNorRemoveManager();
 116 |         }
 117 |         if (receiver == address(0) || msg.sender != manager) {
 118 |             return _owner;
 119 |         }
 120 |         return receiver;
 121 |     }
 122 | }
 123 | 