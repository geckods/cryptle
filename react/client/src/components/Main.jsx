import '../App.css';
import React, { useContext, useEffect, useState } from 'react';
import AppContext from '../contexts/AppContext';
import Play from './Play';
import SignUp from './SignUp';

function Main() {
  const context = useContext(AppContext);
  const enabled = context.getPlayer().enabled;

  return (
    <div className="App">
      <br/>
      <div>
          {
              (enabled) ?
              <Play /> :
              <SignUp />
          }
      </div>
    </div>
  );
}

export default Main;