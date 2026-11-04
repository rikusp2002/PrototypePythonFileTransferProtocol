# Prototype File Transfer Protocol

This was done as an assignment to an introductory programming lab I am enrolled in currently as a student.

You will see two pairs of files as part of the repository except this README: `filetransferclient.py` and `filetransferserver.py` being one pair, the other two python scripts forming the other pair. The latter pair is a simple echo server, which I was tasked to implement TLS sockets on, and the former pair is a file transfer system I was tasked to create.

The file transfer system is very primitive - both server and clients get their own directory. When a client uploads a file to the server, it gets placed in the server directory and now every client can see the uploaded files.

But to run this file you'll need to set up a self-signed certificate first. 

## Creating a self-signed certificate from scratch

You can follow any guide you like for this, especially if you are not a beginner I'd presume you already know how to do so. But, feel free to follow this process if you wish.

Choose your favourite cryptosystem. I have used the widely used protocol **ED-25519**. I've done this on a Linux machine running CachyOS, and the most major Linux distributions will have the exact same steps for one to do so. If you are using Windows, I'll update on that later as I need to learn it myself.

First clone this repository somewhere you like, and enter it.

```sh
git clone https://github.com/rikusp2002/PrototypePythonFileTransferProtocol.git
cd PrototypePythonFileTransferProtocol
```

We now generate a private key with our favourite cryptosystem. I'll be using the OpenSSL package.

```sh
openssl genpkey -algorithm ED25519 > server.key
```
You now have your super shiny key file. if you ever leak it, don't encrypt something with this ever again. 

Now, we need to prepare a configuration file for openssl to follow. I'll give a template for the one I used:
```conf
[ref]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no
[req_distinguished_name]
C = <Put your country of choice in two letter code in block letters>
CN = localhost
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
```

Save it to some name you like, with the extension `.cnf`. Now we are ready to create our certificate signing request.

```sh
openssl req -new -out server.csr -key server.key -config <name of your config file you just saved>.cnf
```
We finally reach the step you were waiting for:

```sh
openssl x509 -req -days <number of days you want it to be valid in integer> -in server.csr -signkey server.key -out server.crt 
```

Now you can run the server-client pairs in different terminal windows to see them in action.

If you wish to name your key, signing request and certificate something more creative, please do not forget to change the entries with your cool name:

### For server files (`filetransferserver.py` and `secure_server.py`)
```py
context.load_cert_chain(certfile="<your cool name for certificate file>.crt", keyfile="<your cool name for key file>.key")
```
### For client files (`filetransferclient.py` and `secure_client.py`)
```py
context.load_verify_locations(cafile="<your cool name for certificate file>.crt")
```
