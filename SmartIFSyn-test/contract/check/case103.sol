// SPDX-License-Identifier: MIT
pragma solidity ~0.4.26;
// // Excerpted from the DAPPSCAN dataset (https://github.com/InPlusLab/DAppSCAN).
// DAppSCAN-source/contracts/QuillAudits-Dfyn Smart Contract/dual-farm-f44a4dcbeb41f38a9c02cb877a8c95b92685f972/contracts/StakingRewardsFactory.sol
//
contract StakingRewardsFactory {
    // immutables
    uint256 public stakingRewardsGenesis;

    // the staking tokens for which the rewards contract has been deployed
    address[] public stakingTokens;

    // info about rewards for a particular staking token
    struct StakingRewardsInfo {
        address stakingRewards;
        address[] poolRewardToken;
        uint256[] poolRewardAmount;
    }

    // multiple reward tokens
    //address[] public rewardTokens;

    // rewards info by staking token
    mapping(address => StakingRewardsInfo)
        public stakingRewardsInfoByStakingToken;

    // rewards info by staking token
    mapping(address => uint256) public rewardTokenQuantities;

    // SWC-120-Weak Sources of Randomness from Chain Attributes: L36
    constructor(uint256 _stakingRewardsGenesis) public {
        require(_stakingRewardsGenesis >= block.timestamp, "StakingRewardsFactory::constructor: genesis too soon");
        stakingRewardsGenesis = _stakingRewardsGenesis;
    }

    ///// permissioned functions

    // deploy a staking reward contract for the staking token, and store the reward amount
    // the reward will be distributed to the staking reward contract no sooner than the genesis
    function deploy(address stakingToken, address[] memory rewardTokens, uint256[] memory rewardAmounts) public {
        StakingRewardsInfo storage info = stakingRewardsInfoByStakingToken[stakingToken];
        require(info.stakingRewards == address(0), "StakingRewardsFactory::deploy: already deployed");

        for (uint8 i = 0; i < rewardTokens.length; i++) {
            require(rewardAmounts[i] > 0, "StakingRewardsFactory::addRewardToken: reward amount should be greater than 0");
            info.poolRewardToken.push(rewardTokens[i]);
            info.poolRewardAmount.push(rewardAmounts[i]);

            rewardTokenQuantities[rewardTokens[i]] = rewardAmounts[i];
        }
        stakingTokens.push(stakingToken);
    }

    // Rescue leftover funds from pool
    function rescueFunds(address stakingToken, address tokenAddress) public
    {
        StakingRewardsInfo storage info = stakingRewardsInfoByStakingToken[stakingToken];
        require(info.stakingRewards != address(0), "StakingRewardsFactory::notifyRewardAmount: not deployed");
    }


    ///// permissionless functions

    // call notifyRewardAmount for all staking tokens.
    function notifyRewardAmounts() public {
        require(stakingTokens.length > 0, "StakingRewardsFactory::notifyRewardAmounts: called before any deploys");
        for (uint256 i = 0; i < stakingTokens.length; i++) {
            notifyRewardAmount(stakingTokens[i]);
        }
    }

    // notify reward amount for an individual staking token.
    // this is a fallback in case the notifyRewardAmounts costs too much gas to call for all contracts
    function notifyRewardAmount(address stakingToken) public {
        require(block.timestamp >= stakingRewardsGenesis, "StakingRewardsFactory::notifyRewardAmount: not ready");

        StakingRewardsInfo storage info = stakingRewardsInfoByStakingToken[stakingToken];
        require(info.stakingRewards != address(0), "StakingRewardsFactory::notifyRewardAmount: not deployed");
        for (uint256 i = 0; i < info.poolRewardToken.length; i++) {
            uint256 rewardAmount = info.poolRewardAmount[i];
            if (rewardAmount > 0) {
                info.poolRewardAmount[i] = 0;
            }
        }
    }

    function stakingRewardsInfo(address stakingToken) public view returns (address, address[] memory, uint256[] memory)
    {
        StakingRewardsInfo storage info = stakingRewardsInfoByStakingToken[stakingToken];
        return (info.stakingRewards, info.poolRewardToken, info.poolRewardAmount);
    }
}
