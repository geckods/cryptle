import React, { useContext, useEffect, useState } from 'react';
import WordleGrid from './WordleGrid';
import AppContext from '../contexts/AppContext';
import { isValidGuess } from '../utils/WordleUtils';
import Payout from "./Payout";
import RICIBs from 'react-individual-character-input-boxes';

const Play = () => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    const [player, setPlayer] = useState(context.getPlayer());

    console.log('AAA');
    console.log(player);


    const [guessing, setGuessing] = useState(player.userGuessState);
    const [guess, setGuess] = useState('');
    const [cool, setCool] = useState('');

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
        <div className='half-width'>
            <WordleGrid guesses={player.guesses} results={player.results} />
            <br/>
            <Payout/>
        </div> :
        <div className='half-width'>
            {
            (!guessing) ?
            <div className='full-width'>
                <WordleGrid guesses={player.guesses} results={player.results} />
                {/* <input
                    id='guess-string'
                    maxLength={5}
                    minLength={5}
                    value={guess}
                    onChange={(event) => {
                        setGuess(event.currentTarget.value);
                    }}
                /> */}
                <div className='separator'></div>
                <div>
                    <RICIBs
                    amount={5}
                    autoFocus
                    handleOutputString={(event) => {
                        setGuess(event);
                    }}
                    inputProps={[
                        {className: 'guess-input'},
                        {className: 'guess-input'},
                        {className: 'guess-input'},
                        {className: 'guess-input'},
                        {className: 'guess-input'}
                    ]}
                    inputRegExp={/^[a-zA-Z]$/}
                    />
                </div>
                <br/>
                <button id={'make-guess'} onClick={() => makeGuess()}>Submit Guess</button>
            </div>:
            <div className='full-width'>
                Guessing ...
                <WordleGrid guesses={player.guesses} results={player.results} />
            </div>
            }
        </div>
        
    )
}

export default Play;