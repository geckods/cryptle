import React, { useEffect, useState } from "react";
import { guessResultCharacterClass } from "../constants/Constants";

function shuffle(array) {
    console.log('Shuffling');
    let currentIndex = array.length,  randomIndex;
  
    // While there remain elements to shuffle.
    while (currentIndex != 0) {
  
      // Pick a remaining element.
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
  
      // And swap it with the current element.
      [array[currentIndex], array[randomIndex]] = [
        array[randomIndex], array[currentIndex]];
    }
    console.log(array);
    return array;
  }

const CryptleLogo = () => {

    const [colors, setColors] = useState([0,1,0,0,0,2,2]);

    useEffect(() => {
        console.log('UseEffect');
        // setInterval(() => {
        //     console.log('Hello');
        //     setColors(shuffle(colors));
        // }, 1000);
    }, [])

    return (
        <table id={'cryptle-logo-container'}>
            <tbody>
                <tr>
                    <td className={guessResultCharacterClass[colors[0]]}>C</td>
                    <td className={guessResultCharacterClass[colors[1]]}>R</td>
                    <td className={guessResultCharacterClass[colors[2]]}>Y</td>
                    <td className={guessResultCharacterClass[colors[3]]}>P</td>
                    <td className={guessResultCharacterClass[colors[4]]}>T</td>
                    <td className={guessResultCharacterClass[colors[5]]}>L</td>
                    <td className={guessResultCharacterClass[colors[6]]}>E</td>
                </tr>
            </tbody>
        </table>
    )
};

export default CryptleLogo;