import '../App.css';
import React, { useContext, useState } from 'react';
import AppContext from '../contexts/AppContext';
import WordleGrid from './WordleGrid';
import { isValidGuess } from '../utils/WordleUtils';
import { getValues, save } from '../utils/StorageUtils';

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    return (
        <button onClick={() => wordleInterface.signUp()}>
            Sign Up
        </button>
    )
};

const Play = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    const [guessing, setGuessing] = useState(false);
    const [guess, setGuess] = useState('');

    const player = JSON.parse(localStorage.getItem(context.getActiveAccount()));

    const makeGuess = () => {
        if (isValidGuess(guess)) {
            setGuessing(true);
            wordleInterface.makeGuess(guess).then((tx) => {
                console.log(tx);
                save(guess, tx, context.getActiveAccount());
            }).catch((e) => {
                console.log('error');
                console.log(e);
                setGuessing(false);
            });
        } else {
            alert('invalid guess');
        }
    };
    
    return (
        <div>
            {
            (!guessing) ?
            <div>
                <WordleGrid guesses={player.guesses} results={player.results} />
                <input 
                    id='guess-string' 
                    maxLength={5} 
                    minLength={5}
                    value={guess}
                    onChange={(event) => {
                        setGuess(event.currentTarget.value);
                    }}
                />
                <br/>
                <button onClick={() => makeGuess()}>Submit Guess</button>
            </div>:
            <div>Guessing ...</div>
            }
        </div>
    )
}

function Main() {
  const context = useContext(AppContext);
  const enabled = context.isGameEnabled();

  return (
    <div className="App">
      <header>
        Welcome {context.getActiveAccount()}
      </header>
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