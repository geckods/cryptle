import WordList from '../wordlist/Wordlist.json';

export const isValidGuess = (guess) => {
    if (WordList.words.includes(guess) && (guess.length === 5) && (/^[a-zA-Z]+$/.test(guess))) {
        return true;
    }
    return false;
};