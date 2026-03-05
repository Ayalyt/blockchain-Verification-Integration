/*
 * @source: etherscan.io
 * @author: -
 * @vulnerable_at_lines: 16, 18
 */

pragma solidity ^0.4.24;

contract airDrop{

    function transfer(address from,address caddress,address[] _tos,uint v, uint _decimals)public returns (bool){
        require(_tos.length > 0);
        bytes4 id=bytes4(keccak256("transferFrom(address,address,uint256)"));
        uint _value = v * 10 ** _decimals;
        // <yes> <report>
        for(uint i=0;i<_tos.length;i++){
            // <yes> <report>
            caddress.call(id,from,_tos[i],_value);
        }
        return true;
    }
}