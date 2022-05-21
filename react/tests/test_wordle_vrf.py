import json

import pytest
import brownie
import random
from brownie import *

lotSize = 1e16


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_pre_init_test_mode(accounts, WordleVRF, word_list):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    vrfCoordinatorV2Mock = accounts[0].deploy(VRFCoordinatorV2Mock, 0.1, 0.1)
    vrfCoordinatorV2Mock.createSubscription()
    vrfCoordinatorV2Mock.fundSubscription(1, 10000000000)

    wordle = accounts[0].deploy(WordleVRF, lotSize, 1, vrfCoordinatorV2Mock.address)
    wordle.appendToTargetWordLists(word_list.address, 0, 700)
    wordle.appendToAllowedGuessesWordList(word_list.address, 0, 700)
    return wordle, vrfCoordinatorV2Mock


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_basic_deploy_test_mode(wordle_pre_init_test_mode):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle, vrfCoordinatorV2Mock = wordle_pre_init_test_mode
    wordle.initGame()
    return wordle, vrfCoordinatorV2Mock


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_single_signup_test_mode(wordle_basic_deploy_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle, vrfCoordinatorV2Mock = wordle_basic_deploy_test_mode
    wordle.signUp({'from': accounts[1], 'amount': '1 ether'})
    return wordle, vrfCoordinatorV2Mock


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_4_player_signup_test_mode(wordle_single_signup_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    wordle.signUp({'from': accounts[2], 'amount': '1 ether'})
    wordle.signUp({'from': accounts[3], 'amount': '1 ether'})
    wordle.signUp({'from': accounts[4], 'amount': '1 ether'})
    return wordle, vrfCoordinatorV2Mock


@pytest.mark.require_network("development")
def test_init_worked(wordle_pre_init_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_pre_init_test_mode
    assert wordle.currGameState() == 0
    wordle.initGame()
    assert wordle.currGameState() == 1


@pytest.mark.require_network("development")
def test_pending_mode(wordle_pre_init_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_pre_init_test_mode
    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle.signUp({'from': accounts[1], 'amount': '2 ether'})

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        makeGuess(wordle, accounts[1], "HELLO")

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle.payoutAndReset()


@pytest.mark.require_network("development")
def test_cannot_init_twice(wordle_basic_deploy_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_basic_deploy_test_mode
    with brownie.reverts("Error: EXPECTED GameState.PENDING"):
        wordle.initGame()


@pytest.mark.require_network("development")
def test_sign_up_insufficient(wordle_basic_deploy_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_basic_deploy_test_mode
    with brownie.reverts("Error: INSUFFICIENT FUNDS PROVIDED"):
        wordle.signUp({'from': accounts[1], 'amount': lotSize / 2})


@pytest.mark.require_network("development")
def test_sign_up_sufficient(wordle_basic_deploy_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_basic_deploy_test_mode
    wordle.signUp({'from': accounts[1], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert wordle.balance() == '1 ether'
    assert wordle.playersList(0) == accounts[1]
    assert wordle.numberOfGuesses(accounts[1]) == 0
    assert wordle.solved(accounts[1]) is False
    assert wordle.enabled(accounts[1]) is True


@pytest.mark.require_network("development")
def test_multiple_sign_up_sufficient(wordle_basic_deploy_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_basic_deploy_test_mode
    wordle.signUp({'from': accounts[1], 'amount': '1 ether'})
    wordle.signUp({'from': accounts[2], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert accounts[2].balance() == '99 ether'
    assert wordle.balance() == '2 ether'
    assert wordle.playersList(0) == accounts[1]
    assert wordle.playersList(1) == accounts[2]


@pytest.mark.require_network("development")
def test_cannot_sign_up_twice(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: PLAYER ALREADY SIGNED UP"):
        wordle.signUp({'from': accounts[1], 'amount': '1 ether'})


@pytest.mark.require_network("development")
def test_disallowed_guess_from_not_signed_up_user(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: PLAYER NOT SIGNED UP"):
        makeGuess(wordle, accounts[2], "HELLO")


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_length(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess(brownie.convert.datatypes.HexString("ABC".encode('utf-8').hex(), "bytes5"), {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_characters(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        makeGuess(wordle, accounts[1], "hello")

    with brownie.reverts("Error: INVALID INPUT WORD"):
        makeGuess(wordle, accounts[1], "HELL0")

@pytest.mark.require_network("development")
def test_invalid_guess_word_not_in_words_list(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        makeGuess(wordle, accounts[1], "XXXXX")

    with brownie.reverts("Error: INVALID INPUT WORD"):
        makeGuess(wordle, accounts[1], "ZDNAC")

@pytest.mark.require_network("development")
def test_cannot_get_guess_result_VRF_pending(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    makeGuess(wordle, accounts[1], "THESE")
    with brownie.reverts("Error: Not received VRF Random Number"):
        wordle.getGuessResult({'from': accounts[1]})


@pytest.mark.require_network("development")
def test_get_word_try_1(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    makeGuess(wordle, accounts[1], "TYPES")
    vrfCoordinatorV2Mock.fulfillRandomWords(1, wordle.address, 287)
    result = getGuessResultCall(wordle, accounts[1])
    wordle.getGuessResult({'from': accounts[1]})
    assert result == (2, 2, 2, 2, 2)

    assert wordle.numberOfGuesses(accounts[1]) == 1
    assert wordle.solved(accounts[1]) is True
    assert wordle.solvedCountByGuesses(1) == 1


@pytest.mark.require_network("development")
def test_get_word_try_2(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    makeGuess(wordle, accounts[1], "WHICH")
    vrfCoordinatorV2Mock.fulfillRandomWords(1, wordle.address, 287)
    result = getGuessResultCall(wordle, accounts[1])
    wordle.getGuessResult({'from': accounts[1]})

    assert result == (0, 0, 0, 0, 0)
    assert wordle.numberOfGuesses(accounts[1]) == 1
    assert wordle.solved(accounts[1]) is False

    makeGuess(wordle, accounts[1], "MEETS")
    vrfCoordinatorV2Mock.fulfillRandomWords(2, wordle.address, 345)
    result = getGuessResultCall(wordle, accounts[1])
    wordle.getGuessResult({'from': accounts[1]})
    assert result == (2, 2, 2, 2, 2)
    assert wordle.numberOfGuesses(accounts[1]) == 2
    assert wordle.solved(accounts[1]) is True
    assert wordle.solvedCountByGuesses(2) == 1

def brownieHexToString(brownieHex):
    return bytes.fromhex(str(brownieHex)[2:]).decode('utf-8')

def stringToBrownieHex(x):
    return brownie.convert.datatypes.HexString(x.encode('utf-8').hex(), "bytes5")

def makeGuess(wordle, account, string):
    return wordle.makeGuess(stringToBrownieHex(string), {'from': account})

def getWordListForUser(wordle, account, index):
    return brownieHexToString(wordle.getWordListForUser(account, index, {'from':accounts[0]}))

def getGuessResultCall(wordle, account):
    return wordle.getGuessResult.call({'from':account})

def getIndex(x):
    return ord(x) - ord('A')

def getWordleMatch(guessedWord, targetWord):
    letterCounts = [0]*26
    result = ["X","X","X","X","X"]
    for c in targetWord:
        letterCounts[getIndex(c)]+=1

    for i in range(5):
        if targetWord[i] == guessedWord[i]:
            result[i]="G"
            letterCounts[getIndex(targetWord[i])]-=1

    for i in range(5):
        if result[i] == "G":
            continue
        if letterCounts[getIndex(guessedWord[i])] > 0:
            result[i] = "Y"
            letterCounts[getIndex(guessedWord[i])]-=1
    return result

def getMatchingWordleWords(guessedWord, targetWord, wordList):
    realResult = getWordleMatch(guessedWord, targetWord)
    return set([x for x in wordList if getWordleMatch(guessedWord, x)==realResult])

@pytest.mark.require_network("development")
def testWordListNarrowingLogic(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    global testGuessNumber
    testGuessNumber = 1

    random.seed(69)

    while wordle.numberOfGuesses(accounts[1]) <6 and not wordle.solved(accounts[1]):
        initialWordListSize = wordle.getWordListForUserLength(accounts[1])
        initialWordList = []
        for i in range(initialWordListSize):
            initialWordList.append(getWordListForUser(wordle, accounts[1],i))

        guessedWord = random.choice(initialWordList)
        targetWordIndex = random.randrange(initialWordListSize)
        targetWord = initialWordList[targetWordIndex]
        expectedNewWordsList = getMatchingWordleWords(guessedWord, targetWord, initialWordList)

        makeGuess(wordle, accounts[1], guessedWord)
        if initialWordListSize > 1:
            vrfCoordinatorV2Mock.fulfillRandomWords(testGuessNumber, wordle.address, targetWordIndex)
            testGuessNumber += 1
        result = getGuessResultCall(wordle, accounts[1])
        wordle.getGuessResult({'from': accounts[1]})

        newWordListSize = wordle.getWordListForUserLength(accounts[1])
        newWordList = []
        for i in range(newWordListSize):
            newWordList.append(getWordListForUser(wordle, accounts[1],i))

        print(initialWordList, guessedWord, targetWord, expectedNewWordsList, newWordList)

        # todo: even when there's only one word left, narrow the words list (for uniformity, and will be gas cheap only)
        assert len(expectedNewWordsList)==1 or set(expectedNewWordsList) == set(newWordList)


@pytest.mark.require_network("development")
def test_get_word_already_guessed(wordle_single_signup_test_mode):

    global testGuessNumber
    testGuessNumber = 1

    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    makeGuessAndGetCorrectResult(wordle, vrfCoordinatorV2Mock, accounts[1])
    with brownie.reverts("Error: PLAYER ALREADY GUESSED THE CORRECT WORD"):
        makeGuess(wordle, accounts[1], "XXXXX")


def makeGuessAndGetCorrectResult(wordleContract, vrfCoordinatorV2MockContract, account):
    global testGuessNumber

    wordListLength = wordleContract.getWordListForUserLength(account)

    wordToGuess = getWordListForUser(wordleContract, account, 0)
    makeGuess(wordleContract, account, wordToGuess)
    if wordListLength > 1:
        vrfCoordinatorV2MockContract.fulfillRandomWords(testGuessNumber, wordleContract.address, 0)
        testGuessNumber += 1
    result = getGuessResultCall(wordleContract, account)
    wordleContract.getGuessResult({'from': account})
    return result

def makeGuessAndGetWrongResult(wordleContract, vrfCoordinatorV2MockContract, account):
    global testGuessNumber

    wordListLength = wordleContract.getWordListForUserLength(account)

    wordToGuess = 0
    if wordleContract.getWordListForUserLength(account) > 1:
        wordToGuess = getWordListForUser(wordleContract, account, 0)
    else:
        if getWordListForUser(wordleContract, account, 0) != "AUDIO":
            wordToGuess = "AUDIO"
        else:
            wordToGuess = "CRANE"
    makeGuess(wordleContract, account, wordToGuess)
    if wordListLength > 1:
        vrfCoordinatorV2MockContract.fulfillRandomWords(testGuessNumber, wordleContract.address, 1)
        testGuessNumber += 1
    result = getGuessResultCall(wordleContract, account)
    wordleContract.getGuessResult({'from': account})
    return result

@pytest.mark.require_network("development")
def solveInXTries(wordleContract, vrfCoordinatorV2MockContract, account, numTries):
    for i in range(numTries-1):
        makeGuessAndGetWrongResult(wordleContract, vrfCoordinatorV2MockContract, account)
    makeGuessAndGetCorrectResult(wordleContract, vrfCoordinatorV2MockContract, account)


@pytest.mark.require_network("development")
def setupSolver(wordleContract, vrfCoordinatorV2MockContract, listOfAccounts, listOfNumTries):
    for idx, account in enumerate(listOfAccounts):
        solveInXTries(wordleContract, vrfCoordinatorV2MockContract, account, listOfNumTries[idx])


testGuessNumber = 1

@pytest.mark.require_network("development")
def test_basic_game_4_player(wordle_4_player_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_4_player_signup_test_mode
    global testGuessNumber
    testGuessNumber = 1
    setupSolver(wordle, vrfCoordinatorV2Mock, accounts[1:5], [1, 3, 4, 6])

    for account in accounts[1:5]:
        assert wordle.solved(account) is True

    assert wordle.solvedCountByGuesses(0) == 0
    assert wordle.solvedCountByGuesses(1) == 1
    assert wordle.solvedCountByGuesses(2) == 0
    assert wordle.solvedCountByGuesses(3) == 1
    assert wordle.solvedCountByGuesses(4) == 1
    assert wordle.solvedCountByGuesses(5) == 0
    assert wordle.solvedCountByGuesses(6) == 1

    paymentSplitterAddress = wordle.payoutAndReset.call()
    wordle.payoutAndReset()

    # test if the reset worked
    assert wordle.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle.enabled(account) is False
        assert wordle.solved(account) is False

    assert wordle.getPlayerCount() == 0
    for i in range(7):
        assert wordle.solvedCountByGuesses(i) == 0

    with open(
            "client/src/artifacts/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.5.0/PaymentSplitter.json",
            'r') as f:
        abi = json.load(f)['abi']

    paymentSplitter = Contract.from_abi("myPaymentSplitter", paymentSplitterAddress, abi)

    assert paymentSplitter.balance() > 0

    shares = [paymentSplitter.shares(account) for account in accounts[1:5]]
    assert shares == [10000, 2000, 1000, 100]

    for account in accounts[1:5]:
        if paymentSplitter.shares(account) > 0:
            paymentSplitter.release(account, {'from': account})

    for i in range(1, 4):
        assert accounts[i].balance() > accounts[i + 1].balance()


#
#
@pytest.mark.require_network("development")
def test_basic_game_4_player_one_guy_didnt_solve(wordle_4_player_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_4_player_signup_test_mode
    global testGuessNumber
    testGuessNumber = 1

    setupSolver(wordle, vrfCoordinatorV2Mock, accounts[1:4], [3, 4, 5])

    for account in accounts[1:4]:
        assert wordle.solved(account) is True
    assert wordle.solved(accounts[4]) is False

    assert wordle.solvedCountByGuesses(0) == 0
    assert wordle.solvedCountByGuesses(1) == 0
    assert wordle.solvedCountByGuesses(2) == 0
    assert wordle.solvedCountByGuesses(3) == 1
    assert wordle.solvedCountByGuesses(4) == 1
    assert wordle.solvedCountByGuesses(5) == 1
    assert wordle.solvedCountByGuesses(6) == 0

    paymentSplitterAddress = wordle.payoutAndReset.call()
    wordle.payoutAndReset()

    # test if the reset worked
    assert wordle.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle.enabled(account) is False
        assert wordle.solved(account) is False

    assert wordle.getPlayerCount() == 0
    for i in range(7):
        assert wordle.solvedCountByGuesses(i) == 0

    with open(
            "client/src/artifacts/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.5.0/PaymentSplitter.json",
            'r') as f:
        abi = json.load(f)['abi']

    paymentSplitter = Contract.from_abi("myPaymentSplitter", paymentSplitterAddress, abi)

    assert paymentSplitter.balance() > 0

    shares = [paymentSplitter.shares(account) for account in accounts[1:5]]
    assert shares == [2000, 1000, 500, 0]

    for account in accounts[1:5]:
        if paymentSplitter.shares(account) > 0:
            paymentSplitter.release(account, {'from': account})

    for i in range(1, 4):
        assert accounts[i].balance() > accounts[i + 1].balance()

@pytest.mark.require_network("development")
def test_repeated_games(wordle_4_player_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_4_player_signup_test_mode
    global testGuessNumber
    testGuessNumber = 1

    setupSolver(wordle, vrfCoordinatorV2Mock, accounts[1:4], [3, 4, 5])
    wordle.payoutAndReset()
    wordle.initGame()
    for account in accounts[1:4]:
        wordle.signUp({'from':account, 'value':'0.1 ether'})
    setupSolver(wordle, vrfCoordinatorV2Mock, accounts[1:4], [1, 5, 6])

    assert [2262857142857142857,1131428571428571428,565714285714285714] == ([wordle.getOutstandingBalance({'from':account}) for account in accounts[1:4]])
    for account in accounts[1:4]:
        wordle.receiveOutstandingBalance({'from':account})
    assert [(98900000000000000000 + 2262857142857142857), (98900000000000000000 + 1131428571428571428),
            (98900000000000000000 + 565714285714285714)] == (
           [account.balance() for account in accounts[1:4]])
    assert accounts[0].balance() == 100040000000000000000
