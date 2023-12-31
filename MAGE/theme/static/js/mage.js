// Get root URL
const rootUrl = window.location.host;

// Create websocket
const serverSocket = new WebSocket('ws://' + rootUrl + '/ws/servers/');
let serverRefreshTimer = 30;


function setRefreshTimer(totalSecs){
    let setRefreshTimer = setInterval(function() {
        if (serverRefreshTimer <= 0) {
            clearInterval(setRefreshTimer);
        }
        let barPercentage = Math.round((100 * serverRefreshTimer) / totalSecs);
        document.getElementById('refreshtimer').innerHTML = "Refreshing data in " + serverRefreshTimer.toString() + "s";
        document.getElementById('refreshprogress').style.width = barPercentage + '%';
        serverRefreshTimer -= 1;
    }, 900);
}

serverSocket.onopen = function(event) {
    setRefreshTimer(serverRefreshTimer);
}

serverSocket.onmessage = function (event) {
    // Get all server elements and the respective PKs.
    const srvPkElements = document.querySelectorAll('[data-serverpk]');
    const receivedData = JSON.parse(event.data);
    const serverData = receivedData.server_data;
    const refreshTimer = receivedData.refresh_timer;
    for (let index = 0; index < srvPkElements.length; ++index) {
        let serverPk = srvPkElements[index].dataset.serverpk;
        let serverInfo = serverData[serverPk].server_info
        srvPkElements[index].querySelector("#mapimg").src = '/static/' + serverInfo.mapimg;
        srvPkElements[index].querySelector("#mapname").innerHTML = serverInfo.mapname;
        srvPkElements[index].querySelector("#maptitle").innerHTML = "<strong>Map title: </strong>" + serverInfo.maptitle;
        srvPkElements[index].querySelector("#gametype").innerHTML = "<strong>Game type: </strong>" + serverInfo.gametype;
        srvPkElements[index].querySelector("#players").innerHTML = "<strong>Players: </strong>" + serverInfo.numplayers + " / " + serverInfo.maxplayers;
        srvPkElements[index].querySelector("#host").innerHTML = "<strong>Host: </strong>" + serverData[serverPk].server_host + ":" + serverData[serverPk].server_port;
        srvPkElements[index].querySelector("#statuscontainer").classList.remove("server_online_container", "server_offline_container", "server_polling_container");
        srvPkElements[index].querySelector("#statuscontainer").classList.add(serverInfo.status + "_container");
        srvPkElements[index].querySelector("#statusindicator").classList.remove("server_online", "server_offline", "server_polling");
        srvPkElements[index].querySelector("#statusindicator").classList.add(serverInfo.status);
        srvPkElements[index].querySelector("#serverstatus").innerHTML = serverInfo.status_verbose;
    }
    serverRefreshTimer = refreshTimer;
    setRefreshTimer(refreshTimer);
}

serverSocket.onclose = function (event) {
    console.log("Socket closed: ", event);
}