## P2P node types and message types

The Image translator service is built on a peer to peer architecture, where each node provides a specific service.

**In total we have 5 different node types.**

### Registration node

The registration node has two functions:

1. It is the node where all other nodes register themselves.
2. It is also acts as the gateway for users into the p2p network, by returning the IP of an _Interface node_ on a curl request.

The IP of the registration server is always known. If the registration server goes offline, then in theory another node will create a registration server. This provides some element of fault tolerance.

### Interface node

Interface nodes are the nodes users interact with. The IP of an interface node can be found by querying the registration server. Each interface node will run a small web server (port 3000) that will serve HTML and JS allowing the user to upload their (picture, email, region) and pays using meta mask.

For more information on the web server check out [trozler/interface_nodes_btpeer](https://github.com/trozler/interface_nodes_btpeer.git).

Additionally each interface node will run their btpeer implementation in a second process on port 1119.

_Message types:_

- The web server (port 3000) will send an "INIT" message to the p2p node running on port 1119 when a user has successfully paid and uploaded (picture, email, region).

- The p2p interface node process will then send a (BINT) tasks to broker nodes, initiating the transcription message.

### Broker node

Broker nodes will publish messages from Interface and Transcription nodes.

They will also send messages to Transcription and Translation nodes.

Example flow:

1. If an Interface node publishes a message, the broker will add the message to the queue and send it to a Transcription node

   - Receiving message type will be _"BINT"_ in BTPeer.
   - Send a message out using _"TRSC"_.

2. If a Transcription node publishes a message, the broker will add it to the queue and send it to a Translation node.

   - Receiving message type will be _“BTCR”_ in BTPeer.
   - Send a message out using _"TRAN"_.

3. If a broker node wants to leave the network the queue needs to be propagated to another broker node.
   - Everytime the state of the broker queue changes it will call an API provided by AWS API gateway. This API will be used to visualize the message flow and satisfy the IoT requirement.

### Transcription node

1. All Transcription nodes will listen to messages from all broker nodes.
   - Receiving message type from broker node is _TRSC_.

### Translation node

1. All Translation nodes will listen to messages from all broker nodes.
   - Will also send email to users containing final results.
   - Receiving message type from broker node is _“TRAN”_.
