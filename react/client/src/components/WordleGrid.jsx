import React from "react";
import WordleGridRow from "./WordleGridRow";

const WordleGrid = () => {
    return (
        <table>
            <tbody>
                <WordleGridRow />
                <WordleGridRow />
                <WordleGridRow />
                <WordleGridRow />
                <WordleGridRow />
                <WordleGridRow />
            </tbody>
        </table>
    )
};

export default WordleGrid;