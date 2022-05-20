import React from "react";
import WordleGridRow from "./WordleGridRow";

const WordleGrid = (props) => {
    const { guesses, results } = props;

    const keys = [0, 1, 2, 3, 4, 5];

    return (
        <table>
            <tbody>
                {
                    keys.map((key) => {
                        if (key < guesses.length) {
                            return (
                                <WordleGridRow
                                    key={key}
                                    id={key} 
                                    guess={guesses[key]}
                                    result={results[key]}
                                />
                            )
                        }
                        return (
                            <WordleGridRow 
                                key={key}
                                id={key}
                                guess={null}
                                result={null}
                            />
                        )
                    })
                }
            </tbody>
        </table>
    )
};

export default WordleGrid;