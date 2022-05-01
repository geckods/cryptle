export const isValidGuess = (guess) => {
    if (guess.length !== 5) {
        return false;
    }
    if(/^[a-zA-Z]+$/.test(guess)) {
        return true;
    }
    return false;
};