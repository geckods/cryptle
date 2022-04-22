import json

import pytest
import brownie
from brownie import *


@pytest.fixture(scope="module")
def wordle_basic_deploy(accounts, Wordle):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    yield accounts[0].deploy(Wordle)


@pytest.fixture(scope="module")
def wordle_single_signup(wordle_basic_deploy, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_single_signup = wordle_basic_deploy
    wordle_single_signup.signUp({'from': accounts[1], 'amount': '1 ether'})
    return wordle_single_signup


@pytest.fixture(scope="module")
def wordle_4_player_signup(wordle_single_signup, accounts):
    """
    Yield a 'Contract' object for the Wordle contract.
    """
    wordle_4_player_signup = wordle_single_signup
    wordle_4_player_signup.signUp({'from': accounts[2], 'amount': '1 ether'})
    wordle_4_player_signup.signUp({'from': accounts[3], 'amount': '1 ether'})
    wordle_4_player_signup.signUp({'from': accounts[4], 'amount': '1 ether'})
    return wordle_4_player_signup


# @pytest.fixture(scope="module")
# def wordle_4_player_signup(wordle_single_signup, accounts):
#     """
#     Yield a 'Contract' object for the Wordle contract.
#     """
#     wordle_4_player_signup = wordle_single_signup
#     wordle_4_player_signup.signUp({'from': accounts[2], 'amount': '1 ether'})
#     wordle_4_player_signup.signUp({'from': accounts[3], 'amount': '1 ether'})
#     wordle_4_player_signup.signUp({'from': accounts[4], 'amount': '1 ether'})
#     return wordle_4_player_signup


def test_sign_up_insufficient(wordle_basic_deploy):
    with brownie.reverts():
        wordle_basic_deploy.signUp({'from': accounts[1], 'amount': '0.5 ether'})


def test_sign_up_sufficient(wordle_basic_deploy):
    wordle_basic_deploy.signUp({'from': accounts[1], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert wordle_basic_deploy.balance() == '1 ether'
    assert wordle_basic_deploy.playersList(0) == accounts[1]
    assert wordle_basic_deploy.number_of_guesses(accounts[1]) == 0
    assert wordle_basic_deploy.solved(accounts[1]) is False
    assert wordle_basic_deploy.enabled(accounts[1]) is True


def test_multiple_sign_up_sufficient(wordle_basic_deploy):
    wordle_basic_deploy.signUp({'from': accounts[1], 'amount': '1 ether'})
    wordle_basic_deploy.signUp({'from': accounts[2], 'amount': '1 ether'})

    assert accounts[1].balance() == '99 ether'
    assert accounts[2].balance() == '99 ether'
    assert wordle_basic_deploy.balance() == '2 ether'
    assert wordle_basic_deploy.playersList(0) == accounts[1]
    assert wordle_basic_deploy.playersList(1) == accounts[2]


def test_cannot_sign_up_twice(wordle_single_signup):
    with brownie.reverts():
        wordle_single_signup.signUp({'from': accounts[1], 'amount': '1 ether'})


def test_disallowed_guess_from_not_signed_up_user(wordle_single_signup):
    result = wordle_single_signup.makeGuess("HELLO", {'from': accounts[2]})
    assert result.return_value[0] is False


def test_invalid_guess_wrong_length(wordle_single_signup):
    result = wordle_single_signup.makeGuess("ABC", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is False

    result = wordle_single_signup.makeGuess("ABCDEF", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is False


def test_invalid_guess_wrong_characters(wordle_single_signup):
    result = wordle_single_signup.makeGuess("hello", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is False

    result = wordle_single_signup.makeGuess("HELL0", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is False


def test_basic_allowed_guess(wordle_single_signup):
    result = wordle_single_signup.makeGuess("HELLO", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True


def test_get_word_try_1(wordle_single_signup):
    result = wordle_single_signup.makeGuess("AUDIO", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (0, 0, 0, 0, 0)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 1
    assert wordle_single_signup.solved(accounts[1]) is True
    assert wordle_single_signup.getSolvedCountsByGuessNumber(1).return_value == 1


def test_get_word_try_6(wordle_single_signup):
    result = wordle_single_signup.makeGuess("PARTY", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (2, 1, 2, 2, 2)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 1
    assert wordle_single_signup.solved(accounts[1]) is False

    result = wordle_single_signup.makeGuess("AAAAA", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (0, 2, 2, 2, 2)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 2
    assert wordle_single_signup.solved(accounts[1]) is False

    result = wordle_single_signup.makeGuess("AUDIT", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (0, 0, 0, 0, 2)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 3
    assert wordle_single_signup.solved(accounts[1]) is False

    result = wordle_single_signup.makeGuess("DDDIO", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (2, 2, 0, 0, 0)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 4
    assert wordle_single_signup.solved(accounts[1]) is False

    result = wordle_single_signup.makeGuess("XXXXX", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (2, 2, 2, 2, 2)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 5
    assert wordle_single_signup.solved(accounts[1]) is False

    result = wordle_single_signup.makeGuess("AUDIO", {'from': accounts[1]})
    assert result.return_value[0] is True
    assert result.return_value[1] is True
    assert result.return_value[2] == (0, 0, 0, 0, 0)

    assert wordle_single_signup.number_of_guesses(accounts[1]) == 6
    assert wordle_single_signup.solved(accounts[1]) is True

    assert wordle_single_signup.getSolvedCountsByGuessNumber(0).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(1).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(2).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(3).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(4).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(5).return_value == 0
    assert wordle_single_signup.getSolvedCountsByGuessNumber(6).return_value == 1


def makeBadGuess(wordleContract, account):
    wordleContract.makeGuess("XXXXX", {'from': account})


def solveInXTries(wordleContract, account, numTries, actualWord):
    for i in range(numTries - 1):
        makeBadGuess(wordleContract, account)
    wordleContract.makeGuess(actualWord, {'from': account})


def setupSolver(wordleContract, listOfAccounts, listOfNumTries, actualWord):
    for idx, account in enumerate(listOfAccounts):
        solveInXTries(wordleContract, account, listOfNumTries[idx], actualWord)


def test_basic_game_4_player(wordle_4_player_signup):
    setupSolver(wordle_4_player_signup, accounts[1:5], [1, 3, 4, 6], "AUDIO")

    for account in accounts[1:5]:
        assert wordle_4_player_signup.solved(account) is True

    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(0).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(1).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(2).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(3).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(4).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(5).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(6).return_value == 1

    paymentSplitterAddress = wordle_4_player_signup.payoutAndReset().return_value

    # test if the reset worked
    for account in accounts[1:5]:
        assert wordle_4_player_signup.enabled(account) is False
        assert wordle_4_player_signup.solved(account) is False

    assert wordle_4_player_signup.getPlayerCount() == 0
    for i in range(7):
        assert wordle_4_player_signup.getSolvedCountsByGuessNumber(i).return_value == 0

    with open("client/src/artifacts/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.5.0/PaymentSplitter.json", 'r') as f:
        abi = json.load(f)['abi']

    paymentSplitter = Contract.from_abi("myPaymentSplitter",paymentSplitterAddress, abi)

    assert paymentSplitter.balance() > 0

    shares = [paymentSplitter.shares(account) for account in accounts[1:5]]
    assert shares == [10000,2000,1000,100]

    for account in accounts[1:5]:
        if paymentSplitter.shares(account) > 0:
            paymentSplitter.release(account, {'from': account})

    for i in range(1,4):
        assert accounts[i].balance() > accounts[i+1].balance()

def test_basic_game_4_player_one_guy_didnt_solve(wordle_4_player_signup):
    setupSolver(wordle_4_player_signup, accounts[1:4], [3, 4, 5], "AUDIO")

    for account in accounts[1:4]:
        assert wordle_4_player_signup.solved(account) is True
    assert wordle_4_player_signup.solved(accounts[4]) is False

    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(0).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(1).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(2).return_value == 0
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(3).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(4).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(5).return_value == 1
    assert wordle_4_player_signup.getSolvedCountsByGuessNumber(6).return_value == 0

    paymentSplitterAddress = wordle_4_player_signup.payoutAndReset().return_value

    # test if the reset worked
    for account in accounts[1:5]:
        assert wordle_4_player_signup.enabled(account) is False
        assert wordle_4_player_signup.solved(account) is False

    assert wordle_4_player_signup.getPlayerCount() == 0
    for i in range(7):
        assert wordle_4_player_signup.getSolvedCountsByGuessNumber(i).return_value == 0

    with open("client/src/artifacts/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.5.0/PaymentSplitter.json", 'r') as f:
        abi = json.load(f)['abi']

    paymentSplitter = Contract.from_abi("myPaymentSplitter",paymentSplitterAddress, abi)

    assert paymentSplitter.balance() > 0

    shares = [paymentSplitter.shares(account) for account in accounts[1:5]]
    assert shares == [2000,1000,500,0]

    for account in accounts[1:5]:
        if paymentSplitter.shares(account) > 0:
            paymentSplitter.release(account, {'from': account})

    for i in range(1,4):
        assert accounts[i].balance() > accounts[i+1].balance()