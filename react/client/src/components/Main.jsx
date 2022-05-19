import '../App.css';
import React, { useContext, useEffect, useState } from 'react';
import AppContext from '../contexts/AppContext';
import WordleGrid from './WordleGrid';
import { isValidGuess } from '../utils/WordleUtils';
import CryptleLogo from './CryptleLogo';

const SignUp = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    return (
        <div>
            <CryptleLogo />
            <br/>
            <button id={'signup-button'} onClick={() => wordleInterface.signUp()}>
                Sign Up
            </button>
        </div>
    );
};

const Play = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    const [player, setPlayer] = useState(context.getPlayer());

    console.log('AAA');
    console.log(player);


    const [guessing, setGuessing] = useState(player.userGuessState);
    const [guess, setGuess] = useState('');

    const isGameComplete = async () => {
        const guessCount = context.getPlayer().results.length;
        const isSolved = context.getPlayer().solved;
        return isSolved || (guessCount === 6 && context.getPlayer().userGuessState == 0);
    };


    const [loading, setLoading] = useState(1);
    const [complete, setComplete] = useState(-1);


    useEffect(() => {
        isGameComplete().then((result) => {
            setComplete(result);
            setLoading(0);
        })

        if(guessing){
            wordleInterface.pollGuessResult().then((result) => {
                wordleInterface.getPlayerState().then((player) => {
                    context.setPlayer(player);
                });
            });
        }

    }, [player]);

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

    const widthdrawFunds = () => {
        wordleInterface.widthdrawFunds().then((tx) => {
            console.log(tx);
            alert('Success');
        }).catch((e) => {
            console.log(e);
            alert('Fail');
        });
    }
    
    return (
        (complete) ?
        <div>
            <WordleGrid guesses={player.guesses} results={player.results} />
            <br/>
            <button onClick={() => widthdrawFunds()}>Withdraw Funds</button>
        </div> :
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
            <div>Guessing ...
                <WordleGrid guesses={player.guesses} results={player.results} />
            </div>
            }
        </div>
        
    )
}

function Main() {
  const context = useContext(AppContext);
  const enabled = context.getPlayer().enabled;

  
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