import '../App.css';
import React, { useContext } from 'react';
import AppContext from '../contexts/AppContext';

const SignUp = () => {
    const context = useContext(AppContext);

    const signUp = () => {
        const wordle = context.getWordle();
        wordle.methods.signUp().send({value: 1000000000000000000, from: context.getAccounts()[0]}).then((tx) => {
            console.log(tx);
        }).catch((e) => {
            console.log('error');
            console.log(e);
        });
    };

    return (
        <button onClick={signUp}>
            Sign Up
        </button>
    )
};

const Play = () => {
    return (
        <div>Placeholder</div>
    )
}

function Main() {
  const context = useContext(AppContext);
  const enabled = context.isGameEnabled();

  return (
    <div className="App">
      <header>
        Welcome {context.getAccounts().join('\n')}
      </header>
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