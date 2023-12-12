// Create websocket
const serverSocket = new WebSocket('ws://' + window.location.host + '/ws/servers/');

// Get all server PKs
document.addEventListener("DOMContentLoaded", (event) => {
    const srvPkElements = Array.from(document.querySelectorAll('[data-serverpk]'));
    const srvPkArray = [];
    for (let index = 0; index < srvPkElements.length; ++index) {
        console.log(srvPkElements[index].dataset.serverpk);
        srvPkArray.push(srvPkElements[index].dataset.serverpk);
    }
    console.log(srvPkArray);
});
