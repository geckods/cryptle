from brownie import *


def getBalanceInEth(account):
    return float(account.balance()) / 1e18


def getBalancesInEth(accountList):
    return [getBalanceInEth(account) for account in accountList]


def setupWordleVRFOnLocalBlockchain():
    accounts[0].deploy(VRFCoordinatorV2Mock, 0.1, 0.1)
    VRFCoordinatorV2Mock[0].createSubscription()
    VRFCoordinatorV2Mock[0].fundSubscription(1, 10000000000)
    accounts[0].deploy(WordList)
    accounts[0].deploy(WordleVRF, [WordList[0].address], '0.1 ether', 1)
    WordleVRF[0].initGame()
    return WordleVRF[0], VRFCoordinatorV2Mock[0]


def setupWordleVRFOnLocalBlockchainWithSignup():
    wordle, vrfMock = setupWordleVRFOnLocalBlockchain()
    wordle.signUp({'from': accounts[1], 'value': '0.1 ether'})
    return wordle, vrfMock

def main():
    setupWordleVRFOnLocalBlockchainWithSignup()