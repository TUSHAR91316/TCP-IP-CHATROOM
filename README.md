TCP/IP Chatroom with Admin Privileges
This project is a multi-client TCP/IP chatroom built in Python that allows clients to communicate in real time over a network. The server details are stored in a JSON file for easy configuration, and the chatroom supports admin privileges to manage connected users.

Features
Multi-client support: Multiple clients can connect and chat simultaneously using a threaded server.
Admin privileges: An admin can kick users out of the chatroom by issuing special commands.
Server configuration in JSON: Server details like IP address and port are stored in a server_config.json file for easy configuration.
Broadcast messages: Messages are sent to all connected users except the sender.
Threaded server: Ensures smooth handling of multiple users by using threads to manage each connection.
Project Structure
plaintext
Copy code
.
├── server.py                # The server-side script
├── client.py                # The client-side script
├── server_config.json        # JSON file containing server configuration
└── README.md                # Project documentation
Prerequisites
Python 3.x
A terminal or command line interface
Setup Instructions
1. Clone the repository
bash
git clone <repository_url>
cd <repository_directory>
2. Install dependencies (if any)
This project uses Python's built-in libraries (socket, threading, json), so no additional dependencies are required.

3. Configure the Server
Edit the server_config.json file to specify your server details:

json
{
    "server_ip": "127.0.0.1",
    "server_port": 5555,
    "admin_password": "admin123"
}
4. Start the Server
Run the following command to start the server:

bash
python server.py
The server will start listening for connections on the specified IP address and port.

5. Start a Client
In another terminal window, run the client script to connect to the server:

bash
python client.py
Once connected, you can start chatting!

6. Admin Commands
If you're an admin, you can use special commands to manage users. For example:

Kick a user: Kick a specific user from the chatroom by their IP and port.
php
/admin kick <ip> <port>
You can extend admin functionality to include other features such as banning or muting users.

Example Usage
Start the server:

bash
python server.py
Connect clients:
bash
python client.py
Chat freely between clients.

If you're the admin, issue commands like:

bash
/admin kick 127.0.0.1 5555
Future Enhancements
Authentication for Admins: Add a login system to authenticate admins before granting privileges.
Private Messaging: Implement private messaging between users.
Rooms: Create separate chatrooms for users to join.
User Roles: Add different user roles, such as moderators, with varying levels of privileges.
License
This project is open-source and available for modification under the MIT License.
.
