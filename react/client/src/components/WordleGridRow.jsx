import React from "react";
import { guessResultCharacterClass } from "../constants/Constants";

const WordleGridRow = (props) => {
    const { guess, result, id } = props;
    console.log('ROW: ' + id + ' Guess: ' + guess);
    console.log('ROW: ' + id + ' Result: ' + result);

    if (guess) {
        return (
            <tr>
                <td className={guessResultCharacterClass[result ? result[0]:3]}>
                    {guess[0]}
                </td>
                <td className={guessResultCharacterClass[result ? result[1]:3]}>
                    {guess[1]}
                </td>
                <td className={guessResultCharacterClass[result ? result[2]:3]}>
                    {guess[2]}
                </td>
                <td className={guessResultCharacterClass[result ? result[3]:3]}>
                    {guess[3]}
                </td>
                <td className={guessResultCharacterClass[result ? result[4]:3]}>
                    {guess[4]}
                </td>
            </tr>
        )
    }

    return (
        <tr>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>
    )
};

export default WordleGridRow;