import React, {useEffect, useContext, useState} from "react";
import { guessResultCharacterClass } from "../constants/Constants";
import AppContext from '../contexts/AppContext';
import LiveReward from "./LiveReward";
import LivePlayerCount from "./LivePlayerCount";


const WordleGridRow = (props) => {
    const context = useContext(AppContext);
    const wordleInterface = context.getWordleInterface();

    const { guess, result, id } = props;


    const [playerCount, setPlayerCount] = useState(0);
    const [currentPayout, setCurrentPayout] = useState(0.0);

    useEffect(() => {
        wordleInterface.getCurrentPayout(id+1).then((tx) => {
            setCurrentPayout(tx);
        });
        wordleInterface.getSolvedCountByGuesses(id+1).then((tx) => {
            setPlayerCount(tx);
        });

    },[])


    let classNames = [];
    for(let i=0; i<5; i++) {
        classNames.push(guessResultCharacterClass[(result != null) ? result[i] : 3])
    }

    if (guess) {
        return (
            <tr>
                <LivePlayerCount playerCount={Number(playerCount)}></LivePlayerCount>
                <td className={classNames[0]}>
                    {guess[0]}
                </td>
                <td className={classNames[1]}>
                    {guess[1]}
                </td>
                <td className={classNames[2]}>
                    {guess[2]}
                </td>
                <td className={classNames[3]}>
                    {guess[3]}
                </td>
                <td className={classNames[4]}>
                    {guess[4]}
                </td>
                <LiveReward reward={Number(currentPayout)}></LiveReward>
            </tr>
        )
    }

    return (
        <>
            <tr>
                <LivePlayerCount playerCount={Number(playerCount)}></LivePlayerCount>
                <td className="white-cell"></td>
                <td className="white-cell"></td>
                <td className="white-cell"></td>
                <td className="white-cell"></td>
                <td className="white-cell"></td>
                <LiveReward reward={Number(currentPayout)}></LiveReward>
            </tr>
        </>
    )
};

export default WordleGridRow;