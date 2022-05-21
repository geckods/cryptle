from brownie import *
import os
import json

def main():
    # requires brownie account to have been created
    if network.show_active()=='development':
        # add these accounts to metamask by importing private key
        owner = accounts[0]

    elif network.show_active() == 'avax-test':
        # add these accounts to metamask by importing private key
        accounts.add(os.environ['PRIMARY_TEST_ACCOUNT_PRIVATE_KEY'])
        owner = accounts[0]

        with open(
                "/home/geckods/Blockchain/cryptle/react/client/src/artifacts/contracts/WordleVRF.json",
                'r') as f:
            wordleAbi = json.load(f)['abi']

        wordle = Contract.from_abi("wordle", os.environ['CURRENT_WORDLE_ADDRESS'], wordleAbi, accounts[0])

        if wordle.getPlayerCount() > 0:
            wordle.payoutAndReset({'from':owner})
            wordle.initGame({'from': owner})

#             CRONTAB:
# PRIMARY_TEST_ACCOUNT_PRIVATE_KEY=0x...
# CURRENT_WORDLE_ADDRESS=0x...
#
# 59 23 * * *  cd /home/geckods/Blockchain/cryptle/react && /home/geckods/Blockchain/cryptle/env/bin/brownie run /home/geckods/Blockchain/cryptle/react/scripts/payoutResetInit.py --network avax-test