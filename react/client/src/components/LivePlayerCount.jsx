import React from "react";

const LivePlayerCount = (props) => {
    const {playerCount} = props;

    return (
        <>
            <td id = "player_count">{playerCount}</td>
        </>
    )
}

export default LivePlayerCount;