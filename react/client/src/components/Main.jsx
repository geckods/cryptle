import '../App.css';
import React, { useContext, useState } from 'react';
import AppContext from '../contexts/AppContext';
import WordleGrid from './WordleGrid';

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
    const context = useContext(AppContext);
    const [guessing, setGuessing] = useState(false);
    const [guess, setGuess] = useState('');

    const isValidGuess = (guess) => {
        if (guess.length !== 5) {
            return false;
        }
        if(/^[a-zA-Z]+$/.test(guess)) {
            return true;
        }
        return false;
    };

    const makeGuess = () => {
        if (isValidGuess(guess)) {
            console.log('Guessing');
            setGuessing(true);
            const wordle = context.getWordle();
            wordle.methods.makeGuess(guess.toUpperCase()).send({from: context.getActiveAccount()}).then((tx) => {
                console.log(tx);
                wordle.methods.getGuessResult().call({from: context.getActiveAccount()}).then((tx1) => {
                    console.log('GetResult o/p');
                    console.log(tx1);
                }).catch((e) => {
                    console.log('error');
                    console.log(e);
                }).finally(() => {
                    setGuessing(false);
                });
            }).catch((e) => {
                console.log('error');
                console.log(e);
                setGuessing(false);
            });
        } else {
            alert('invalid guess');
        }
    };
    
    const getGuessResult = () => {
        
    }

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
        Welcome {context.getAccounts().join('\n')}
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