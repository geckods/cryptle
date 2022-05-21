import map from "../artifacts/deployments/map.json"

export const accountsAvailable = (accounts) => {
    return accounts !== null && accounts !== undefined && accounts.length > 0;
}


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

export const getContractAddressFromChainId = (chainId) => {
    switch (Number(chainId)) {
        case 43113:
            return '0x5e0f37aeAaBEB5107D2cea09a04cfB3ea8eE1761';
        default:
            return 'NOT LIVE';
    }
}
