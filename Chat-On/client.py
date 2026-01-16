import socket
import threading
import json
import os
import ssl
import struct
import base64
import random

# Global variables
nickname = ""
password = ""
client = None
stop_thread = False

def send_json(sock, data):
    """Helper to send JSON data with length prefix"""
    try:
        json_data = json.dumps(data)
        encoded_data = json_data.encode('utf-8')
        sock.sendall(struct.pack('>I', len(encoded_data)) + encoded_data)
    except Exception as e:
        print(f"Error sending JSON: {e}")

def recv_json(sock):
    """Helper to receive JSON data with length prefix"""
    try:
        raw_len = sock.recv(4)
        if not raw_len:
            return None
        msg_len = struct.unpack('>I', raw_len)[0]
        
        data = b''
        while len(data) < msg_len:
            packet = sock.recv(msg_len - len(data))
            if not packet:
                return None
            data += packet
            
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        return None

def enter_server():
    os.system('cls||clear')
    with open('servers.json') as f:
        data = json.load(f)
    print('Your servers: ', end="")
    for servers in data:
        print(servers, end=" ")
    
    server_name = input("\nEnter the server name: ")
    global nickname
    global password
    
    nickname = input("Choose Your Nickname (Leave blank for Anonymous): ").strip()
    
    if not nickname:
        nickname = f"Anon#{random.randint(1000, 9999)}"
        print(f"Assigned Anonymous Nickname: {nickname}")
    
    if nickname == 'admin':
        password = input("Enter Password for Admin: ")

    ip = data[server_name]["ip"]
    port = data[server_name]["port"]
    
    global client
    # Create a raw socket
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Wrap with SSL
    # context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    # context.check_hostname = False
    # context.verify_mode = ssl.CERT_NONE
    
    # We use a custom context to ignore self-signed cert warnings for this demo
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE # DANGEROUS in prod, okay for self-signed local demo

    try:
        client = context.wrap_socket(raw_socket, server_hostname=ip)
        client.connect((ip, port))
    except Exception as e:
        print(f"Could not connect to secure server: {e}")
        return

def add_server():
    os.system('cls||clear')
    server_name = input("Enter a name for the server:")
    server_ip = input("Enter the ip address of the server:")
    server_port = int(input("Enter the port number of the server:"))

    with open('servers.json', 'r') as f:
        data = json.load(f)
    with open('servers.json', 'w') as f:
        data[server_name] = {"ip": server_ip, "port": server_port}
        json.dump(data, f, indent=4)

while True:
    os.system('cls||clear')
    option = input("(1)Enter server\n(2)Add server\n")
    if option == '1':
        enter_server()
        if client: # If connection successful
            break
    elif option == '2':
        add_server()

def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            msg_obj = recv_json(client)
            if not msg_obj:
                print("Disconnected from server.")
                client.close()
                stop_thread = True
                break
                
            msg_type = msg_obj.get('type')
            content = msg_obj.get('content')
            
            if msg_type == 'request':
                if content == 'NICK':
                    send_json(client, {"type": "resp", "content": nickname})
                elif content == 'PASS':
                    send_json(client, {"type": "resp", "content": password})
                    
            elif msg_type == 'error':
                print(f"Error: {content}")
                if content in ['BAN', 'REFUSE']:
                    client.close()
                    stop_thread = True
                    
            elif msg_type == 'msg':
                print(content)
                
            elif msg_type == 'file':
                sender = msg_obj.get('sender')
                filename = msg_obj.get('filename')
                file_data_b64 = msg_obj.get('data')
                
                print(f"Receiving file '{filename}' from {sender}...")
                
                # Create downloads folder
                if not os.path.exists('downloads'):
                    os.makedirs('downloads')
                    
                path = os.path.join('downloads', f"received_{filename}")
                
                with open(path, "wb") as f:
                    f.write(base64.b64decode(file_data_b64))
                    
                print(f"File saved to {path}")

        except Exception as e:
            print(f'Error Occured: {e}')
            client.close()
            break

def write():
    global stop_thread
    while True:
        if stop_thread:
            break
            
        try:
            user_input = input("")
            
            # File transfer
            if user_input.startswith('/send '):
                filepath = user_input[6:].strip()
                if os.path.exists(filepath):
                    filename = os.path.basename(filepath)
                    with open(filepath, "rb") as f:
                        file_content = base64.b64encode(f.read()).decode('utf-8')
                    
                    send_json(client, {
                        "type": "file",
                        "filename": filename,
                        "data": file_content
                    })
                    print(f"Sending {filename}...")
                else:
                    print("File not found!")
                    
            # Admin Legacy Commands
            elif user_input.startswith('/kick') or user_input.startswith('/ban'):
                 if nickname == 'admin':
                     send_json(client, {"type": "msg", "content": user_input})
                 else:
                     print("Commands can be executed by Admins only !!")
            
            # Normal Message
            else:
                send_json(client, {"type": "msg", "content": user_input})
                
        except Exception:
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

