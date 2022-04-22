from brownie import *

def getBalanceInEth(account):
    return float(account.balance())/1e18

def getBalancesInEth(accountList):
    return [getBalanceInEth(account) for account in accountList]