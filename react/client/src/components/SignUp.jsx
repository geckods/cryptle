import React from "react";
import { useContext } from "react";
import CryptleLogo from './CryptleLogo';
import AppContext from '../contexts/AppContext';
import Payout from "./Payout";

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    return (
        <div className='half-width'>
            <CryptleLogo />
            <br/>
            <button id={'signup-button'} onClick={() => wordleInterface.signUp()}>
                Play
            </button>
            <div className={'separator'}></div>
            <Payout/>
        </div>
    );
};

export default SignUp;