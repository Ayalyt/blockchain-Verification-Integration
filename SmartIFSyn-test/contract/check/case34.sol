/*
 * @source: https://swcregistry.io/docs/SWC-136/
 * @author: -
 * @vulnerable_at_lines: 13, 15, 17, 19
 */

pragma solidity ^0.4.26;

contract Save { // (i)
  uint256 private password;
  uint256 constant num = 49409376313952921;
  uint256 constant value = 1 ether;
  function withdraw(uint256 _password) public { // @name _password @anno H
    require(uint256(sha3(_password)) % password == num);
    msg.sender.transfer(value);
  }  // confidentiality vuln
  function recovery(uint256 _password) public { // @name _password @anno H
    require(uint256(sha3(_password)) % password == num);
    selfdestruct(msg.sender);
  }
}