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
contract Wordle is Ownable, VRFConsumerBaseV2{


    //VRF RELATED OBJECTS

    VRFCoordinatorV2Interface COORDINATOR;

    // Your subscription ID.
    uint64 s_subscriptionId;

    // Rinkeby coordinator. For other networks,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    address vrfCoordinator = 0x6168499c0cFfCaCD319c818142124B7A15E857ab;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // For a list of available gas lanes on each network,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    bytes32 keyHash = 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc;

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 callbackGasLimit = 100000;

    // The default is 3, but you can set this higher.
    uint16 requestConfirmations = 3;

    // For this example, retrieve 2 random values in one request.
    // Cannot exceed VRFCoordinatorV2.MAX_NUM_WORDS.
    uint32 numWords =  1;

    uint256[] public s_randomWords;
    uint256 public s_requestId;
    address s_owner;


    // user level objects
    mapping(address => uint) public numberOfGuesses;
    mapping(address => bool) public solved;
    mapping(address => WordleResult[5][6]) public guessStore; //multidimentional array notation is reversed for whatever reason
    mapping(address => bool) public enabled;
    mapping(address => string) private wordAssignment;
    address[] public playersList;

    string[] public wordList;

    // overall aggregation objects
    uint[7] private solvedCountByGuesses;
    uint private vrfRandomNumber;
    address[] public pastGamePaymentSplitters;

    // configuration constants
    uint[7] payouts = [0,10000,5000,2000,1000,500,100]; //payouts as a by-thousand fraction of the 4-guess payout, so 1000 is par
    uint authorsCut = 10; //author's cut as a by-thousand fraction

    enum WordleResult{ GREEN, YELLOW, GREY } //enum represents the outcome of a wordle guess at a single character level

    // the contract starts in PENDING. The owner must call init to move it to IN_PROGRESS, where players can sign up and play
    // when the owner calls payoutAndReset, then it goes back to PENDING
    enum GameState{PENDING, IN_PROGRESS}

    GameState public currGameState;
    bool public testingMode;

    WordList wl;

    uint public lotSizeInWei;

    constructor(address wordListContractAddress, uint lotSizeInWeiParam, bool isTesting, uint64 vrfSubscriptionId) VRFConsumerBaseV2(vrfCoordinator){

        wl = WordList(wordListContractAddress);

        for(uint i=0;i<wl.getWordListLength();i++){
            wordList.push(wl.wordList(i));
        }

        lotSizeInWei = lotSizeInWeiParam;

        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        s_owner = msg.sender;
        s_subscriptionId = vrfSubscriptionId;

        currGameState = GameState.PENDING;
        vrfRandomNumber = 0;

        testingMode = isTesting;
    }

    // Assumes the subscription is funded sufficiently.
    function requestRandomWords() external onlyOwner {
        // Will revert if subscription is not set and funded.
        s_requestId = COORDINATOR.requestRandomWords(
            keyHash,
            s_subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
    }

    function fulfillRandomWords(
        uint256, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        s_randomWords = randomWords;
    }

    string masterWordForTesting = "AUDIO";
    string allChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    function signUp() public payable {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(msg.value >= lotSizeInWei, "Error: INSUFFICIENT FUNDS PROVIDED");
        require(!enabled[msg.sender], "Error: PLAYER ALREADY SIGNED UP");

        if(testingMode){
            wordAssignment[msg.sender] = masterWordForTesting;
        } else {
            uint randomNumberForUser = uint(keccak256(abi.encode(vrfRandomNumber, playersList.length)));
            wordAssignment[msg.sender] = wordList[randomNumberForUser%wl.getWordListLength()];
        }

        resetSingleUser(msg.sender);
        playersList.push(msg.sender);
        enabled[msg.sender]=true;
    }

    function getAssignedWord(address user) onlyOwner public view returns (string memory){
        // FOR DEBUGGING PURPOSES, remove in actual deployment
        return wordAssignment[user];
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

    function initGame() onlyOwner public {
        require(currGameState == GameState.PENDING, "Error: EXPECTED GameState.PENDING");

        if(!testingMode){
            vrfRandomNumber = uint(keccak256(abi.encodePacked(block.difficulty, block.timestamp)));
        }

        currGameState = GameState.IN_PROGRESS;
    }

    function payoutAndReset() onlyOwner public returns (PaymentSplitter paymentSplitterAddress){
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");

        // first, payout to the owner
        payable(owner()).transfer((address(this).balance* authorsCut)/1000);
        
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
        delete guessStore[userAddress];
    }

    function makeGuess(string calldata guessedWordString) public returns (WordleResult[5] memory) {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(numberOfGuesses[msg.sender] < 6, "Error: NUMBER OF GUESSES EXHAUSTED");
        require(!solved[msg.sender], "Error: PLAYER ALREADY GUESSED THE CORRECT WORD");
        require(isValidWord(guessedWordString), "Error: INVALID INPUT WORD");

        WordleResult[5] memory result;

        result = getWordleComparison(wordAssignment[msg.sender], guessedWordString);
        guessStore[msg.sender][numberOfGuesses[msg.sender]] = result;
        numberOfGuesses[msg.sender]++;
        
        if(isAllGreen(result)){
            solved[msg.sender] = true;
            solvedCountByGuesses[numberOfGuesses[msg.sender]]++;
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
