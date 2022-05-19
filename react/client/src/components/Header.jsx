import React from "react";
import { useContext } from "react";
import AppContext from '../contexts/AppContext';

const Header = () => {
    const context = useContext(AppContext);
    return (
        <header>
            Welcome {context.getActiveAccount()}
        </header>
    );
};

export default Header;