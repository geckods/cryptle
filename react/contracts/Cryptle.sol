// SPDX-License-Identifier: GPL-3.0

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/finance/PaymentSplitter.sol";

//import "@openzeppelin/contracts/access/Ownable.sol";
//import "@openzeppelin/contracts/finance/PaymentSplitter.sol";

pragma solidity >=0.8.0 <0.9.0;

/**
 * @title Wordle
 * @dev Play the game wordle
 */
contract Wordle is Ownable{

    // user level objects
    mapping(address => uint) public number_of_guesses;
    mapping(address => bool) public solved;
    mapping(address => WordleResult[5][6]) public guessStore; //multidimentional array notation is reversed for whatever reason
    mapping(address => bool) public enabled;
    mapping(address => string) internal wordAssignment;
    address[] public playersList;

    // overall aggregation objects
    uint[7] solved_count_by_guesses;

    // configuration constants
    uint[7] payouts = [0,10000,5000,2000,1000,500,100]; //payouts as a by-thousand fraction of the 4-guess payout, so 1000 is par
    uint authors_cut = 10; //author's cut as a by-thousand fraction

    enum WordleResult{ GREEN, YELLOW, GREY } //enum represents the outcome of a wordle guess at a single character level

    struct WordleGuessResult {
        bool isGuessAllowed; // false when you're out of guesses or you already got the word
        bool isValidGuess; // false when the string passed is invalid
        WordleResult[5] guessOutcome;
    }

    string masterWord = "AUDIO";
    string allChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    function signUp() public payable {
        assert(msg.value >= 1 ether);
        assert(!enabled[msg.sender]);
        wordAssignment[msg.sender] = masterWord;// todo: pick random word from a database and make it his word
        
        resetSingleUser(msg.sender);
        playersList.push(msg.sender);
        enabled[msg.sender]=true;
    }

    function getSolvedCountsByGuessNumber(uint guessNumber) onlyOwner public returns (uint solvedCount){
        return solved_count_by_guesses[guessNumber];
    }

    function getPlayerCount() public view returns(uint count) {
        return playersList.length;
    }

    function payoutAndReset() onlyOwner public returns (PaymentSplitter paymentSplitterAddress){
        
        // first, payout to the owner
        payable(owner()).transfer((address(this).balance*authors_cut)/1000);
        
        // then, distribute the rest of the eth to players
        // create shares
        uint playersCount = playersList.length;
        uint eligiblePlayersCount = 0;

        for(uint i=0;i<playersList.length;i++){
            if(enabled[playersList[i]] && solved[playersList[i]]){
                eligiblePlayersCount++;
            }
        }

        address[] memory eligiblePlayers = new address[](eligiblePlayersCount);
        uint[] memory eligiblePlayerShares = new uint[](eligiblePlayersCount);

        uint j=0;

        for(uint i=0;i<playersList.length;i++){
            if(enabled[playersList[i]] && solved[playersList[i]]){
                eligiblePlayers[j]=playersList[i];
                eligiblePlayerShares[j]=(payouts[number_of_guesses[playersList[i]]]);
                j++;
            }
        }


        if(eligiblePlayersCount>0){
            paymentSplitterAddress = new PaymentSplitter(eligiblePlayers, eligiblePlayerShares);
            payable(paymentSplitterAddress).transfer(address(this).balance);
        }

        // finally, reset all players state and remove from playersList
        for(uint i=0;i<playersList.length;i++){
            resetSingleUser(playersList[i]);
        }
        delete playersList;

        // reset global data
        delete solved_count_by_guesses;

        return paymentSplitterAddress;
    }

    function resetSingleUser(address userAddress) internal {
        enabled[userAddress] = false;
        number_of_guesses[userAddress] = 0;
        solved[userAddress] = false;
        delete guessStore[userAddress];
    }

    function makeGuess(string calldata guessedWordString) public returns (WordleGuessResult memory) {
        WordleGuessResult memory result;
        result.isValidGuess = true;
        result.isGuessAllowed = true;

        if(!enabled[msg.sender] || number_of_guesses[msg.sender] >= 6 || solved[msg.sender]){
            result.isGuessAllowed = false;
            return result;
        }

        if(!isValidWord(guessedWordString)){
            result.isValidGuess = false;
            return result;
        }

        result.guessOutcome = getWordleComparison(wordAssignment[msg.sender], guessedWordString);
        guessStore[msg.sender][number_of_guesses[msg.sender]] = result.guessOutcome;
        number_of_guesses[msg.sender]++;
        
        if(isAllGreen(result.guessOutcome)){
            solved[msg.sender] = true;
            solved_count_by_guesses[number_of_guesses[msg.sender]]++;
        }

        return result;
    }

    function isValidWord(string calldata guessedWordString) internal pure returns (bool){
        if(bytes(guessedWordString).length != 5){
            return false;
        }
        for(uint i=0;i<5;i++){
            if(getIntegerIndex(bytes(guessedWordString)[i])>25){
                return false;
            }
        }
        return true;
    }
    
    function isAllGreen(WordleResult[5] memory guess) internal pure returns (bool) {
        return (guess[0]==WordleResult.GREEN && guess[1]==WordleResult.GREEN && guess[2]==WordleResult.GREEN && guess[3]==WordleResult.GREEN && guess[4]==WordleResult.GREEN);
    }

    function getIntegerIndex(bytes1 char) pure internal returns (uint8) {
        if(uint8(bytes1("A")) > uint8(char)){
            return 255;
        }
        return uint8(char) - uint8(bytes1("A"));
    }

    function getWordleComparison(string storage targetWordString, string calldata guessedWordString) internal view returns (WordleResult[5] memory){

        int[26] memory letterCounts;
        bytes memory targetWord = bytes(targetWordString);
        bytes memory guessedWord = bytes(guessedWordString);
        for(uint i=0;i<26;i++){
            letterCounts[getIntegerIndex(bytes(allChars)[i])]=0;
        }
        
        WordleResult[5] memory result = [WordleResult.GREY,WordleResult.GREY,WordleResult.GREY,WordleResult.GREY,WordleResult.GREY];

        for(uint i=0;i<5;i++){
            letterCounts[getIntegerIndex(targetWord[i])]++;
            result[i]=WordleResult.GREY;
        }

        for(uint i=0;i<5;i++){
            if(targetWord[i]==guessedWord[i]){
                result[i]=WordleResult.GREEN;
                letterCounts[getIntegerIndex(targetWord[i])]--;
            }
        }

        for(uint i=0;i<5;i++){
            if(result[i]==WordleResult.GREEN)continue;
            if(letterCounts[getIntegerIndex(guessedWord[i])]>0){
                result[i]=WordleResult.YELLOW;
                letterCounts[getIntegerIndex(guessedWord[i])]--;
            }
        }
        return result;
    }
}
