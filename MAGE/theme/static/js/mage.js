// Create websocket
const serverSocket = new WebSocket('ws://' + window.location.host + '/ws/servers/');

// Get all server PKs
document.addEventListener("DOMContentLoaded", (event) => {
    const srvPkElements = Array.from(document.querySelectorAll('[data-serverpk]'));
    const srvPkArray = [];
    for (let index = 0; index < srvPkElements.length; ++index) {
        // Push all server PKs to an array
        srvPkArray.push(srvPkElements[index].dataset.serverpk);
    }
    console.log(srvPkArray);
});
