import os
import socket
import ssl
import threading

HOST = '127.0.0.1'
PORT = 8443
SERVER_DIR = './server_dir'

#Create the directory if it does not exist. I have already created this folder on my system but this allows for better testing in a different device.
os.makedirs(SERVER_DIR, exist_ok=True)

def handle_client(conn, addr): #This work is a little bit complicated so I'll just create a function for this entire thing
    print(f"[+] Secure connection established from {addr}")
    try:
        while True:
            #I'll let the clients do basic commands as list, upload, download and exit. This recieves the command.
            request = conn.recv(1024).decode('utf-8').strip()
            if not request: #if we fail somehow, we end the server.
                break
            
            parts = request.split(' ', 1) #We use string splicing to actually process the command.
            command = parts[0].upper() #The listed command should be at the start, and we convert it to uppercase. Lowercase also works.
            
            if command == 'LIST':
                #This part handles listing the files in the server.
                files = os.listdir(SERVER_DIR)
                conn.sendall(("\n".join(files) if files else "Server directory is empty.").encode('utf-8')) #I love python one liners
                
            elif command == 'UPLOAD': #This part handles uploading.
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)
                conn.sendall(b"READY") #This is a flag which tells the client that the server is ready to upload.
                
                #We first determine what is the file size. If you are not sure, just write 4096 as that is the hardcoded limit for this transfer system anyways.
                file_size = int(conn.recv(1024).decode('utf-8'))
                conn.sendall(b"ACK") #this tells the server has recieved the filesize.
                
                #We now process the file
                with open(filepath, 'wb') as f:
                    remaining = file_size
                    while remaining > 0:
                        chunk = conn.recv(min(remaining, 4096))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                print(f"->Uploaded: {filename} from {addr}")
                conn.sendall(b"SUCCESS") #Same, the flag for success

            elif command == 'DOWNLOAD': #this part handles the download
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)
                
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    conn.sendall(b"FOUND") #This tells teh client that it has found the file requested.
                    # Wait for client readiness
                    if conn.recv(1024) == b"READY":
                        file_size = os.path.getsize(filepath)
                        conn.sendall(str(file_size).encode('utf-8'))
                        
                        # Wait for client acknowledgment
                        if conn.recv(1024) == b"ACK":
                            with open(filepath, 'rb') as f:
                                conn.sendall(f.read())
                            print(f"<- Downloaded: {filename} by {addr}")
                else:
                    conn.sendall(b"NOT_FOUND")
                    
            elif command == 'EXIT':
                break
    except Exception as e:
        print(f"[-] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Connection closed from {addr}")


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    
bind_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
bind_socket.bind((HOST, PORT))
bind_socket.listen()
    

secure_socket = context.wrap_socket(bind_socket, server_side=True)
print(f"[*] Secure Server listening on {HOST}:{PORT}. Use KeyboardInterrupt (Ctrl+C) to close the server.")
    
try:
    while True:
        conn, addr = secure_socket.accept()
        #This is where we do the multi-threading
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()
except KeyboardInterrupt:
    print("\n[*] Server shutting down.")
finally:
    secure_socket.close()


