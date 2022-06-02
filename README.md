# Cryptle: Wordle For The Web3 World
 
[![Cryptle: Wordle For The Web3 World](http://img.youtube.com/vi/8gPGcuEk0ro/0.jpg)](http://www.youtube.com/watch?v=8gPGcuEk0ro "Cryptle: Wordle For The Web3 World")

## What is Cryptle?
Cryptle is Wordle for the Web3 World. 
Players compete to guess their (randomly selected) words (that are different for each player). Players that guess their word in fewer guesses receive payouts for their performance. In essence, users can bet on their own Wordle game outcomes.

Cryptle is our submission for the Chainlink Spring Hackthon 2022. Check it out [here!](https://devpost.com/software/cryptle).

## Navigating this repository
### Note that only some relevant files and folders are mentioned in this directory tree.
```
├── react
│   ├── README.md                       | Default Readme file for brownie react mix
│   ├── brownie-config.yaml             | Stores the brownie configuration
│   ├── client
│   │   ├── src                         | All the front-end react code
│   ├── contracts
│   │   ├── CryptleVRF.sol              | The main smart contract that powers the game 
│   │   ├── VRFCoordinatorV2Mock.sol    | A mock of the VRF Coordinator that we used for testing
│   │   ├── WordList.sol                | The main wordList smart contract (and other versions of it below)
│   │   ├── WordList_0_1500.sol
│   │   ├── WordList_1500_3000.sol
│   │   └── WordList_3000_4500.sol
│   ├── scripts                         
│   │   ├── deploy.py                   | Script for automated deployment of the project to a new network
│   │   ├── payoutResetInit.py          | Script for resetting the game (called via cron every 24 hours)
│   │   └── util.py                     | Some utility functions
│   └── tests
│       └── test_wordle_vrf.py          | The main unit tests we wrote to test the smart contract
└── wordslist
    └── wordListGen.py                  | The python code we used to generate the words list
```
## Inspiration
Cryptle was inspired by the desire to build a simple, easy-to-use, Web3 game that did away with complex and inaccessible tokenomics/strategies/learning curves in favour of enjoyable and accessible gameplay that benefits from the settlements layer of Web3. 

## How we built it
We built Cryptle using Solidity, powered for the python-based Brownie framework for automation and testing. We used React to build the frontend and the web3.js library to interact with the smart contract.

## Challenges we ran into
We faced a few interesting design challenges around random numbers, and hiding sensitive information on the blockchain. See the video for more details!

## Try it out!
Navigate to http://cryptle.xyz or https://geckods.github.io/cryptle/ to try it out. Note that at the moment, we are only live on the Avalanche Fuji test chain. Coming to other blockchains soon!

## What's next for Cryptle
We have plans for a mainnet launch, more features, more optimizations, and more play-to-earn massively multiplayer online Web3 games!
