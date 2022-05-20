import React from "react";
import { useContext } from "react";
import AppContext from '../contexts/AppContext';
import { getChainFromChainId } from "../utils/Web3Utils";

const Header = () => {
    const context = useContext(AppContext);
    const chain = getChainFromChainId(context.getChainId());
    return (
        <header id={'header'}>
             <span id={'chain-id'} className={chain}>{chain}</span>
             <span id={'active-account'}>{context.getActiveAccount().substr(0,10)}</span> 
        </header>
    );
};

export default Header;