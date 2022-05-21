const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
};

export class WordleContractInterface {
    constructor (web3, wordleContract, account) {
        this.web3 = web3;
        this.wordleContract = wordleContract;
        this.account = account;
    }

    signUp = async (signUpCost) => {
        const tx = await this.wordleContract.methods.signUp().send({value: signUpCost, from: this.account});
        console.log(tx);
        return tx;
    };

    getSignUpCost = async () => {
        const tx = await this.wordleContract.methods.lotSizeInWei().call({from: this.account});
        return tx;
    };


    makeGuess = async (guess) => {
        const tx = await this.wordleContract.methods.makeGuess(this.web3.utils.asciiToHex(guess.toUpperCase())).send({from: this.account});
        console.log('Make Guess Txn');
        console.log(tx);
        return tx;
    };

    pollGuessResult = async () => {
        let resultAvailable = 0;
        let result;

        while(!resultAvailable) {
            try {
                const tx1 = await this.getGuessResultCall();
                result = await this.getGuessResultSend().then(() => {
                    resultAvailable = 1;
                    window.location.reload(false);
                });
            } catch (e) {
                await sleep(10000);
                console.log(e);
            }
        }

        return result;
    }

    getPlayerState = async () => {
        const enabled = await this.wordleContract.methods.enabled(this.account).call();
        const solved = await this.wordleContract.methods.solved(this.account).call();
        const numberOfGuesses = await this.wordleContract.methods.numberOfGuesses(this.account).call();
        const userGuessState = await this.wordleContract.methods.guessState(this.account).call();
        const currGameState = await this.wordleContract.methods.currGameState().call();

        let guesses = [];
        let results = [];

        for(let i=0;i<=numberOfGuesses;i++){
            if(i!=Number(numberOfGuesses) || Number(userGuessState) === 1){
                const guess = await this.wordleContract.methods.userGuesses(this.account, i).call();
                guesses.push(this.web3.utils.hexToAscii(guess));
            }
        }

        for(let i=0;i<numberOfGuesses;i++){
            let result = [];
            for(let j=0;j<5;j++){
                const resultElement = await this.wordleContract.methods.guessStore(this.account, i, j).call();
                result.push(resultElement);
            }
            results.push(result);
        }

        let userObject = {
                enabled:enabled,
                solved:solved,
                numberOfGuesses: numberOfGuesses,
                userGuessState: Number(userGuessState),
                guesses:guesses,
                results:results,
                currGameState:currGameState
        }

        console.log(userObject);
        return userObject;


    }

    getGuessResultCall = async () => {
        const tx1 = await this.wordleContract.methods.getGuessResult().call({from: this.account});
        console.log('Get Result Dry Run');
        console.log(tx1);
        return tx1;
    };

    getGuessResultSend = async () => {
        const tx1 = await this.wordleContract.methods.getGuessResult().send({from: this.account});
        console.log('Get Result Reak Run');
        console.log(tx1);
        return tx1;
    };


    isSolved = async () => {
        const tx = await this.wordleContract.methods.solved(this.account).call({from: this.account});
        return tx;
    };

    getAccountBalance = async () => {
        const tx = await this.wordleContract.methods.getOutstandingBalance().call({from: this.account});
        return tx;
    };

    withdrawOutstandingBalance = async () => {
        const tx = await this.wordleContract.methods.receiveOutstandingBalance().send({from: this.account});
        return tx;
    };

}

export default WordleContractInterface;