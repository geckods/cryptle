import React from "react";
import { useContext, useEffect, useState } from "react";
import CryptleLogo from './CryptleLogo';
import AppContext from '../contexts/AppContext';
import Payout from "./Payout";

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();
    const [signingUp, setSigningUp] = useState(false);

    const [signUpCost, setSignUpCost] = useState(0);
    const [numPlayers, setNumPlayers] = useState(0);

    useEffect(() => {
      wordleInterface.getSignUpCost().then((tx) => {
        setSignUpCost(tx);
      });
      wordleInterface.getNumPlayers().then((tx) => {
        setNumPlayers(tx);
      });
    });

    const signUp = () => {

        setSigningUp(true);
        wordleInterface.signUp(signUpCost).then((tx) => {
            window.location.reload(false);
        })
        .catch((e) => {
            alert('Error');
            console.log(e);
            setSigningUp(false);
        });


    };


//     TODO: parameterize currency into a global variable which is fetched based on the chain
    return (
        <div className='half-width'>
            <CryptleLogo />
            <br/>
            {
                (signingUp) ?
                <button id={'signup-button'} disabled>
                    Signing Up..
                </button>:
                <div>
                    <div>SIGN UP FEE: {signUpCost/(1e18)} AVAX</div>
                    <button  id={'signup-button'} onClick={signUp}>
                        PLAY
                    </button>
                    <div>{numPlayers} PLAYERS</div>
                </div>
            }
            <div className={'separator'}></div>
            <Payout/>
        </div>
    );
};

export default SignUp;