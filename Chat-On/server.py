import threading
import socket
import ssl
import json
import struct

host = "127.0.0.1"
port = 5555  

# SSL Context Setup
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, 5555))
server.listen()

clients = []
nicknames = []

def send_json(sock, data):
    """Helper to send JSON data with length prefix"""
    try:
        json_data = json.dumps(data)
        encoded_data = json_data.encode('utf-8')
        # Send 4 bytes length + data
        sock.sendall(struct.pack('>I', len(encoded_data)) + encoded_data)
    except Exception as e:
        print(f"Error sending JSON: {e}")

def recv_json(sock):
    """Helper to receive JSON data with length prefix"""
    try:
        # Read 4 bytes for length
        raw_len = sock.recv(4)
        if not raw_len:
            return None
        msg_len = struct.unpack('>I', raw_len)[0]
        
        # Read the message data
        data = b''
        while len(data) < msg_len:
            packet = sock.recv(msg_len - len(data))
            if not packet:
                return None
            data += packet
            
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Error receiving JSON: {e}")
        return None

def broadcast(data, exclude_client=None):
    """Broadcasts a dictionary object as JSON to all clients"""
    for client in clients:
        if client != exclude_client:
            send_json(client, data)

def handle(client):
    while True:
        try:
            msg_obj = recv_json(client)
            if not msg_obj:
                raise Exception("Client disconnected")

            msg_type = msg_obj.get('type')
            
            if msg_type == 'msg':
                content = msg_obj.get('content')
                sender = nicknames[clients.index(client)]
                
                # Admin Commands (legacy logic adapted)
                if content.startswith('KICK') and sender == 'admin':
                    name_to_kick = content[5:]
                    kick_user(name_to_kick)
                elif content.startswith('BAN') and sender == 'admin':
                    name_to_ban = content[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned by the Admin!')
                else:
                    broadcast({
                        "type": "msg",
                        "content": f"{sender}: {content}"
                    })
                    
            elif msg_type == 'file':
                sender = nicknames[clients.index(client)]
                filename = msg_obj.get('filename')
                file_data = msg_obj.get('data') # Base64 encoded string
                
                print(f"File received from {sender}: {filename}")
                
                # Broadcast file to others
                broadcast({
                    "type": "file",
                    "sender": sender,
                    "filename": filename,
                    "data": file_data
                }, exclude_client=client)

        except Exception as e:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast({"type": "msg", "content": f'{nickname} left the Chat!'})
                nicknames.remove(nickname)
                break

def receive():
    print("Secure Server Listening...")
    while True:
        raw_socket, address = server.accept()
        print(f"Connected with {str(address)}")
        
        # Wrap socket with SSL
        try:
            client = context.wrap_socket(raw_socket, server_side=True)
        except ssl.SSLError as e:
            print(f"SSL Error: {e}")
            continue

        # Handshake protocol
        send_json(client, {"type": "request", "content": "NICK"})
        
        # Expect Nickname
        resp = recv_json(client)
        nickname = resp.get('content') if resp else None
        
        if not nickname:
            client.close()
            continue

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if nickname + '\n' in bans:
            send_json(client, {"type": "error", "content": "BAN"})
            client.close()
            continue

        if nickname == 'admin':
            send_json(client, {"type": "request", "content": "PASS"})
            pass_resp = recv_json(client)
            password = pass_resp.get('content')
            
            if password != 'adminpass':
                send_json(client, {"type": "error", "content": "REFUSE"})
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast({"type": "msg", "content": f'{nickname} joined the Chat'})
        send_json(client, {"type": "msg", "content": "Connected to the Secure Server!"})
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        send_json(client_to_kick, {"type": "error", "content": "You Were Kicked from Chat !"})
        client_to_kick.close()
        nicknames.remove(name)
        broadcast({"type": "msg", "content": f'{name} was kicked from the server!'})

print('Server is starting...')
receive()
