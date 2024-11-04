const roomName = "example_room";  // Replace this with the actual room name
const socket = new WebSocket(`ws://${window.location.host}/ws/game/${roomName}/`);

socket.onopen = function(event) {
    console.log("WebSocket connection established:", event);
};

socket.onmessage = function(event) {
    console.log("Message from server:", event.data);
};

socket.onclose = function(event) {
    console.log("WebSocket connection closed:", event);
};
