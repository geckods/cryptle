export class WordleContractInterface {
    constructor (web3, wordleContract, account) {
        this.web3 = web3;
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
    };

    isSolved = async () => {
        const tx = await this.wordleContract.methods.solved(this.account).call({from: this.account});
        return tx;
    };

    withdrawFunds = async () => {
        const tx = await this.wordleContract.methods.pastGamePaymentSplitters().call({from: this.account});
        if (tx && tx.length > 0) {
            const paymentSplitterAddress = tx[tx.length-1];
            
            let contractArtifact
            try {
                contractArtifact = await import(`../artifacts/contracts/dependencies/OpenZeppelin/openzeppelin-contracts@4.5.0/PaymentSplitter.json`);
            } catch (e) {
                console.log(`Failed to load payment splitter contract artifact`);
                return 0
            }

            const paymetSplitter = new this.web3.eth.Contract(contractArtifact.abi, paymentSplitterAddress);
            const tx = await paymetSplitter.methods.release(this.account).send({from: this.account});
            if (tx) {
                return 1;
            }
            return 0;
        } else {
            return 0;
        }
    };
}

export default WordleContractInterface;