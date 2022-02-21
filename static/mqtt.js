    // Generate a random client ID
    clientID = "clientID-" + parseInt(Math.random() * 100);

    // Fetch the hostname/IP address and port number from the form
    host = "192.168.1.2"
    port = "9001"

    // Initialize new Paho client connection
    client = new Paho.MQTT.Client(host, Number(port), clientID);

    // Set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // Connect the client, if successful, call onConnect function
    client.connect({ onSuccess: onConnect, });

// Called when the client connects
function onConnect() {
    // Subscribe to the requested topic
    client.subscribe("house/#");
}

// Called when the client loses its connection
function onConnectionLost(responseObject) {
	    client.connect({ onSuccess: onConnect, });
}


// Called when a message arrives
function onMessageArrived(message) {
    //console.log("onMessageArrived:"+message.destinationName + message.payloadString);

    if (message.destinationName == "house/indoor/sensor/temperature") {
        document.getElementById("insidenow").innerHTML = message.payloadString + "&deg;";
    }

    if (message.destinationName == "house/outside/sensor/temperature") {
        document.getElementById("outsidenow").innerHTML = message.payloadString.split(".")[0] + "&deg;";
    }

    if (message.destinationName == "house/sensor/power") {
        document.getElementById("current_power").innerHTML = message.payloadString.split(":")[0];
    }

    if (message.destinationName == "house/money/otherbalance") {
        document.getElementById("bankbalance").innerHTML = message.payloadString.split(".")[0];
    }

    if (message.destinationName == "house/money/homeloanbalance") {
        document.getElementById("homeloanbalance").innerHTML = message.payloadString.split(".")[0];
    }
}

 
function startDisconnect() {
    client.disconnect();
}
