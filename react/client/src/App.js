import React, {useEffect, useState} from "react"
import './App.css'
import {getWeb3} from "./getWeb3"
import {getEthereum} from "./getEthereum"
import Main from "./components/Main"
import AppContext from "./contexts/AppContext"
import WordleContractInterface from "./services/WordleContractInterface"
import { accountsAvailable } from "./utils/Web3Utils"
import Loading from "./components/Loading"
import Disconnected from "./components/Disconnected";
import { isValidGuess } from "./utils/WordleUtils"

const initialAppState = {
    web3: null,
    accounts: null,
    chainid: null,
    wordleInterface: null,
    player: null,
    loading: true
};

const App = () =>{

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
        getState: () => {
            return state;
        },
        getPlayer: () => {
            return state.player
        },
        setPlayer: (player1) => {
            setState({
                ...state, player: player1
            })
        }
    };

    useEffect(() => {
        const func = async () => {
            const web3 = await getWeb3();
            try {
                const ethereum = await getEthereum();
                ethereum.enable();
                const accounts = await web3.eth.getAccounts();
                if (accountsAvailable(accounts)) {
                    // Get the current chain id
                    const chainid = parseInt(await web3.eth.getChainId());
                    const wordleArtifact = await import(`./artifacts/contracts/WordleVRF.json`);
                    const wordle = new web3.eth.Contract(wordleArtifact.abi, "0x99e1978d0ffB5c86AF2C12B29817682282397CF2");
                    const wordleInterface = new WordleContractInterface(web3, wordle, accounts[0])
                    const playerState = await wordleInterface.getPlayerState();

                    console.log(playerState);

                    setState({
                        accounts: accounts,
                        web3: web3,
                        chainid: chainid,
                        wordleInterface: wordleInterface,
                        player: playerState,
                        loading: false
                    });
                } else {
                    setState({
                        ...state,
                        loading: false
                    })
                }
            } catch (e) {
                console.log(`Could not enable accounts. Interaction with contracts not available.
                Use a modern browser with a Web3 plugin to fix this issue.`);
                console.log(e);
                setState({
                    ...state,
                    loading: false
                })
            }
        }
        func();
    }, []);

    return (
        <AppContext.Provider value={contextFunctions}>
            {
                (state.loading) ?
                <Loading /> :
                (state.web3 && state.chainid) ?
                <Main /> :
                <Disconnected />
            }
        </AppContext.Provider>
    )
}

export default App
