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
            <Loading/>
        :
        <div id={'payout'}>
            <div>
                Your balance: {balance}
            </div>
            {
                balance>0 && <button onClick={getFunds}>Withdraw</button>
            }
        </div>
    )
};

export default Payout;