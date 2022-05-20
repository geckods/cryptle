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

    const [gettingGuessResult, setGettingGuessResult] = useState(player.userGuessState);
    const [guessing, setGuessing] = useState(false);

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

        if(!guessing && Number(gettingGuessResult)){
            wordleInterface.pollGuessResult().then((result) => {
                wordleInterface.getPlayerState().then((player) => {
                    context.setPlayer(player);
                    window.location.reload(false);
                });
            });
        }

    }, [player]);

    const makeGuess = () => {
        if (isValidGuess(guess)) {
            setGuessing(true);
            wordleInterface.makeGuess(guess).then((tx) => {
                console.log(tx);
                window.location.reload(false);
            }).catch((e) => {
                console.log('error');
                console.log(e);
                setGuessing(false);
            });
        } else {
            alert('invalid guess');
        }
    };

    const GettingResultState = () => {
        return (
            <div className='full-width'>
                <button id={'make-guess'} disabled>Getting Result ...</button>
            </div>
        );
    };

    const MakingGuessState = () => {
        return (
            <div className='full-width'>
                <button id={'make-guess'} disabled>Guessing ...</button>
            </div>
        );
    };
    
    return (
        (complete) ?
        <div className='half-width'>
            <WordleGrid guesses={player.guesses} results={player.results} />
            <br/>
            <Payout/>
        </div> :
        <div className='half-width'>
            <div className='full-width'>
                <WordleGrid guesses={player.guesses} results={player.results} />
                <div className='separator'></div>
            </div>
            {
            (guessing) ?
                <MakingGuessState />:
                (Number(player.userGuessState)) ?
                <GettingResultState />:
                <div>
                    <RICIBs
                    amount={5}
                    autoFocus
                    handleOutputString={(guessString) => {
                        setGuess(guessString.toUpperCase());
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
                    <br/>
                    <button id={'make-guess'} onClick={() => makeGuess()}>Submit Guess</button>
                </div>
                
            }
        </div>
        
    )
}

export default Play;