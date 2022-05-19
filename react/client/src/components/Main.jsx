import '../App.css';
import React, { useContext, useEffect, useState } from 'react';
import AppContext from '../contexts/AppContext';
import Play from './Play';
import SignUp from './SignUp';
import Payout from "./Payout";

function Main() {

  console.log("We are in main");
  const context = useContext(AppContext);
  const enabled = context.getPlayer().enabled;
  const gameState = Number(context.getPlayer().currGameState);
  console.log(gameState);

  return (
    <div className="App">
      <br/>
      <div>
          {
          (gameState)?
              (enabled) ?
                  <Play /> :
                  <SignUp />
              :
                <Payout/>
          }
      </div>
    </div>
  );
}

export default Main;