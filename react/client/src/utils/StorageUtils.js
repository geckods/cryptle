export const save = (guess, result, account) => {
    let player = localStorage.getItem(account);
    if (player) {
        player = JSON.parse(player);
        player.guesses.push(guess);
        player.results.push(result);
    } else {
        player = {
            guesses: [],
            results: []
        };
    }
    localStorage.setItem(account, JSON.stringify(player));
};

export const getValues = (key) => {
    let vals = localStorage.getItem(key);
    if (vals) {
        return JSON.stringify(vals);
    }
    return [];
};