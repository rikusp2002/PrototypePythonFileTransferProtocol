import os
import socket
import ssl

HOST = '127.0.0.1'
PORT = 8443

#We want so that client folders are different for each so that it feels like the real thing 
client_name = input("Enter client folder name (e.g., client_1): ").strip()
client_dir = os.path.join("./client_dirs", client_name)
os.makedirs(client_dir, exist_ok=True)
    
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#I still don't know why do we need this but I'm not really sure rn I will check this later
context.check_hostname = False
context.load_verify_locations(cafile="server.crt")
#Lol forgot to put certificate at first so it showed a certificate error. This works now.    
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure_socket = context.wrap_socket(raw_socket, server_hostname=HOST)
    
try:
    secure_socket.connect((HOST, PORT))
    print(f"[+] Connected securely to server. Active directory: {client_dir}\n")
        
    while True:
        print("Commands: LIST, UPLOAD <filename>, DOWNLOAD <filename>, EXIT")
        choice = input("Enter command: ").strip()
        if not choice:
            continue
            
        parts = choice.split(' ', 1)
        command = parts[0].upper()
            
        if command == 'LIST':
            secure_socket.sendall(b"LIST")
            response = secure_socket.recv(4096).decode('utf-8')
            print(f"\n--- Server Files ---\n{response}\n--------------------\n")
                
        elif command == 'UPLOAD':
            if len(parts) < 2:
                print("Usage: UPLOAD <filename>")
                continue
            filename = parts[1]
            local_path = os.path.join(client_dir, filename)
                
            if not os.path.exists(local_path):
                print(f"File not found in local directory: {local_path}")
                continue
                
            secure_socket.sendall(f"UPLOAD {filename}".encode('utf-8'))
            if secure_socket.recv(1024) == b"READY":
                file_size = os.path.getsize(local_path)
                secure_socket.sendall(str(file_size).encode('utf-8'))
                    
                if secure_socket.recv(1024) == b"ACK":
                    with open(local_path, 'rb') as f:
                        secure_socket.sendall(f.read())
                        
                    if secure_socket.recv(1024) == b"SUCCESS":
                        print(f"<- Successfully uploaded {filename} to server.")
                            
        elif command == 'DOWNLOAD':
            if len(parts) < 2:
                print("Usage: DOWNLOAD <filename>")
                continue
            filename = parts[1]
            local_path = os.path.join(client_dir, filename)
                
            secure_socket.sendall(f"DOWNLOAD {filename}".encode('utf-8'))
            response = secure_socket.recv(1024)
                
            if response == b"FOUND":
                secure_socket.sendall(b"READY")
                file_size = int(secure_socket.recv(1024).decode('utf-8'))
                secure_socket.sendall(b"ACK")
                    
                with open(local_path, 'wb') as f:
                    remaining = file_size
                    while remaining > 0:
                        chunk = secure_socket.recv(min(remaining, 4096))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                print(f"-> Downloaded {filename} into {local_path}")
            else:
                print("[X] File not found on the server.")
                    
        elif command == 'EXIT':
            secure_socket.sendall(b"EXIT")
            break
        else:
            print("Invalid command.")
                
except Exception as e:
    print(f"Error: {e}")
finally:
    secure_socket.close()
    print("Disconnected from server.")


