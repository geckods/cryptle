import React from "react";
import { guessResultCharacterClass } from "../constants/Constants";

const WordleGridRow = (props) => {
    const { guess, result, id } = props;
    console.log('ROW: ' + id + ' Guess: ' + guess);
    console.log('ROW: ' + id + ' Result: ' + result);

    let classNames = [];

    for(let i=0; i<5; i++) {
        classNames.push(guessResultCharacterClass[(result !== null) ? result[i] : 3])
    }
    console.log(classNames);

    if (guess) {
        return (
            <tr>
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
            </tr>
        )
    }

    return (
        <tr>
            <td className="white-cell"></td>
            <td className="white-cell"></td>
            <td className="white-cell"></td>
            <td className="white-cell"></td>
            <td className="white-cell"></td>
        </tr>
    )
};

export default WordleGridRow;