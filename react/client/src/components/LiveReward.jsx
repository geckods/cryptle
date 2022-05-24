import React from "react";

const LiveReward = (props) => {
    const {reward} = props;

    const abc = (reward/(1e18)).toFixed(2);

    return (
        <>
            <td id = "live_reward" className={(abc>1.0)?"green-payout-cell":"red-payout-cell"}>{abc}</td>
        </>
    )
}

export default LiveReward;