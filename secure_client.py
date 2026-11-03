import socket
import ssl

HOST = '127.0.0.1'
PORT = 8443

#Clientside SSL Context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
#The cool stuff. We add the certificate here so that server can verify it
context.load_verify_locations(cafile="server.crt")
    
#Required when using 'localhost' or '127.0.0.1' with self-signed certs. I don't know why this does not work without this, but well.
context.check_hostname = False 

#We do connect and wrap at the same time here
raw_socket = socket.create_connection((HOST, PORT))
with context.wrap_socket(raw_socket, server_hostname=HOST) as secure_socket:
    print("[+] Connected securely to the server.")
    print("Type /quit to disconnect.")
        
    while True:
        message = input("Enter message: ")

        # Check whether the user wants to quit
        if message.strip().lower() == "/quit":
            print("Disconnecting from server...")
            break

        # Send message to server
        secure_socket.sendall(message.encode("utf-8"))

        # Receive server response
        data = secure_socket.recv(1024)

        if not data:
            print("Server disconnected.")
            break

        print("Server replied:", data.decode("utf-8"))

print("Client stopped.")

