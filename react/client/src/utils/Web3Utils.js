import map from "../artifacts/deployments/map.json"

export const accountsAvailable = (accounts) => {
    return accounts !== null && accounts !== undefined && accounts.length > 0;
}

export const loadContract = async (chain, contractName, web3) => {
    // Load a deployed contract instance into a web3 contract object
    // const {web3} = state

    // Get the address of the most recent deployment from the deployment map
    let address
    try {
        address = map[chain][contractName][0]
    } catch (e) {
        console.log(`Couldn't find any deployed contract "${contractName}" on the chain "${chain}".`)
        return undefined
    }

    // Load the artifact with the specified address
    let contractArtifact
    try {
        contractArtifact = await import(`./artifacts/deployments/${chain}/${address}.json`)
    } catch (e) {
        console.log(`Failed to load contract artifact "./artifacts/deployments/${chain}/${address}.json"`)
        return undefined
    }

    return new web3.eth.Contract(contractArtifact.abi, address)
};

export const getChainFromChainId = (chainId) => {
    switch (Number(chainId)) {
        case 1:
            return 'Ethereum';
        case 4:
            return 'Rinkeby';
        case 137:
            return 'Polygon';
        case 8001:
            return 'Polygon-Mumbai';
        case 43114:
            return 'Avalanche-C';
        case 43113:
            return 'Avalanche-Fuji';
        default:
            return 'Unknown';
    }
};
