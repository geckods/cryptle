import React from "react";
import { useState, useEffect, useContext } from "react";
import CryptleLogo from './CryptleLogo';
import AppContext from '../contexts/AppContext';
import Header from "./Header";
import Loading from "./Loading";

const Payout = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    const [loading, setLoading] = useState(true);
    const [balance, setBalance] = useState(-1);

    useEffect( () => {
        wordleInterface.getAccountBalance().then((returnedBalance) => {
            setBalance(returnedBalance);
            setLoading(false);
        });
    })

    const getFunds = () => {
        wordleInterface.withdrawOutstandingBalance().then((tx) => {
            alert(JSON.stringify(tx));
        }).catch( (e) => {
            alert("error");
            console.log(e);
        });
    }

    return (
        (loading)?
            <div>Loading ...</div>
        :
        <div id={'payout'}>
            <div id={'balance-container'}>
                Your balance 
                <br/>
                <span id={'balance'}>{Number(balance)/Math.pow(10,18)}</span>
            </div>
            {
                balance>0 && <button id={'withdraw'} onClick={getFunds}>Withdraw</button>
            }
        </div>
    )
};

export default Payout;