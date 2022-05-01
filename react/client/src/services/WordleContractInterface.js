export class WordleContractInterface {
    constructor (wordleContract, account) {
        this.wordleContract = wordleContract;
        this.account = account;
    }

    signUp = () => {
        this.wordleContract.methods.signUp().send({value: 1000000000000000000, from: this.account}).then((tx) => {
            console.log(tx);
        }).catch((e) => {
            console.log('error');
            console.log(e);
        });
    };

    makeGuess = async (guess) => {
        const tx = await this.wordleContract.methods.makeGuess(guess.toUpperCase()).send({from: this.account});
        console.log('Make Guess Txn');
        console.log(tx);
        const tx1 = await this.getGuessResult();

        return tx1;
    };

    getGuessResult = async () => {
        const tx1 = await this.wordleContract.methods.getGuessResult().call({from: this.account});
        console.log('Get Result Dry Run');
        console.log(tx1);

        // const tx2 = await this.wordleContract.methods.getGuessResult().send({from: this.account});
        // console.log('Get Result Actual');
        // console.log(tx2);
        return tx1;
    }
}

export default WordleContractInterface;