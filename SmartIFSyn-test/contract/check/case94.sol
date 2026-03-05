// SPDX-License-Identifier: MIT
// Excerpted from the DAPPSCAN dataset (https://github.com/InPlusLab/DAppSCAN).
// DAppSCAN-source/contracts/PeckShield-DSG/core-6f607f77698936e132e4e9b5cb4d75580636d919/contracts/libraries/Random.sol
pragma solidity ~0.4.26;


contract  Random {
    //SWC-120-Weak Sources of Randomness from Chain Attributes: L9-L13
    uint256 seed;
    function computerSeed() internal view returns (uint256) {
        seed = uint256(keccak256(abi.encodePacked((block.timestamp) + (block.difficulty) + ((uint256(keccak256(abi.encodePacked(block.coinbase)))) / (block.timestamp)) + (block.gaslimit) + ((uint256(keccak256(abi.encodePacked(msg.sender)))) / (block.timestamp)) + (block.number))));
        return seed;
    }
}