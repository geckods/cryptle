import React from "react";
import { useContext } from "react";
import CryptleLogo from './CryptleLogo';
import AppContext from '../contexts/AppContext';
import Header from "./Header";
import Loading from "./Loading";

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    return (
        <div>
            <Header />
            <CryptleLogo />
            <br/>
            <button id={'signup-button'} onClick={() => wordleInterface.signUp()}>
                <span id={'signup-button-arrow'}>&rarr;</span>
            </button>
        </div>
    );
};

export default SignUp;