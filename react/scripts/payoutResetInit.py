from brownie import *
import os
import json


def main():
    print("Network:", network.show_active())
    # requires brownie account to have been created
    if network.show_active() == 'development':
        # add these accounts to metamask by importing private key
        owner = accounts[0]

    elif network.show_active() == 'avax-test':
        # add these accounts to metamask by importing private key
        print("Adding Private Key")
        accounts.add(os.environ['PRIMARY_TEST_ACCOUNT_PRIVATE_KEY'])
        owner = accounts[0]

        print("Fetching JSON ABI")
        print("current working directory", os.getcwd())
        with open(
                "../client/src/artifacts/contracts/WordleVRF.json",
                'r') as f:
            wordleAbi = json.load(f)['abi']

        wordle = Contract.from_abi("wordle", os.environ['CURRENT_WORDLE_ADDRESS'], wordleAbi, accounts[0])

        if wordle.currGameState() == 0:
            print("initGame")
            wordle.initGame({'from': owner})
        elif wordle.getPlayerCount() > 0:
            print("payoutAndReset")
            wordle.payoutAndReset({'from': owner})
            print("initGame")
            wordle.initGame({'from': owner})
        else:
            print("Game initialised and no players signed up. Abandoning reset!")


#             CRONTAB:
# PRIMARY_TEST_ACCOUNT_PRIVATE_KEY=0x...
# CURRENT_WORDLE_ADDRESS=0x...
#
# 59 23 * * *  cd /home/geckods/Blockchain/cryptle/react && /home/geckods/Blockchain/cryptle/env/bin/brownie run /home/geckods/Blockchain/cryptle/react/scripts/payoutResetInit.py --network avax-test

if __name__ == "__main__":
    network.connect('avax-test')
    main()
