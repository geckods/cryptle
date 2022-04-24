// SPDX-License-Identifier: GPL-3.0

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/finance/PaymentSplitter.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

interface WordList {
   function getWordListLength() external view returns(uint);
   function wordList(uint i) external view returns(string memory);
}

pragma solidity >=0.8.0 <0.9.0;

/**
 * @title Wordle
 * @dev Play the game wordle
 */
contract Wordle is Ownable{

    // user level objects
    mapping(address => uint) public numberOfGuesses;
    mapping(address => bool) public solved;
    mapping(address => WordleResult[5][6]) public guessStore; //multidimentional array notation is reversed for whatever reason
    mapping(address => string[6]) public userGuesses;
    mapping(address => bool) public enabled;

    mapping(address => string[]) private currWordListForUser;
    mapping(address => UserGuessState) private guessState;

    address[] public playersList;

    string[] public wordList;

    // overall aggregation objects
    uint[7] private solvedCountByGuesses;
    uint private vrfRandomNumber;
    address[] public pastGamePaymentSplitters;

    // configuration constants
    uint[7] private payouts = [0,10000,5000,2000,1000,500,100]; //payouts as a by-thousand fraction of the 4-guess payout, so 1000 is par
    uint private ownersCut = 10; //author's cut as a by-thousand fraction

    enum WordleResult{ GREEN, YELLOW, GREY } //enum represents the outcome of a wordle guess at a single character level

    // the contract starts in PENDING. The owner must call init to move it to IN_PROGRESS, where players can sign up and play
    // when the owner calls payoutAndReset, then it goes back to PENDING
    enum GameState{PENDING, IN_PROGRESS}

    //
    enum UserGuessState{AWAITING_GUESS, PROCESSING_GUESS}

    GameState public currGameState;

    WordList wl;

    uint public lotSizeInWei;

    constructor(address wordListContractAddress, uint lotSizeInWeiParam){

        wl = WordList(wordListContractAddress);

        for(uint i=0;i<wl.getWordListLength();i++){
            wordList.push(wl.wordList(i));
        }

        lotSizeInWei = lotSizeInWeiParam;

        currGameState = GameState.PENDING;
        vrfRandomNumber = 0;

    }

    string masterWordForTesting = "AUDIO";
    string allChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    function signUp() public payable {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(msg.value >= lotSizeInWei, "Error: INSUFFICIENT FUNDS PROVIDED");
        require(!enabled[msg.sender], "Error: PLAYER ALREADY SIGNED UP");

        resetSingleUser(msg.sender);
        playersList.push(msg.sender);

        enabled[msg.sender]=true;
        currWordListForUser[msg.sender] = wordList;
    }

    function setOwnerCut(uint newCut) onlyOwner public {
        ownersCut = newCut;
    }

    function getOwnerCut() onlyOwner public view returns (uint){
        return ownersCut;
    }

    function getSolvedCountsByGuessNumber(uint guessNumber) onlyOwner public view returns (uint solvedCount){
        return solvedCountByGuesses[guessNumber];
    }

    function getPlayerCount() public view returns(uint count) {
        return playersList.length;
    }

    function getCompletedGameCount() public view returns(uint count) {
        return pastGamePaymentSplitters.length;
    }

    function getWordListForUserLength(address a) onlyOwner public view returns(uint){
        return currWordListForUser[a].length;
    }

    function getWordListForUser(address a, uint b) onlyOwner public view returns(string memory){
        return currWordListForUser[a][b];
    }


    function initGame() onlyOwner public {
        require(currGameState == GameState.PENDING, "Error: EXPECTED GameState.PENDING");
        currGameState = GameState.IN_PROGRESS;
    }

    function payoutAndReset() onlyOwner public returns (PaymentSplitter paymentSplitterAddress){
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");

        // first, payout to the owner
        payable(owner()).transfer((address(this).balance* ownersCut)/1000);

        // then, distribute the rest of the eth to players
        // create shares
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
                eligiblePlayerShares[j]=(payouts[numberOfGuesses[playersList[i]]]);
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
        delete solvedCountByGuesses;

        currGameState = GameState.PENDING;

        pastGamePaymentSplitters.push(address(paymentSplitterAddress));

        return paymentSplitterAddress;
    }

    function resetSingleUser(address userAddress) internal {
        enabled[userAddress] = false;
        numberOfGuesses[userAddress] = 0;
        solved[userAddress] = false;
        guessState[userAddress] = UserGuessState.AWAITING_GUESS;
        delete guessStore[userAddress];
        delete currWordListForUser[userAddress];
    }

    function makeGuess(string calldata guessedWordString) public{
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(numberOfGuesses[msg.sender] < 6, "Error: NUMBER OF GUESSES EXHAUSTED");
        require(!solved[msg.sender], "Error: PLAYER ALREADY GUESSED THE CORRECT WORD");
        require(isValidWord(guessedWordString), "Error: INVALID INPUT WORD");
        require(guessState[msg.sender] == UserGuessState.AWAITING_GUESS, "Error: EXPECTED UserGuessState.AWAITING_GUESS");

        // record the guess, change the player state, and begin fetching the random number
        userGuesses[msg.sender][numberOfGuesses[msg.sender]] = guessedWordString;
        guessState[msg.sender] = UserGuessState.PROCESSING_GUESS;

        if(currWordListForUser[msg.sender].length > 1){
            // initiate the process of getting a random number here,
        }
    }

    function getGuessResult() public returns (WordleResult[5] memory) {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(guessState[msg.sender] == UserGuessState.PROCESSING_GUESS, "Error: EXPECTED UserGuessState.PROCESSING_GUESS");
        guessState[msg.sender] = UserGuessState.AWAITING_GUESS;

        WordleResult[5] memory result;

        string memory guessedWordString = userGuesses[msg.sender][numberOfGuesses[msg.sender]];
        uint randomNumber = uint(keccak256(abi.encodePacked(msg.sender)));
        string memory targetWord = currWordListForUser[msg.sender][randomNumber%currWordListForUser[msg.sender].length];

        result = getWordleComparison(targetWord, guessedWordString);
        guessStore[msg.sender][numberOfGuesses[msg.sender]] = result;
        numberOfGuesses[msg.sender]++;

        if(isAllGreen(result)){
            solved[msg.sender] = true;
            solvedCountByGuesses[numberOfGuesses[msg.sender]]++;
        } else {
            string[] memory newWordsListTemp = new string[](currWordListForUser[msg.sender].length);
            uint numberOfNewWords = 0;
            // create an array, and then trim it
            for(uint i=0;i<currWordListForUser[msg.sender].length;i++){
                if(isSameWordleResult(getWordleComparison(currWordListForUser[msg.sender][i], guessedWordString),result)){
                    newWordsListTemp[numberOfNewWords] = currWordListForUser[msg.sender][i];
                    numberOfNewWords++;
                }
            }

            string[] memory newWordsList = new string[](numberOfNewWords);
            for(uint i=0;i<numberOfNewWords;i++){
                newWordsList[i]=newWordsListTemp[i];
            }

            currWordListForUser[msg.sender] = newWordsList;
        }

        return result;

    }

    function isSameWordleResult(WordleResult[5] memory a, WordleResult[5] memory b) private returns (bool){
        for(uint i=0;i<5;i++){
            if(a[i]!=b[i])return false;
        }
        return true;
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

    function getWordleComparison(string memory targetWordString, string memory guessedWordString) internal view returns (WordleResult[5] memory){

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
