import socket
import ssl

HOST = '127.0.0.1'
PORT = 8443


#Create a secure SSL context for the server side, this is necessary
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
#Here we load the generated certificate and private key using our favourite cryptosystem!
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

#This was same as before, creating the socket
bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
bind_socket.bind((HOST, PORT))
bind_socket.listen()
    
print(f"[*] Secure Echo Server listening on {HOST}:{PORT}...")

#We now wrap the socket with our SSL context
with context.wrap_socket(bind_socket, server_side=True) as tls_server:
    while True:
        try:
            #Try accepting the encrypted traffic. This fails if there is a certificate failure.
            client_socket, addr = tls_server.accept()
            print(f"[+] Secure connection established from {addr}")
                
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    print(f"[Received]: {data.decode('utf-8')}")
                    #The classic echo is here
                    client_socket.sendall(data)
                        
            print(f"[-] Connection closed with {addr}")
        except Exception as e:
            print(f"[!] Error: {e}")


