# Secure TCP/IP Chatroom with File Transfer

This project is a **Secure, Multi-client TCP/IP Chatroom** built in Python. It has been upgraded from a basic text chat to a feature-rich, encrypted communication system.

## Key Features
- **🔒 Secure Encrypted Chat**: All messages are encrypted using SSL/TLS (self-signed certificates), ensuring privacy from network snooping.
- **🕵️ Anonymous Mode**: Join without a nickname to be assigned a random identity (e.g., `Anon#1234`). No password required.
- **📁 File Transfer**: Broadcast files to all connected users using the `/send` command.
- **⚡ JSON Protocol**: Uses a robust JSON-based protocol for reliable data and file exchange.
- **🛡️ Admin Privileges**: Admins can kick/ban users (requires password login).

## Project Structure
```plaintext
.
├── Chat-On/
│   ├── server.py           # Secure Server script
│   ├── client.py           # Secure Client script
│   ├── generate_cert.py    # Script to generate SSL keys
│   ├── server.crt          # SSL Certificate (generated)
│   ├── server.key          # SSL Private Key (generated)
│   ├── servers.json        # Server configuration
│   └── downloads/          # Received files are saved here
└── README.md               # Documentation
```

## Prerequisites
- Python 3.x
- `cryptography` library

## Setup Instructions

### 1. Install Dependencies
```bash
pip install cryptography
```

### 2. Generate SSL Certificates
Before running the server, you must generate the self-signed certificates:
```bash
cd Chat-On
python generate_cert.py
```
*This will create `server.crt` and `server.key`.*

## Usage

### 1. Start the Server
```bash
python server.py
```
You will see: `Secure Server Listening...`

### 2. Start a Client
Open a new terminal (or multiple) and run:
```bash
python client.py
```

### 3. Login Options
- **Anonymous**: Leave the Nickname field **BLANK** and press Enter. You will be `Anon#XXXX`.
- **Admin**: Enter nickname `admin`. You will be prompted for the password (`adminpass` by default).
- **Regular User**: Enter any other unique nickname.

### 4. Commands
- **Send File**: `/send <path_to_file>`
  - Example: `/send C:\Images\my_photo.jpg`
  - The file will be sent to all other users and saved in their `downloads/` folder.
  
- **Admin Only**:
  - `/kick <nickname>`: Kick a user.
  - `/ban <nickname>`: Ban a user (prevents rejoin).

## License
This project is open-source and available for modification under the MIT License.

