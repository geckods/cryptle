import React, {useEffect, useState} from "react"
import './App.css'
import {getWeb3} from "./getWeb3"
import map from "./artifacts/deployments/map.json"
import {getEthereum} from "./getEthereum"
import Main from "./components/Main"
import AppContext from "./contexts/AppContext"
import WordleContractInterface from "./services/WordleContractInterface"
import { accountsAvailable } from "./utils/Web3Utils"

const App = () =>{

    const initialAppState = {
        web3: null,
        accounts: null,
        chainid: null,
        wordle: null,
        enabled: false,
        wordleInterface: null,
        player: {
            guesses: [],
            results: []
        }
    };

    const [state, setState] = useState(initialAppState);

    const contextFunctions = {
        getAccounts: () => {
            return state.accounts
        },
        getActiveAccount: () => {
            return state.accounts[0]
        },
        getChainId: () => {
            return state.chainid
        },
        isGameEnabled: () => {
            return state.enabled
        },
        getWordle: () => {
            return state.wordle
        },
        getWordleInterface: () => {
            return state.wordleInterface
        }
    };

    useEffect(() => {
        const func = async () => {
            // Get network provider and web3 instance.
            const web3 = await getWeb3();

            // Try and enable accounts (connect metamask)
            try {
                const ethereum = await getEthereum();
                ethereum.enable();

                // Use web3 to get the user's accounts
                const accounts = await web3.eth.getAccounts();

                if (accountsAvailable(accounts)) {
                    // Get the current chain id
                    const chainid = parseInt(await web3.eth.getChainId());

                    const wordle = await loadContract("dev", "Wordle", web3);
                    const enabled = await wordle.methods.enabled(accounts[0]).call();

                    let player = localStorage.getItem(accounts[0]);

                    if (player) {
                        player = JSON.parse(player);
                    } else {
                        player = initialAppState.player;
                        localStorage.setItem(accounts[0], JSON.stringify(player));
                    }

                    setState({
                        accounts: accounts,
                        web3: web3,
                        chainid: chainid,
                        wordle: wordle,
                        enabled: (enabled) ?? false,
                        wordleInterface: new WordleContractInterface(wordle, accounts[0]),
                        player: player
                    });
                }
            } catch (e) {
                console.log(`Could not enable accounts. Interaction with contracts not available.
                Use a modern browser with a Web3 plugin to fix this issue.`);
                console.log(e);
            }    
        }

        func();

    }, []);

    const loadContract = async (chain, contractName, web3) => {
        // Load a deployed contract instance into a web3 contract object
        // const {web3} = state

        // Get the address of the most recent deployment from the deployment map
        let address
        try {
            address = map[chain][contractName][0]
        } catch (e) {
            console.log(`Couldn't find any deployed contract "${contractName}" on the chain "${chain}".`)
            return undefined
        }

        // Load the artifact with the specified address
        let contractArtifact
        try {
            contractArtifact = await import(`./artifacts/deployments/${chain}/${address}.json`)
        } catch (e) {
            console.log(`Failed to load contract artifact "./artifacts/deployments/${chain}/${address}.json"`)
            return undefined
        }

        return new web3.eth.Contract(contractArtifact.abi, address)
    }

    return (
        <AppContext.Provider value={contextFunctions}>
            {
                (state.web3 && state.chainid) ?
                <Main /> :
                <div>Disconnected</div>
            }
        </AppContext.Provider>
    )
}

export default App
