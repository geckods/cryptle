import json

import pytest
import brownie
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
    wordle.appendToTargetWordLists([word_list.address])
    wordle.appendToAllowedGuessesWordList([word_list.address])
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
        wordle.makeGuess("HELLO", {'from': accounts[1]})

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
        wordle.makeGuess("HELLO", {'from': accounts[2]})


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_length(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("ABC", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("ABCDEF", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_characters(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("hello", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("HELL0", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_invalid_guess_word_not_in_words_list(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("XXXXX", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle.makeGuess("ZDNAK", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_cannot_get_guess_result_VRF_pending(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    wordle.makeGuess("ESSAY", {'from': accounts[1]})
    with brownie.reverts("Error: Not received VRF Random Number"):
        wordle.getGuessResult({'from': accounts[1]})


@pytest.mark.require_network("development")
def test_get_word_try_1(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    wordle.makeGuess("ESSAY", {'from': accounts[1]})
    vrfCoordinatorV2Mock.fulfillRandomWords(1, wordle.address, 287)
    result = wordle.getGuessResult.call({'from': accounts[1]})
    wordle.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 0)

    assert wordle.numberOfGuesses(accounts[1]) == 1
    assert wordle.solved(accounts[1]) is True
    assert wordle.solvedCountByGuesses(1) == 1


@pytest.mark.require_network("development")
def test_get_word_try_2(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    wordle.makeGuess("WHICH", {'from': accounts[1]})
    vrfCoordinatorV2Mock.fulfillRandomWords(1, wordle.address, 287)
    result = wordle.getGuessResult.call({'from': accounts[1]})
    wordle.getGuessResult({'from': accounts[1]})

    assert result == (2, 2, 2, 2, 2)
    assert wordle.numberOfGuesses(accounts[1]) == 1
    assert wordle.solved(accounts[1]) is False

    wordle.makeGuess("SETUP", {'from': accounts[1]})
    vrfCoordinatorV2Mock.fulfillRandomWords(2, wordle.address, 503)
    result = wordle.getGuessResult.call({'from': accounts[1]})
    wordle.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 0)
    assert wordle.numberOfGuesses(accounts[1]) == 2
    assert wordle.solved(accounts[1]) is True
    assert wordle.solvedCountByGuesses(2) == 1


#
#
# @pytest.mark.require_network("development")
# def test_get_word_try_6(wordle_single_signup_test_mode):
#     wordle_single_signup_test_mode.makeGuess("WHICH", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#
#     assert result == (2, 2, 2, 2, 2)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is False
#
#     # after WHICH
#     # WHICH -> (2,2,2,2,2)
#     # ESSAY -> (1, 1, 2, 2, 2)
#     # PENIS -> (1, 0, 2, 2, 1)
#     # SEPOY -> (0, 0, 1, 2, 2)
#     # the word is SETUP
#
#     wordle_single_signup_test_mode.makeGuess("SETUX", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#     assert result == (0, 0, 0, 0, 2)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 2
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is False
#
#     # SETUX takes the list size to 1, so the word is permanently SETUP from here on out
#
#     wordle_single_signup_test_mode.makeGuess("ASPEN", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#     assert result == (2, 1, 1, 1, 2)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 3
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is False
#
#     wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#     assert result == (2, 2, 2, 2, 2)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 4
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is False
#
#     wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#     assert result == (2, 2, 2, 2, 2)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 5
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is False
#
#     wordle_single_signup_test_mode.makeGuess("SETUP", {'from': accounts[1]})
#     result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
#     wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
#     assert result == (0, 0, 0, 0, 0)
#     assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 6
#     assert wordle_single_signup_test_mode.solved(accounts[1]) is True
#     assert wordle_single_signup_test_mode.solvedCountByGuesses(6) == 1
#
#
# @pytest.mark.require_network("development")
# def test_get_word_run_out(wordle_single_signup_test_mode):
#     for i in range(6):
#         makeBadGuess(wordle_single_signup_test_mode, accounts[1])
#     with brownie.reverts("Error: NUMBER OF GUESSES EXHAUSTED"):
#         wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
#
#
@pytest.mark.require_network("development")
def test_get_word_already_guessed(wordle_single_signup_test_mode):
    wordle, vrfCoordinatorV2Mock = wordle_single_signup_test_mode
    makeGuessAndGetCorrectResult(wordle, vrfCoordinatorV2Mock, accounts[1])
    with brownie.reverts("Error: PLAYER ALREADY GUESSED THE CORRECT WORD"):
        wordle.makeGuess("XXXXX", {'from': accounts[1]})


def makeGuessAndGetCorrectResult(wordleContract, vrfCoordinatorV2MockContract, account):
    global testGuessNumber

    wordListLength = wordleContract.getWordListForUserLength(account)

    wordToGuess = wordleContract.getWordListForUser(account, 0)
    wordleContract.makeGuess(wordToGuess, {'from': account})
    if wordListLength > 1:
        vrfCoordinatorV2MockContract.fulfillRandomWords(testGuessNumber, wordleContract.address, 0)
        testGuessNumber += 1
    result = wordleContract.getGuessResult.call({'from': account})
    wordleContract.getGuessResult({'from': account})
    return result

def makeGuessAndGetWrongResult(wordleContract, vrfCoordinatorV2MockContract, account):
    global testGuessNumber

    wordListLength = wordleContract.getWordListForUserLength(account)

    wordToGuess = 0
    if wordleContract.getWordListForUserLength(account) > 1:
        wordToGuess = wordleContract.getWordListForUser(account, 0)
    else:
        if wordleContract.getWordListForUser(account, 0) != "AUDIO":
            wordToGuess = "AUDIO"
        else:
            wordToGuess = "CRANE"
    wordleContract.makeGuess(wordToGuess, {'from': account})
    if wordListLength > 1:
        vrfCoordinatorV2MockContract.fulfillRandomWords(testGuessNumber, wordleContract.address, 1)
        testGuessNumber += 1
    result = wordleContract.getGuessResult.call({'from': account})
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


# 1 -> ESSAY
# 2 -> CHINA
# AUDIO -> (1, 2, 2, 1, 2)
# BRAIN -> (2, 2, 1, 1, 1)
# AIAIA -> (2, 1, 2, 2, 0)
# IIIII -> (2, 2, 0, 2, 2)
# NNNNN -> (2, 2, 2, 0, 2)
# CHINA -> (0, 0, 0, 0, 0)
# 3 -> MAYOR
# AEIOU -> (1, 2, 2, 0, 2)
# BATON -> (2, 0, 2, 0, 2)
# CABOT -> (2, 0, 2, 0, 2)
# FAVOR -> (2, 0, 2, 0, 0)
# MAJOR -> (0, 0, 2, 0, 0)
# MAYOR -> (0, 0, 0, 0, 0)
# 4 -> UPSET
# AEIOU -> (2, 1, 2, 2, 1)
# LUMEN -> (2, 1, 2, 0, 2)
# UPPER -> (0, 0, 2, 0, 2)
# UPSET -> (0, 0, 0, 0, 0)

testGuessNumber = 1


#
#
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
