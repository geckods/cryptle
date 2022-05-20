import '../App.css';
import React, { useContext, useEffect, useState } from 'react';
import AppContext from '../contexts/AppContext';
import Play from './Play';
import SignUp from './SignUp';
import Payout from "./Payout";
import Header from './Header';
import CryptleLogo from './CryptleLogo';

function Main() {
  const context = useContext(AppContext);
  const enabled = context.getPlayer().enabled;
  const gameState = Number(context.getPlayer().currGameState);

  return (
    <div className="App">
      <div className='full-width'>
        <Header/>
        <br/>
        {
        (gameState)?
            (enabled) ?
                <Play /> :
                <SignUp />
            :
            <div className='full-width'>
                <CryptleLogo />
                <Payout/>
            </div>
        }
      </div>
    </div>
  );
}

export default Main;