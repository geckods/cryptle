import '../App.css';
import React, { useContext, useState } from 'react';
import AppContext from '../contexts/AppContext';
import WordleGrid from './WordleGrid';
import { isValidGuess } from '../utils/WordleUtils';

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

    const makeGuess = () => {
        if (isValidGuess(guess)) {
            setGuessing(true);
            wordleInterface.makeGuess(guess).then((tx) => {
                console.log(tx);
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
                <WordleGrid />
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