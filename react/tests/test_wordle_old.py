import json

import pytest
import brownie
from brownie import *

lotSize = 1e16

skipTestsOfDeprecatedContract = True


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def wordle_old_pre_init_test_mode(accounts, WordleOld, word_list):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    return accounts[0].deploy(WordleOld, word_list.address, lotSize, True)


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def wordle_old_basic_deploy_test_mode(wordle_old_pre_init_test_mode):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_old_basic_deploy_test_mode = wordle_old_pre_init_test_mode
    wordle_old_basic_deploy_test_mode.initGame()
    return wordle_old_basic_deploy_test_mode


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def wordle_old_single_signup_test_mode(wordle_old_basic_deploy_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_old_single_signup_test_mode = wordle_old_basic_deploy_test_mode
    wordle_old_single_signup_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})
    return wordle_old_single_signup_test_mode


@pytest.fixture(scope="module")
@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def wordle_old_4_player_signup_test_mode(wordle_old_single_signup_test_mode, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_old_4_player_signup_test_mode = wordle_old_single_signup_test_mode
    wordle_old_4_player_signup_test_mode.signUp({'from': accounts[2], 'amount': '1 ether'})
    wordle_old_4_player_signup_test_mode.signUp({'from': accounts[3], 'amount': '1 ether'})
    wordle_old_4_player_signup_test_mode.signUp({'from': accounts[4], 'amount': '1 ether'})
    return wordle_old_4_player_signup_test_mode


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_init_worked(wordle_old_pre_init_test_mode):
    assert wordle_old_pre_init_test_mode.currGameState() == 0
    wordle_old_pre_init_test_mode.initGame()
    assert wordle_old_pre_init_test_mode.currGameState() == 1


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_pending_mode(wordle_old_pre_init_test_mode):
    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_old_pre_init_test_mode.signUp({'from': accounts[1], 'amount': '2 ether'})

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_old_pre_init_test_mode.makeGuess("HELLO", {'from': accounts[1]})

    with brownie.reverts("Error: EXPECTED GameState.IN_PROGRESS"):
        wordle_old_pre_init_test_mode.payoutAndReset()


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_cannot_init_twice(wordle_old_basic_deploy_test_mode):
    with brownie.reverts("Error: EXPECTED GameState.PENDING"):
        wordle_old_basic_deploy_test_mode.initGame()


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_sign_up_insufficient(wordle_old_basic_deploy_test_mode):
    with brownie.reverts("Error: INSUFFICIENT FUNDS PROVIDED"):
        wordle_old_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': lotSize / 2})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_sign_up_sufficient(wordle_old_basic_deploy_test_mode):
    wordle_old_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert wordle_old_basic_deploy_test_mode.balance() == '1 ether'
    assert wordle_old_basic_deploy_test_mode.playersList(0) == accounts[1]
    assert wordle_old_basic_deploy_test_mode.numberOfGuesses(accounts[1]) == 0
    assert wordle_old_basic_deploy_test_mode.solved(accounts[1]) is False
    assert wordle_old_basic_deploy_test_mode.enabled(accounts[1]) is True


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_multiple_sign_up_sufficient(wordle_old_basic_deploy_test_mode):
    wordle_old_basic_deploy_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})
    wordle_old_basic_deploy_test_mode.signUp({'from': accounts[2], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert accounts[2].balance() == '99 ether'
    assert wordle_old_basic_deploy_test_mode.balance() == '2 ether'
    assert wordle_old_basic_deploy_test_mode.playersList(0) == accounts[1]
    assert wordle_old_basic_deploy_test_mode.playersList(1) == accounts[2]


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_cannot_sign_up_twice(wordle_old_single_signup_test_mode):
    with brownie.reverts("Error: PLAYER ALREADY SIGNED UP"):
        wordle_old_single_signup_test_mode.signUp({'from': accounts[1], 'amount': '1 ether'})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_disallowed_guess_from_not_signed_up_user(wordle_old_single_signup_test_mode):
    with brownie.reverts("Error: PLAYER NOT SIGNED UP"):
        wordle_old_single_signup_test_mode.makeGuess("HELLO", {'from': accounts[2]})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_invalid_guess_wrong_length(wordle_old_single_signup_test_mode):
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_old_single_signup_test_mode.makeGuess("ABC", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_old_single_signup_test_mode.makeGuess("ABCDEF", {'from': accounts[1]})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_invalid_guess_wrong_characters(wordle_old_single_signup_test_mode):
    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_old_single_signup_test_mode.makeGuess("hello", {'from': accounts[1]})

    with brownie.reverts("Error: INVALID INPUT WORD"):
        wordle_old_single_signup_test_mode.makeGuess("HELL0", {'from': accounts[1]})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_basic_allowed_guess(wordle_old_single_signup_test_mode):
    wordle_old_single_signup_test_mode.makeGuess("HELLO", {'from': accounts[1]})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_get_word_try_1(wordle_old_single_signup_test_mode):
    result = wordle_old_single_signup_test_mode.makeGuess("AUDIO", {'from': accounts[1]})
    assert result.return_value == (0, 0, 0, 0, 0)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is True
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(1) == 1


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_get_word_try_6(wordle_old_single_signup_test_mode):
    result = wordle_old_single_signup_test_mode.makeGuess("PARTY", {'from': accounts[1]})
    assert result.return_value == (2, 1, 2, 2, 2)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 1
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is False

    result = wordle_old_single_signup_test_mode.makeGuess("AAAAA", {'from': accounts[1]})
    assert result.return_value == (0, 2, 2, 2, 2)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 2
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is False

    result = wordle_old_single_signup_test_mode.makeGuess("AUDIT", {'from': accounts[1]})
    assert result.return_value == (0, 0, 0, 0, 2)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 3
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is False

    result = wordle_old_single_signup_test_mode.makeGuess("DDDIO", {'from': accounts[1]})
    assert result.return_value == (2, 2, 0, 0, 0)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 4
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is False

    result = wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    assert result.return_value == (2, 2, 2, 2, 2)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 5
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is False

    result = wordle_old_single_signup_test_mode.makeGuess("AUDIO", {'from': accounts[1]})
    assert result.return_value == (0, 0, 0, 0, 0)

    assert wordle_old_single_signup_test_mode.numberOfGuesses(accounts[1]) == 6
    assert wordle_old_single_signup_test_mode.solved(accounts[1]) is True

    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(0) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(1) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(2) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(3) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(4) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(5) == 0
    assert wordle_old_single_signup_test_mode.getSolvedCountsByGuessNumber(6) == 1


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_get_word_run_out(wordle_old_single_signup_test_mode):
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})
    with brownie.reverts("Error: NUMBER OF GUESSES EXHAUSTED"):
        wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_get_word_already_guessed(wordle_old_single_signup_test_mode):
    wordle_old_single_signup_test_mode.makeGuess("AUDIO", {'from': accounts[1]})
    with brownie.reverts("Error: PLAYER ALREADY GUESSED THE CORRECT WORD"):
        wordle_old_single_signup_test_mode.makeGuess("XXXXX", {'from': accounts[1]})


def makeBadGuess(wordleContract, account):
    wordleContract.makeGuess("XXXXX", {'from': account})


def solveInXTries(wordleContract, account, numTries, actualWord):
    for i in range(numTries - 1):
        makeBadGuess(wordleContract, account)
    wordleContract.makeGuess(actualWord, {'from': account})


def setupSolver(wordleContract, listOfAccounts, listOfNumTries, actualWord):
    for idx, account in enumerate(listOfAccounts):
        solveInXTries(wordleContract, account, listOfNumTries[idx], actualWord)


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_basic_game_4_player(wordle_old_4_player_signup_test_mode):
    setupSolver(wordle_old_4_player_signup_test_mode, accounts[1:5], [1, 3, 4, 6], "AUDIO")

    for account in accounts[1:5]:
        assert wordle_old_4_player_signup_test_mode.solved(account) is True

    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(0) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(1) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(2) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(3) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(4) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(5) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(6) == 1

    paymentSplitterAddress = wordle_old_4_player_signup_test_mode.payoutAndReset().return_value

    # test if the reset worked
    assert wordle_old_4_player_signup_test_mode.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle_old_4_player_signup_test_mode.enabled(account) is False
        assert wordle_old_4_player_signup_test_mode.solved(account) is False

    assert wordle_old_4_player_signup_test_mode.getPlayerCount() == 0
    for i in range(7):
        assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(i) == 0

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


@pytest.mark.require_network("development")
@pytest.mark.skipif(skipTestsOfDeprecatedContract, reason="Skipping test for deprecated contract")
def test_basic_game_4_player_one_guy_didnt_solve(wordle_old_4_player_signup_test_mode):
    setupSolver(wordle_old_4_player_signup_test_mode, accounts[1:4], [3, 4, 5], "AUDIO")

    for account in accounts[1:4]:
        assert wordle_old_4_player_signup_test_mode.solved(account) is True
    assert wordle_old_4_player_signup_test_mode.solved(accounts[4]) is False

    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(0) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(1) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(2) == 0
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(3) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(4) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(5) == 1
    assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(6) == 0

    paymentSplitterAddress = wordle_old_4_player_signup_test_mode.payoutAndReset().return_value

    # test if the reset worked
    assert wordle_old_4_player_signup_test_mode.currGameState() == 0
    for account in accounts[1:5]:
        assert wordle_old_4_player_signup_test_mode.enabled(account) is False
        assert wordle_old_4_player_signup_test_mode.solved(account) is False

    assert wordle_old_4_player_signup_test_mode.getPlayerCount() == 0
    for i in range(7):
        assert wordle_old_4_player_signup_test_mode.getSolvedCountsByGuessNumber(i) == 0

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
