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
contract WordleVRF is Ownable, VRFConsumerBaseV2{

    //VRF RELATED OBJECTS
    VRFCoordinatorV2Interface COORDINATOR;

    // Your subscription ID.
    uint64 public s_subscriptionId;

    // Rinkeby coordinator. For other networks,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    //    0x6168499c0cFfCaCD319c818142124B7A15E857ab -> Rinkeby
    //    0x602C71e4DAC47a042Ee7f46E0aee17F94A3bA0B6 -> Macbook
    //    0xD8a813cefe2200b81e1E362cb2BfD37FBE4e6f44 -> PC
    address public vrfCoordinator;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // For a list of available gas lanes on each network,
    // see https://docs.chain.link/docs/vrf-contracts/#configurations
    bytes32 public keyHash = 0xd89b2bf150e3b9e13446986e571fb9cab24b13cea0a43ea20a6049a85cc807cc;

    // Depends on the number of requested values that you want sent to the
    // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
    // so 100,000 is a safe default for this example contract. Test and adjust
    // this limit based on the network that you select, the size of the request,
    // and the processing of the callback request in the fulfillRandomWords()
    // function.
    uint32 public callbackGasLimit = 1000000;

    // The default is 3, but you can set this higher.
    uint16 public requestConfirmations = 3;

    // For this example, retrieve 2 random values in one request.
    // Cannot exceed VRFCoordinatorV2.MAX_NUM_WORDS.
    uint32 public numWords =  1;

    uint256[] public s_randomWords;
    uint256 public s_requestId;
    address public s_owner;

    // user level objects
    mapping(address => uint) public numberOfGuesses;
    mapping(address => bool) public solved;
    mapping(address => WordleResult[5][6]) public guessStore; //multidimentional array notation is reversed for whatever reason
    mapping(address => string[6]) public userGuesses;
    mapping(address => bool) public enabled;


    mapping(uint => address) public vrfRequestIdToAddress;
    mapping(address => uint) public vrfAddressToRandomNumber;

    enum RandomNumberRequestState{NO_REQUEST, REQUESTED, FULFILLED}
    mapping(address => RandomNumberRequestState) public randomNumberRequestStateForUser;

    mapping(address => string[]) private currWordListForUser;
    function getWordListForUserLength(address a) onlyOwner public view returns(uint){
        return currWordListForUser[a].length;
    }

    function getWordListForUser(address a, uint b) onlyOwner public view returns(string memory){
        return currWordListForUser[a][b];
    }

    mapping(address => UserGuessState) public guessState;

    address[] public playersList;
    function getPlayerCount() public view returns(uint count) {
        return playersList.length;
    }


    string[] private targetWordList;
    mapping(string => bool) private allowedWords;

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

    enum WordleResult{ GREEN, YELLOW, GREY } //enum represents the outcome of a wordle guess at a single character level

    // the contract starts in PENDING. The owner must call init to move it to IN_PROGRESS, where players can sign up and play
    // when the owner calls payoutAndReset, then it goes back to PENDING
    enum GameState{PENDING, IN_PROGRESS}

    //
    enum UserGuessState{AWAITING_GUESS, PROCESSING_GUESS}

    GameState public currGameState;

    WordList private wl;

    uint public lotSizeInWei;

    string allChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

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
    function appendToTargetWordLists(address[] memory wordListContractAddresses) onlyOwner public {
        uint originalTargetWordListLength = targetWordList.length;
        for(uint addressNumber = 0; addressNumber<wordListContractAddresses.length;addressNumber++){
            wl = WordList(wordListContractAddresses[addressNumber]);

            for(uint i=0;i<wl.getWordListLength();i++){
                targetWordList.push(wl.wordList(i));
            }
        }
        emit AppendToTargetWordList(getCompletedGameCount(), originalTargetWordListLength, targetWordList.length);
    }

    event AppendToAllowedGuessWordList(uint indexed currentGameNumber); //todo: track the size of the AllowedGuessWordList
    function appendToAllowedGuessesWordList(address[] memory allowedGuessesWordListContractAddresses) onlyOwner public {
        for(uint addressNumber = 0; addressNumber<allowedGuessesWordListContractAddresses.length;addressNumber++){
            wl = WordList(allowedGuessesWordListContractAddresses[addressNumber]);
            for(uint i=0;i<wl.getWordListLength();i++){
                allowedWords[wl.wordList(i)]=true;
            }
        }
        emit AppendToAllowedGuessWordList(getCompletedGameCount());
    }

    event InitGame(uint indexed currentGameNumber);
    function initGame() onlyOwner public {
        require(currGameState == GameState.PENDING, "Error: EXPECTED GameState.PENDING");
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

    event MakeGuess(uint indexed currentGameNumber, address indexed player, string guessedWord);
    event VRFCall(uint indexed currentGameNumber, address indexed player, uint requestId);
    function makeGuess(string calldata guessedWordString) public{
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(numberOfGuesses[msg.sender] < 6, "Error: NUMBER OF GUESSES EXHAUSTED");
        require(!solved[msg.sender], "Error: PLAYER ALREADY GUESSED THE CORRECT WORD");
        require(isValidWord(guessedWordString), "Error: INVALID INPUT WORD");
        require(guessState[msg.sender] == UserGuessState.AWAITING_GUESS, "Error: EXPECTED UserGuessState.AWAITING_GUESS");

        assert(randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.NO_REQUEST);

        // record the guess, change the player state, and begin fetching the random number
        userGuesses[msg.sender][numberOfGuesses[msg.sender]] = guessedWordString;
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

        emit MakeGuess(getCompletedGameCount(), msg.sender, guessedWordString);
    }

    event GetGuessResult(uint indexed currentGameNumber, address indexed player);
    function getGuessResult() public returns (WordleResult[5] memory) {
        require(currGameState == GameState.IN_PROGRESS, "Error: EXPECTED GameState.IN_PROGRESS");
        require(enabled[msg.sender], "Error: PLAYER NOT SIGNED UP");
        require(guessState[msg.sender] == UserGuessState.PROCESSING_GUESS, "Error: EXPECTED UserGuessState.PROCESSING_GUESS");

        require(currWordListForUser[msg.sender].length == 1 || randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.FULFILLED, "Error: Not received VRF Random Number");

        guessState[msg.sender] = UserGuessState.AWAITING_GUESS;
        if(randomNumberRequestStateForUser[msg.sender] == RandomNumberRequestState.FULFILLED){
            randomNumberRequestStateForUser[msg.sender] = RandomNumberRequestState.NO_REQUEST;
        }

        WordleResult[5] memory result;

        string memory guessedWordString = userGuesses[msg.sender][numberOfGuesses[msg.sender]];

        string memory targetWord;
        if(currWordListForUser[msg.sender].length == 1){
            targetWord = currWordListForUser[msg.sender][0];
        } else {
            targetWord = currWordListForUser[msg.sender][vrfAddressToRandomNumber[msg.sender]%currWordListForUser[msg.sender].length];
        }

        result = getWordleComparison(targetWord, guessedWordString);
        guessStore[msg.sender][numberOfGuesses[msg.sender]] = result;
        numberOfGuesses[msg.sender]++;

        if(isAllGreen(result)){
            solved[msg.sender] = true;
            solvedCountByGuesses[numberOfGuesses[msg.sender]]++;
        } else {
            string[] memory newWordListTemp = new string[](currWordListForUser[msg.sender].length);
            uint numberOfNewWords = 0;
            // create an array, and then trim it
            for(uint i=0;i<currWordListForUser[msg.sender].length;i++){
                if(isSameWordleResult(getWordleComparison(currWordListForUser[msg.sender][i], guessedWordString),result)){
                    newWordListTemp[numberOfNewWords] = currWordListForUser[msg.sender][i];
                    numberOfNewWords++;
                }
            }

            string[] memory newWordList = new string[](numberOfNewWords);
            for(uint i=0;i<numberOfNewWords;i++){
                newWordList[i]=newWordListTemp[i];
            }

            currWordListForUser[msg.sender] = newWordList;
        }

        vrfAddressToRandomNumber[msg.sender]=0;

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

        emit PayoutAndReset(getCompletedGameCount(), address(paymentSplitterAddress));

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


    function isSameWordleResult(WordleResult[5] memory a, WordleResult[5] memory b) private pure returns (bool){
        for(uint i=0;i<5;i++){
            if(a[i]!=b[i])return false;
        }
        return true;
    }

    function isValidWord(string calldata guessedWordString) internal view returns (bool){
        if(bytes(guessedWordString).length != 5){
            return false;
        }
        for(uint i=0;i<5;i++){
            if(getIntegerIndex(bytes(guessedWordString)[i])>25){
                return false;
            }
        }
        return allowedWords[guessedWordString];
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
