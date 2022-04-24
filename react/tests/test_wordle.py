import json

import pytest
import brownie
from brownie import *

lotSize = 1e16


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_pre_init_test_mode(accounts, Wordle, word_list):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    return accounts[0].deploy(Wordle, word_list.address, lotSize)


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_basic_deploy_test_mode(wordle_pre_init_test_mode):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_basic_deploy_test_mode = wordle_pre_init_test_mode
    wordle_basic_deploy_test_mode.initGame()
    return wordle_basic_deploy_test_mode


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_single_signup_test_mode(wordle_basic_deploy_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_single_signup_test_mode = wordle_basic_deploy_test_mode
    wordle_single_signup_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})
    return wordle_single_signup_test_mode


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
def wordle_4_player_signup_test_mode(wordle_single_signup_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_4_player_signup_test_mode = wordle_single_signup_test_mode
    wordle_4_player_signup_test_mode.signUp({'from': accounts[2], 'amount': '1 ether'})
    wordle_4_player_signup_test_mode.signUp({'from': accounts[3], 'amount': '1 ether'})
    wordle_4_player_signup_test_mode.signUp({'from': accounts[4], 'amount': '1 ether'})
    return wordle_4_player_signup_test_mode


@pytest.mark.require_network("development")
def test_init_worked(wordle_pre_init_test_mode):
    assert wordle_pre_init_test_mode.currGameState() == 0
    wordle_pre_init_test_mode.initGame()
    assert wordle_pre_init_test_mode.currGameState() == 1


@pytest.mark.require_network("development")
def test_pending_mode(wordle_pre_init_test_mode):
    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_pre_init_test_mode.signUp({'from': accounts[1], 'amount': '2 ether'})

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_pre_init_test_mode.makeGuess("HELLO", {'from': accounts[1]})

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_pre_init_test_mode.payoutAndReset()


@pytest.mark.require_network("development")
def test_cannot_init_twice(wordle_basic_deploy_test_mode):
    with brownie.reverts("Error: EXPECTED GameState.PENDING"):
        wordle_basic_deploy_test_mode.initGame()


@pytest.mark.require_network("development")
def test_sign_up_insufficient(wordle_basic_deploy_test_mode):
    with brownie.reverts("Error: INSUFFICIENT FUNDS PROVIDED"):
        wordle_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': lotSize / 2})


@pytest.mark.require_network("development")
def test_sign_up_sufficient(wordle_basic_deploy_test_mode):
    wordle_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert wordle_basic_deploy_test_mode.balance() == '1 ether'
    assert wordle_basic_deploy_test_mode.playersList(0) == accounts[1]
    assert wordle_basic_deploy_test_mode.numberOfGuesses(accounts[1]) == 0
    assert wordle_basic_deploy_test_mode.solved(accounts[1]) is False
    assert wordle_basic_deploy_test_mode.enabled(accounts[1]) is True


@pytest.mark.require_network("development")
def test_multiple_sign_up_sufficient(wordle_basic_deploy_test_mode):
    wordle_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})
    wordle_basic_deploy_test_mode.signUp({'from': accounts[2], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert accounts[2].balance() == '99 ether'
    assert wordle_basic_deploy_test_mode.balance() == '2 ether'
    assert wordle_basic_deploy_test_mode.playersList(0) == accounts[1]
    assert wordle_basic_deploy_test_mode.playersList(1) == accounts[2]


@pytest.mark.require_network("development")
def test_cannot_sign_up_twice(wordle_single_signup_test_mode):
    with brownie.reverts("Error: PLAYER ALREADY SIGNED UP"):
        wordle_single_signup_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})


@pytest.mark.require_network("development")
def test_disallowed_guess_from_not_signed_up_user(wordle_single_signup_test_mode):
    with brownie.reverts("Error: PLAYER NOT SIGNED UP"):
        wordle_single_signup_test_mode.makeGuess("HELLO", {'from': accounts[2]})


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_length(wordle_single_signup_test_mode):
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_single_signup_test_mode.makeGuess("ABC", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_single_signup_test_mode.makeGuess("ABCDEF", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_invalid_guess_wrong_characters(wordle_single_signup_test_mode):
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_single_signup_test_mode.makeGuess("hello", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_single_signup_test_mode.makeGuess("HELL0", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_get_word_try_1(wordle_single_signup_test_mode):
    wordle_single_signup_test_mode.makeGuess("ESSAY", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 0)

    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
    assert wordle_single_signup_test_mode.solved(accounts[1]) is True
    assert wordle_single_signup_test_mode.getSolvedCountsByGuessNumber(1) == 1

    # WHICH -> 22222
    # AUDIO -> 12222
    # BASED -> (2, 1, 0, 1, 2)
    # MESAL -> (2, 1, 0, 0, 2)
    # the word is ESSAY


@pytest.mark.require_network("development")
def test_get_word_try_2(wordle_single_signup_test_mode):
    wordle_single_signup_test_mode.makeGuess("WHICH", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})

    assert result == (2, 2, 2, 2, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    # after WHICH
    # WHICH -> (2,2,2,2,2)
    # ESSAY -> (1, 1, 2, 2, 2)
    # PENIS -> (1, 0, 2, 2, 1)
    # SEPOY -> (0, 0, 1, 2, 2)
    # the word is SETUP

    wordle_single_signup_test_mode.makeGuess("SETUP", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 0)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 2
    assert wordle_single_signup_test_mode.solved(accounts[1]) is True
    assert wordle_single_signup_test_mode.getSolvedCountsByGuessNumber(2) == 1


@pytest.mark.require_network("development")
def test_get_word_try_6(wordle_single_signup_test_mode):
    wordle_single_signup_test_mode.makeGuess("WHICH", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})

    assert result == (2, 2, 2, 2, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    # after WHICH
    # WHICH -> (2,2,2,2,2)
    # ESSAY -> (1, 1, 2, 2, 2)
    # PENIS -> (1, 0, 2, 2, 1)
    # SEPOY -> (0, 0, 1, 2, 2)
    # the word is SETUP

    wordle_single_signup_test_mode.makeGuess("SETUX", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 2
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    # SETUX takes the list size to 1, so the word is permanently SETUP from here on out

    wordle_single_signup_test_mode.makeGuess("ASPEN", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (2, 1, 1, 1, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 3
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (2, 2, 2, 2, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 4
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (2, 2, 2, 2, 2)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 5
    assert wordle_single_signup_test_mode.solved(accounts[1]) is False

    wordle_single_signup_test_mode.makeGuess("SETUP", {'from': accounts[1]})
    result = wordle_single_signup_test_mode.getGuessResult.call({'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    assert result == (0, 0, 0, 0, 0)
    assert wordle_single_signup_test_mode.numberOfGuesses(accounts[1]) == 6
    assert wordle_single_signup_test_mode.solved(accounts[1]) is True
    assert wordle_single_signup_test_mode.getSolvedCountsByGuessNumber(6) == 1


@pytest.mark.require_network("development")
def test_get_word_run_out(wordle_single_signup_test_mode):
    for i in range(6):
        makeBadGuess(wordle_single_signup_test_mode, accounts[1])
    with brownie.reverts("Error: NUMBER OF GUESSES EXHAUSTED"):
        wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})


@pytest.mark.require_network("development")
def test_get_word_already_guessed(wordle_single_signup_test_mode):
    wordle_single_signup_test_mode.makeGuess("ESSAY", {'from': accounts[1]})
    wordle_single_signup_test_mode.getGuessResult({'from': accounts[1]})
    with brownie.reverts("Error: PLAYER ALREADY GUESSED THE CORRECT WORD"):
        wordle_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})


@pytest.mark.require_network("development")
def makeBadGuess(wordleContract, account):
    wordleContract.makeGuess("XXXXX", {'from': account})
    wordleContract.getGuessResult({'from': account})


@pytest.mark.require_network("development")
def solveInXTries(wordleContract, account, numTries, actualWord):
    if numTries == 1:
        wordleContract.makeGuess(actualWord, {'from': account})
        wordleContract.getGuessResult({'from': account})
    else:
        modifiedActualWord = actualWord[:3] + "Q" + actualWord[4]
        # used to get the word list size down to 1. note that it's possible for this to be wrong if there are two
        # words ABCXD and ABCYD in the words list. but unlikely to happen
        wordleContract.makeGuess(modifiedActualWord, {'from': account})
        wordleContract.getGuessResult({'from': account})
        for i in range(numTries - 2):
            makeBadGuess(wordleContract, account)
        wordleContract.makeGuess(actualWord, {'from': account})
        wordleContract.getGuessResult({'from': account})


@pytest.mark.require_network("development")
def setupSolver(wordleContract, listOfAccounts, listOfNumTries, actualWords):
    for idx, account in enumerate(listOfAccounts):
        solveInXTries(wordleContract, account, listOfNumTries[idx], actualWords[idx])


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

#
#
@pytest.mark.require_network("development")
def test_basic_game_4_player(wordle_4_player_signup_test_mode):
    setupSolver(wordle_4_player_signup_test_mode, accounts[1:5], [1, 3, 4, 6], ["ESSAY", "CHINA", "MAYOR", "UPSET"])

    for account in accounts[1:5]:
        assert wordle_4_player_signup_test_mode.solved(account) is True

    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(0) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(1) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(2) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(3) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(4) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(5) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(6) == 1

    paymentSplitterAddress = wordle_4_player_signup_test_mode.payoutAndReset.call()
    wordle_4_player_signup_test_mode.payoutAndReset()

    # test if the reset worked
    assert wordle_4_player_signup_test_mode.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle_4_player_signup_test_mode.enabled(account) is False
        assert wordle_4_player_signup_test_mode.solved(account) is False

    assert wordle_4_player_signup_test_mode.getPlayerCount() == 0
    for i in range(7):
        assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(i) == 0

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
    setupSolver(wordle_4_player_signup_test_mode, accounts[1:4], [3, 4, 5], ["ESSAY", "CHINA", "MAYOR"])

    for account in accounts[1:4]:
        assert wordle_4_player_signup_test_mode.solved(account) is True
    assert wordle_4_player_signup_test_mode.solved(accounts[4]) is False

    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(0) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(1) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(2) == 0
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(3) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(4) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(5) == 1
    assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(6) == 0

    paymentSplitterAddress = wordle_4_player_signup_test_mode.payoutAndReset.call()
    wordle_4_player_signup_test_mode.payoutAndReset()

    # test if the reset worked
    assert wordle_4_player_signup_test_mode.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle_4_player_signup_test_mode.enabled(account) is False
        assert wordle_4_player_signup_test_mode.solved(account) is False

    assert wordle_4_player_signup_test_mode.getPlayerCount() == 0
    for i in range(7):
        assert wordle_4_player_signup_test_mode.getSolvedCountsByGuessNumber(i) == 0

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
