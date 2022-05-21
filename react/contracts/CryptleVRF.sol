// SPDX-License-Identifier: GPL-3.0

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/finance/PaymentSplitter.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

interface WordList {
   function getWordListLength() external view returns(uint);
   function wordList(uint i) external view returns(bytes5);
}

pragma solidity >=0.8.0 <0.9.0;

/**
 * @title Wordle
 * @dev Play the game wordle
 */
contract WordleVRF is Ownable, VRFConsumerBaseV2{

    //VRF RELATED OBJECTS
    VRFCoordinatorV2Interface COORDINATOR;

    // Your subscription ID.
    uint64 public s_subscriptionId;
    function setSubscriptionId(uint64 newSubscriptionId) onlyOwner public {
        s_subscriptionId = newSubscriptionId;
    }

    // Rinkeby coordinator. For other networks,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    //    0x6168499c0cFfCaCD319c818142124B7A15E857ab -> Rinkeby
    //    0x602C71e4DAC47a042Ee7f46E0aee17F94A3bA0B6 -> Macbook
    //    0xD8a813cefe2200b81e1E362cb2BfD37FBE4e6f44 -> PC
    address public vrfCoordinator;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // For a list of available gas lanes on each network,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    // Mumbai : 0x4b09e658ed251bcafeebbc69400383d49f344ace09b9576fe248bb02c003fe9f
    // Rinkeby : 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc
    // BSC test: 0xd4bb89654db74673a187bd804519e65e3f71a52bc55f11da7601a13dcf505314
    // AVAX TEST: 0x354d2f95da55398f44b7cff77da56283d9c6c829a4bdf1bbcaf2ad6a4d081f61
    bytes32 public keyHash = 0x354d2f95da55398f44b7cff77da56283d9c6c829a4bdf1bbcaf2ad6a4d081f61;
    function setKeyHash(bytes32 newKeyHash) onlyOwner public {
        keyHash = newKeyHash;
    }

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 public callbackGasLimit = 1000000;
    function setCallbackGasLimit(uint32 newCallbackGasLimit) onlyOwner public {
        callbackGasLimit = newCallbackGasLimit;
    }

    // The default is 3, but you can set this higher.
    uint16 public requestConfirmations = 3;
    function setRequestConfirmations(uint16 newRequestConfirmations) onlyOwner public {
        requestConfirmations = newRequestConfirmations;
    }

    // Cannot exceed VRFCoordinatorV2.MAX_NUM_WORDS.
    uint32 public numWords =  1;

    uint256[] public s_randomWords;
    uint256 public s_requestId;
    address public s_owner;

    // user level objects
    mapping(address => uint) public numberOfGuesses;
    mapping(address => bool) public solved;
    mapping(address => WordleResult[5][6]) public guessStore; //multidimentional array notation is reversed for whatever reason
    mapping(address => bytes5[6]) public userGuesses;
    mapping(address => bool) public enabled;


    mapping(uint => address) public vrfRequestIdToAddress;
    mapping(address => uint) public vrfAddressToRandomNumber;

    enum RandomNumberRequestState{NO_REQUEST, REQUESTED, FULFILLED}
    mapping(address => RandomNumberRequestState) public randomNumberRequestStateForUser;

    mapping(address => bytes5[]) private currWordListForUser;
    function getWordListForUserLength(address a) onlyOwner public view returns(uint){
        return currWordListForUser[a].length;
    }

    function getWordListForUser(address a, uint b) onlyOwner public view returns(bytes5){
        return currWordListForUser[a][b];
    }

    mapping(address => UserGuessState) public guessState;

    address[] public playersList;
    function getPlayerCount() public view returns(uint count) {
        return playersList.length;
    }


    bytes5[] public targetWordList;
    mapping(bytes5 => bool) public allowedWords;
    uint public allowedWordsSize;

    // overall aggregation objects
    uint[7] public solvedCountByGuesses;

    address[] public pastGamePaymentSplitters;
    function getCompletedGameCount() public view returns(uint count) {
        return pastGamePaymentSplitters.length;
    }

    // configuration constants
    uint[7] private payouts = [0,10000,5000,2000,1000,500,100]; //payouts as a by-thousand fraction of the 4-guess payout, so 1000 is par

    uint private ownersCut = 10; //author's cut as a by-thousand fraction
    function setOwnerCut(uint newCut) onlyOwner public {
        ownersCut = newCut;
    }

    function getOwnerCut() onlyOwner public view returns (uint){
        return ownersCut;
    }

    enum WordleResult{ GREY, YELLOW, GREEN } //enum represents the outcome of a wordle guess at a single character level

    // the contract starts in PENDING. The owner must call init to move it to IN_PROGRESS, where players can sign up and play
    // when the owner calls payoutAndReset, then it goes back to PENDING
    enum GameState{PENDING, IN_PROGRESS}

    //
    enum UserGuessState{AWAITING_GUESS, PROCESSING_GUESS}

    GameState public currGameState;

    WordList private wl;

    uint public lotSizeInWei;


    event ContractCreated(uint lotSizeInWei, uint64 vrfSubscriptionId, address vrfCoordinator);
    constructor(uint _lotSizeInWei, uint64 _vrfSubscriptionId, address _vrfCoordinator) VRFConsumerBaseV2(_vrfCoordinator){
        vrfCoordinator = _vrfCoordinator;
        lotSizeInWei = _lotSizeInWei;
        currGameState = GameState.PENDING;

        COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
        s_owner = msg.sender;
        s_subscriptionId = _vrfSubscriptionId;

        emit ContractCreated(_lotSizeInWei, _vrfSubscriptionId, _vrfCoordinator);
    }

    event AppendToTargetWordList(uint indexed currentGameNumber, uint originalTargetWordListLength, uint updatedTargetWordListLength);
    function appendToTargetWordLists(address wordListContractAddress, uint startIndex, uint endIndex) onlyOwner public {
        wl = WordList(wordListContractAddress);
        require(startIndex >= 0 && endIndex >= 0 && startIndex<= wl.getWordListLength() && endIndex <= wl.getWordListLength(), "Error: WORDLIST INDEX OUT OF RANGE");
        uint originalTargetWordListLength = targetWordList.length;
        for(uint i=startIndex;i<endIndex;i++){
            targetWordList.push(wl.wordList(i));
        }
        emit AppendToTargetWordList(getCompletedGameCount(), originalTargetWordListLength, targetWordList.length);
    }

    event AppendToAllowedGuessWordList(uint indexed currentGameNumber, uint originalAllowedGuessesWordListLength, uint updatedAllowedGuessesWordListLength);
    function appendToAllowedGuessesWordList(address allowedGuessesWordListContractAddress, uint startIndex, uint endIndex) onlyOwner public {
        wl = WordList(allowedGuessesWordListContractAddress);
        require(startIndex >= 0 && endIndex >= 0 && startIndex<= wl.getWordListLength() && endIndex <= wl.getWordListLength(), "Error: WORDLIST INDEX OUT OF RANGE");
        uint allowedWordsAdded = 0;
        for(uint i=startIndex;i<endIndex;i++){
            if(!allowedWords[wl.wordList(i)]){
                allowedWordsAdded++;
                allowedWords[wl.wordList(i)]=true;
            }
        }
        emit AppendToAllowedGuessWordList(getCompletedGameCount(), allowedWordsSize, allowedWordsSize+allowedWordsAdded);
        allowedWordsSize+=allowedWordsAdded;
    }


    function getOutstandingBalance() public view returns(uint) {
        uint balance = 0;
        for(uint i=0;i<pastGamePaymentSplitters.length;i++){
            PaymentSplitter paymentSplitter = PaymentSplitter(payable(pastGamePaymentSplitters[i]));
            balance += ((pastGamePaymentSplitters[i].balance + paymentSplitter.totalReleased())*paymentSplitter.shares(msg.sender))/paymentSplitter.totalShares() - paymentSplitter.released(msg.sender);
        }
        return balance;
    }

    function receiveOutstandingBalance() public {
        uint balance = 0;
        for(uint i=0;i<pastGamePaymentSplitters.length;i++){
            PaymentSplitter paymentSplitter = PaymentSplitter(payable(pastGamePaymentSplitters[i]));
            paymentSplitter.release(payable(msg.sender));
        }
    }


    event InitGame(uint indexed currentGameNumber);
    function initGame() onlyOwner public {
        require(currGameState == GameState.PENDING, "Error: EXPECTED GameState.PENDING");
        require(allowedWordsSize > 0, "Error: EXPECTED allowedWordsSize > 0");
        require(targetWordList.length > 0, "Error: EXPECTED targetWordList.length > 0");
        currGameState = GameState.IN_PROGRESS;
        emit InitGame(getCompletedGameCount());
    }



    event SignUp(uint indexed currentGameNumber, address indexed player);
    function signUp() public payable {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(msg.value >= lotSizeInWei, "Error: INSUFFICIENT FUNDS PROVIDED");
        require(!enabled[msg.sender], "Error: PLAYER ALREADY SIGNED UP");

        resetSingleUser(msg.sender);
        playersList.push(msg.sender);

        enabled[msg.sender]=true;
        currWordListForUser[msg.sender] = targetWordList;
        randomNumberRequestStateForUser[msg.sender] = RandomNumberRequestState.NO_REQUEST;
        guessState[msg.sender] = UserGuessState.AWAITING_GUESS;

        emit SignUp(getCompletedGameCount(), msg.sender);
    }

    event MakeGuess(uint indexed currentGameNumber, address indexed player, bytes5 guessedWord);
    event VRFCall(uint indexed currentGameNumber, address indexed player, uint requestId);
    function makeGuess(bytes5 guessedWord) public{
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(numberOfGuesses[msg.sender] < 6, "Error: NUMBER OF GUESSES EXHAUSTED");
        require(!solved[msg.sender], "Error: PLAYER ALREADY GUESSED THE CORRECT WORD");
        require(isValidWord(guessedWord), "Error: INVALID INPUT WORD");
        require(guessState[msg.sender] == UserGuessState.AWAITING_GUESS, "Error: EXPECTED UserGuessState.AWAITING_GUESS");

        assert(randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.NO_REQUEST);

        // record the guess, change the player state, and begin fetching the random number
        userGuesses[msg.sender][numberOfGuesses[msg.sender]] = guessedWord;
        guessState[msg.sender] = UserGuessState.PROCESSING_GUESS;

        if(currWordListForUser[msg.sender].length > 1){
            // initiate the process of getting a random number here,
                    // Will revert if subscription is not set and funded.
            s_requestId = COORDINATOR.requestRandomWords(
                keyHash,
                s_subscriptionId,
                requestConfirmations,
                callbackGasLimit,
                numWords
            );
            emit VRFCall(getCompletedGameCount(), msg.sender, s_requestId);
            vrfRequestIdToAddress[s_requestId] = msg.sender;
            randomNumberRequestStateForUser[msg.sender] = RandomNumberRequestState.REQUESTED;
        }

        emit MakeGuess(getCompletedGameCount(), msg.sender, guessedWord);
    }

    event GetGuessResult(uint indexed currentGameNumber, address indexed player);
    function getGuessResult() public returns (WordleResult[5] memory) {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(guessState[msg.sender] == UserGuessState.PROCESSING_GUESS, "Error: EXPECTED UserGuessState.PROCESSING_GUESS");

        uint currWordListLength = currWordListForUser[msg.sender].length;

        require(currWordListLength == 1 || randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.FULFILLED, "Error: Not received VRF Random Number");

        guessState[msg.sender] = UserGuessState.AWAITING_GUESS;
        if(randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.FULFILLED){
            randomNumberRequestStateForUser[msg.sender] = RandomNumberRequestState.NO_REQUEST;
        }

        WordleResult[5] memory result;

        bytes5 guessedWord = userGuesses[msg.sender][numberOfGuesses[msg.sender]];

        bytes5 targetWord;
        if(currWordListLength == 1){
            targetWord = currWordListForUser[msg.sender][0];
        } else {
            targetWord = currWordListForUser[msg.sender][vrfAddressToRandomNumber[msg.sender]%currWordListLength];
        }

        result = getWordleComparison(targetWord, guessedWord);
        guessStore[msg.sender][numberOfGuesses[msg.sender]] = result;
        numberOfGuesses[msg.sender]++;

        if(isAllGreen(result)){
            solved[msg.sender] = true;
            solvedCountByGuesses[numberOfGuesses[msg.sender]]++;
        } else {
            uint i=0;
            while(i<currWordListForUser[msg.sender].length){
                if(isSameWordleResult(guessedWord, currWordListForUser[msg.sender][i], result)){
                    i++;
                } else {
                    currWordListForUser[msg.sender][i] = currWordListForUser[msg.sender][currWordListForUser[msg.sender].length-1];
                    currWordListForUser[msg.sender].pop();
                }
            }
        }

        delete vrfAddressToRandomNumber[msg.sender];

        emit GetGuessResult(getCompletedGameCount(), msg.sender);

        return result;
    }


    event FulfilledRandomWords(uint indexed currentGameNumber, address indexed player, uint randomNumber);
    function fulfillRandomWords(
        uint256 requestId, /* requestId */
        uint256[] memory randomWords
    ) internal override {
        assert(vrfRequestIdToAddress[requestId] != address(0));
        assert(randomNumberRequestStateForUser[vrfRequestIdToAddress[requestId]] == RandomNumberRequestState.REQUESTED);
        vrfAddressToRandomNumber[vrfRequestIdToAddress[requestId]] = randomWords[0];
        randomNumberRequestStateForUser[vrfRequestIdToAddress[requestId]] = RandomNumberRequestState.FULFILLED;

        emit FulfilledRandomWords(getCompletedGameCount(), vrfRequestIdToAddress[requestId], randomWords[0]);

        vrfRequestIdToAddress[requestId]=address(0);
    }

    function getCurrentPayout(uint count) public view returns (uint){
        require(count > 0 && count <=6, "Error: REQUIRE GUESS NUMBER TO BE BETWEEN 1 AND 6 INCLUSIVE");

        uint total = address(this).balance;
        total = total * (1000-ownersCut);
        total = total/1000;

        uint mySplit = payouts[count];
        uint totalSplit = 0;
        for(uint i=1;i<=6;i++){
            totalSplit += payouts[i]*solvedCountByGuesses[i];
        }
        totalSplit += mySplit;

        return (total*mySplit)/totalSplit;
    }

    event PayoutAndReset(uint indexed currentGameNumber, address paymentSplitterAddress);
    function payoutAndReset() onlyOwner public returns (PaymentSplitter paymentSplitterAddress){
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");

        // first, payout to the owner
        payable(owner()).transfer((address(this).balance* ownersCut)/1000);

        // then, distribute the rest of the eth to players
        // create shares
        uint eligiblePlayersCount = 0;

        uint playersListLength = playersList.length;

        for(uint i=0;i<playersListLength;i++){
            if(enabled[playersList[i]] && solved[playersList[i]]){
                eligiblePlayersCount++;
            }
        }

        address[] memory eligiblePlayers = new address[](eligiblePlayersCount);
        uint[] memory eligiblePlayerShares = new uint[](eligiblePlayersCount);

        uint j=0;

        for(uint i=0;i<playersListLength;i++){
            if(enabled[playersList[i]] && solved[playersList[i]]){
                eligiblePlayers[j]=playersList[i];
                eligiblePlayerShares[j]=(payouts[numberOfGuesses[playersList[i]]]);
                j++;
            }
        }


        if(eligiblePlayersCount>0){
            paymentSplitterAddress = new PaymentSplitter(eligiblePlayers, eligiblePlayerShares);
            payable(paymentSplitterAddress).transfer(address(this).balance);
            pastGamePaymentSplitters.push(address(paymentSplitterAddress));
        }

        // finally, reset all players state and remove from playersList
        for(uint i=0;i<playersListLength;i++){
            resetSingleUser(playersList[i]);
        }
        delete playersList;

        // reset global data
        delete solvedCountByGuesses;

        currGameState = GameState.PENDING;

        emit PayoutAndReset(getCompletedGameCount(), address(paymentSplitterAddress));



        return paymentSplitterAddress;
    }

    function resetSingleUser(address userAddress) internal {
        delete enabled[userAddress];
        delete numberOfGuesses[userAddress];
        delete solved[userAddress];
        delete guessState[userAddress];
        delete guessStore[userAddress];
        delete currWordListForUser[userAddress];
        delete randomNumberRequestStateForUser[userAddress];
    }

    function getWordleComparison(bytes5 targetWord, bytes5 guessedWord) internal view returns (WordleResult[5] memory){

        uint[26] memory letterCounts;

        WordleResult[5] memory result;

        for(uint i=0;i<5;i++){
            if(targetWord[i]==guessedWord[i]){
                result[i]=WordleResult.GREEN;
            }
            else{
                letterCounts[getIntegerIndex(targetWord[i])]++;
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


    function isSameWordleResult(bytes5 guessedWord, bytes5 targetWord, WordleResult[5] memory expectedResult) private view returns (bool){


        for(uint i=0;i<5;i++){
            if((expectedResult[i] == WordleResult.GREEN) != (guessedWord[i]==targetWord[i]))return false;
        }

        uint[26] memory letterCounts;

        for(uint i=0;i<5;i++){
            if(targetWord[i]!=guessedWord[i]){
                letterCounts[getIntegerIndex(targetWord[i])]++;
            }
        }

        for(uint i=0;i<5;i++){
            if(targetWord[i]==guessedWord[i])continue;
            if(letterCounts[getIntegerIndex(guessedWord[i])]>0){
                if(expectedResult[i] != WordleResult.YELLOW) return false;
                letterCounts[getIntegerIndex(guessedWord[i])]--;
            } else {
                if(expectedResult[i] != WordleResult.GREY) return false;
            }
        }
        return true;
    }

    function isValidWord(bytes5 guessedWord) internal view returns (bool){
        return allowedWords[guessedWord];
    }

    function isAllGreen(WordleResult[5] memory guess) internal pure returns (bool) {
        return (guess[0]==WordleResult.GREEN && guess[1]==WordleResult.GREEN && guess[2]==WordleResult.GREEN && guess[3]==WordleResult.GREEN && guess[4]==WordleResult.GREEN);
    }

    function getIntegerIndex(bytes1 char) pure internal returns (uint) {
        return uint(uint8(char) - 65);
    }

}
