# Image-Translator

## IoT Api gateway

Before running the project an IoT gateway needs to be created. The gateway is used to captured the state of the broker nodes and allows you to visualise the state of the network.

The repo containing the code used to deploy the IoT gateway can be found at [trozler/image_translator_iotgateway](https://github.com/trozler/image_translator_iotgateway).

**Then run the project in the following way:**

```

git clone https://github.com/trozler/image_translator_iotgateway
cd image_translator_iotgateway
npm i
npm run build
cdk synth
cdk diff
cdk deploy

```

This will return a url similar to:

```
https://c02zu014q2.execute-api.eu-central-1.amazonaws.com/prod/message/
```

When you run the framework on each VM, please update the url in `Image-Translator/src/config.py`.

## How to run using EC2 instances

1. Launch an EC2 instance in the same region us-east-1.

2. Configure the security group of the EC2, add rules under Inbound like this
   2.1) All TCP 0-65535 0.0.0.0
   2.2) All UDP 0-65535 0.0.0.0
   3.) Assign an Elastic IP for your EC2. Found in the left tab on the EC2 Dashboard.
   4.) Do ssh-keygen on ec2-server and ping me the ssh keys.

3. Run program as followed
   a) Run `git clone https://github.com/shivesh-ganju/Image-Translator.git` on each VM.
   b) Install dependencies by running `pip install -r requirements.txt` on each VM.
   c) Run the nodes in this order:

   ```
   // VM1
   python3 registration_server.py  // Front end.
   python3 node_register_server.py // Back end.

   // VM2
   python3 node_interface.py       // Back end.
   /* Also start interface front end see below. */

   // VM3
   python3 node_broker.py
   /* Need to also deploy IoT gateway see below. */

   // VM4
   python3 node_transcription.py

   // VM5
   python3 node-it.py

   // VM6
   python3 node-gr.py

   // VM7
   python3 node-fr.py

   // VM8
   python3 node-es.py
   ```

4. Interact with application - User flow:
   a) Send a GET request to registration server front end. You will know this IP.

   ```
   curl http://<ip of registration_server VM>:8080/interface-node

   ////////////////////////////////
   {
      "nodes": [
          "192.168.1.35:1119"
      ]
   }
   ////////////////////////////////
   ```

   b) Open up returned URL in browser and interact with application.

## Interface node additional required steps to run

If you want to run an `interface node` you also have to install the following repo:

```

git clone https://github.com/trozler/interface_nodes_btpeer.git
cd interface_nodes_btpeer
npm i
npm run build
node app.js

```

For more information on the web server, which uses Ethereum for payments, please refer to [trozler/interface_nodes_btpeer](https://github.com/trozler/interface_nodes_btpeer.git).
