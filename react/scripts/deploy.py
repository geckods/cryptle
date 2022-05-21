from brownie import *
import os
import json

def setupWordleOnFuji(lotSize, arrayOfWordListAddresses):
    # arrayOfWordListAddresses = ["0x98046A45a3bf6EF5a326B3F964968AfEB176A246","0xDE994427Afed416e2d3280806f04BD192aE1b835","0x0D9b92967ed16cC9740A2Ae4EAC0fF26e682Cbf6"]
    # lotSize = 1000000000000000000
    wordle = WordleVRF.deploy(lotSize, 75, '0x2ed832ba664535e5886b75d64c46eb9a228c2610', {'from': accounts[0]})

    print(str(wordle.keyHash()))
    if str(wordle.keyHash()) != "0x354d2f95da55398f44b7cff77da56283d9c6c829a4bdf1bbcaf2ad6a4d081f61":
        wordle.setKeyHash("0x354d2f95da55398f44b7cff77da56283d9c6c829a4bdf1bbcaf2ad6a4d081f61")

    with open(
            "client/src/artifacts/contracts/WordList.json",
            'r') as f:
        wordlistAbi = json.load(f)['abi']

    for wordListAddress in arrayOfWordListAddresses:
        wl = Contract.from_abi("myWordList", wordListAddress, wordlistAbi)
        for i in range(0,wl.getWordListLength(), 300):
            wordle.appendToAllowedGuessesWordList(wordListAddress, i, min(i+300, wl.getWordListLength()))

    wl = Contract.from_abi("myWordList", arrayOfWordListAddresses[0], wordlistAbi)
    wordle.appendToTargetWordLists(arrayOfWordListAddresses[0], 0, min(500, wl.getWordListLength()))

    wordle.initGame()

    print("Deployment Address: ", wordle.address)
    print("Remember to allowlist this contract with chainlink VRF subscription manager! Go to https://vrf.chain.link/fuji/75 and add this as a consumer")
    # print("updating environment variable: CURRENT_WORDLE_ADDRESS, will take effect on next ")
    # os.environ.
    return wordle


def main():
    # requires brownie account to have been created
    if network.show_active()=='development':
        # add these accounts to metamask by importing private key
        owner = accounts[0]

    elif network.show_active() == 'avax-test':
        # add these accounts to metamask by importing private key
        accounts.add(os.environ['PRIMARY_TEST_ACCOUNT_PRIVATE_KEY'])
        owner = accounts[0]

        setupWordleOnFuji(1000000000000000000, ["0x98046A45a3bf6EF5a326B3F964968AfEB176A246","0xDE994427Afed416e2d3280806f04BD192aE1b835","0x0D9b92967ed16cC9740A2Ae4EAC0fF26e682Cbf6"])