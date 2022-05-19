import React, {useEffect, useState} from "react"
import './App.css'
import {getWeb3} from "./getWeb3"
import map from "./artifacts/deployments/map.json"
import {getEthereum} from "./getEthereum"
import Main from "./components/Main"
import AppContext from "./contexts/AppContext"
import WordleContractInterface from "./services/WordleContractInterface"
import { accountsAvailable } from "./utils/Web3Utils"
import Loading from "./components/Loading"

const App = () =>{

    const initialAppState = {
        web3: null,
        accounts: null,
        chainid: null,
        wordleInterface: null,
        player: null,
        loading: true
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
        getWordleInterface: () => {
            return state.wordleInterface
        },
        getPlayer: () => {
            return state.player
        },
        setPlayer: (player) => {
            setState({
                ...state, player: player
            })

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

//                    const wordle = await loadContract("dev", "WordleVRF", web3);
                    const wordleArtifact = await import(`./artifacts/contracts/WordleVRF.json`);
                    const wordle = new web3.eth.Contract(wordleArtifact.abi, "0x4E2F7e4De568B56d2CDf9022bADf8843bD6F1eD4");
                    const wordleInterface = new WordleContractInterface(web3, wordle, accounts[0])
                    console.log(wordle);

                    const playerState = await wordleInterface.getPlayerState();

                    let player = playerState;

                    setState({
                        accounts: accounts,
                        web3: web3,
                        chainid: chainid,
                        wordleInterface: wordleInterface,
                        player: player,
                        loading: false
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
                (state.loading) ?
                <Loading /> :
                (state.web3 && state.chainid) ?
                <Main /> :
                <div>Disconnected</div>
            }
        </AppContext.Provider>
    )
}

export default App
