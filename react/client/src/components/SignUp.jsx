import React from "react";
import { useContext } from "react";
import CryptleLogo from './CryptleLogo';
import AppContext from '../contexts/AppContext';
import Payout from "./Payout";
import { useState } from "react";

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();
    const [signingUp, setSigningUp] = useState(false);

    const signUp = () => {
        setSigningUp(true);
        wordleInterface.signUp().then((tx) => {
            console.log(tx);
            window.location.reload(false);
        }).catch((e) => {
            alert('Error');
            console.log(e);
            setSigningUp(false);
        });
    };


    return (
        <div className='half-width'>
            <CryptleLogo />
            <br/>
            {
                (signingUp) ?
                <button id={'signup-button'} onClick={signUp}>
                    Play
                </button> :
                <button id={'signup-button'} disabled>
                    Signing Up..
                </button>
            }            
            <div className={'separator'}></div>
            <Payout/>
        </div>
    );
};

export default SignUp;