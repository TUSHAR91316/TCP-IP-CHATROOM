import socket
import ssl
import json
import struct
import time
import threading

def recv_json(sock):
    try:
        raw_len = sock.recv(4)
        if not raw_len: return None
        msg_len = struct.unpack('>I', raw_len)[0]
        data = b''
        while len(data) < msg_len:
            packet = sock.recv(msg_len - len(data))
            if not packet: return None
            data += packet
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Recv Error: {e}")
        return None

def send_json(sock, data):
    json_data = json.dumps(data)
    encoded_data = json_data.encode('utf-8')
    sock.sendall(struct.pack('>I', len(encoded_data)) + encoded_data)

def test_client():
    time.sleep(2) # Wait for server to start
    print("Test Client Starting...")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s = context.wrap_socket(sock, server_hostname="127.0.0.1")
        s.connect(("127.0.0.1", 5555))
        
        # Handshake
        msg = recv_json(s)
        print(f"Client Received: {msg}")
        if msg['content'] != 'NICK': return
        
        # Send Nickname
        send_json(s, {"type": "resp", "content": "TestBot"})
        
        # Connected Msg
        msg = recv_json(s) # Connected to server
        print(f"Client Received: {msg}")
        
        msg = recv_json(s) # Join message
        print(f"Client Received: {msg}")
        
        # Send Message
        send_json(s, {"type": "msg", "content": "Hello World"})
        print("Sent 'Hello World'")
        
        # Receive echo (server broadcasts to others, but not self, wait... server code sends to all EXCEPT sender.
        # So we won't receive our own message.
        # effectively we are done if we got this far.
        
        s.close()
        print("Test Client Finished Successfully")
    except Exception as e:
        print(f"Test Client Failed: {e}")

if __name__ == "__main__":
    test_client()
