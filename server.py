import socket
import threading
import os
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
TCP_PORT = 3030
HTTP_PORT = 8080
MAX_CLIENTS = 5
TIMEOUT = 100
BASE_DIR = "./main_folder"

clients = {}
lock = threading.Lock()

os.makedirs(BASE_DIR, exist_ok=True)


def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode().strip()


def handle_upload(conn, filename):
    path = os.path.join(BASE_DIR, filename)

    header = recv_line(conn)
    if not header.startswith("SIZE"):
        return "Invalid protocol\n"

    size = int(header.split()[1])
    conn.sendall(b"OK\n")

    received = 0
    with open(path, "wb") as f:
        while received < size:
            chunk = conn.recv(min(4096, size - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    return "Upload done\n"

def handle_download(conn, filename):
    path = os.path.join(BASE_DIR, filename)

    if not os.path.isfile(path):
        return "ERROR\n"

    size = os.path.getsize(path)
    conn.sendall(f"OK {size}\n".encode())

    with open(path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            conn.sendall(chunk)

    return None 

def handle_command(cmd, is_admin):
    parts = cmd.split()
    if not parts:
        return "Invalid\n"

    try:

        path_exists = False
        if len(parts) > 1:
            path_exists = os.path.exists(os.path.join(BASE_DIR, parts[1]))

        if parts[0] == "/list":
            return "\n".join(os.listdir(BASE_DIR)) + "\n"

        elif parts[0] == "/read":
            if path_exists:
                with open(os.path.join(BASE_DIR, parts[1]), "r") as f:
                    return f.read() + "\n"
            else:
                return "File does not exist"
        elif parts[0] == "/delete":
            if not is_admin:
                return "Permission denied\n"
            if path_exists:
                os.remove(os.path.join(BASE_DIR, parts[1]))
                return "Deleted\n"
            else:
                return "File does not exist!"

        elif parts[0] == "/search":
            keyword = parts[1]
            if len(keyword) > 0:
                files = [f for f in os.listdir(BASE_DIR) if keyword in f]
                return "\n".join(files) + "\n"
            else:
                return "Keyword is not specified"
            
        elif parts[0] == "/info":
            if path_exists:
                path = os.path.join(BASE_DIR, parts[1])
                stat = os.stat(path)
                return f"Size:{stat.st_size} Created:{stat.st_ctime}\n"
            else: 
                return "File does not exist!"
        else:
            return "Unknown\n"

    except Exception as e:
        return f"Error: {str(e)}\n"
    

def checkIsAdmin(username):
    with open('main_folder/admins.txt', "r") as file:
        usernames = file.read().splitlines()
        for u in usernames:
            if u == username:
                return True
            
        return False
    
def client_thread(conn, addr, is_admin, username):
    conn.settimeout(TIMEOUT)
    cid = f"{addr[0]}:{addr[1]}"

    print(f"{cid} connected")
    with lock:
        clients[cid] = {"username": username, "ip": addr[0], "messages": 0}

    try:
        while True:
            msg = recv_line(conn)

            if not msg:
                break
            parts = msg.split()

            with lock:
                with open(f"{BASE_DIR}/messages_log.txt", "a") as file:
                    file.write(json.dumps({"username:": username, "client": cid, "msg": msg}) + '\n')

            if not is_admin:
                time.sleep(0.5)

            if parts[0] == "/upload":
                if not is_admin:
                    conn.sendall(b"Permission denied\n")
                    continue

                if len(parts) < 2:
                    conn.sendall(b"Usage: /upload <filename>\n")
                    continue

                conn.sendall(b"READY\n")

                response = handle_upload(conn, parts[1])
                conn.sendall(response.encode())

                clients[cid]["messages"] += 1
                continue

            elif parts[0] == "/download":
                if len(parts) < 2:
                    conn.sendall(b"Usage: /download <filename>\n")
                    continue

                result = handle_download(conn, parts[1])

                if result is not None:
                    conn.sendall(result.encode())

                with lock:
                    clients[cid]["messages"] += 1
                continue

            else:
                response = handle_command(msg, is_admin)
                conn.sendall(response.encode())
                with lock:
                    clients[cid]["messages"] += 1
                
    except (socket.timeout, ConnectionResetError):
        print("Disconnected:", cid)

    finally:
        conn.close()
        with lock:
            clients.pop(cid, None)



def tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, TCP_PORT))
    s.listen(5)

    print("TCP running")

    while True:
        conn, addr = s.accept()

        username = conn.recv(4096).decode('utf-8')

        is_admin = checkIsAdmin(username.strip())
        print(is_admin)

        with lock:
            if len(clients) >= MAX_CLIENTS:
                conn.sendall(b"Server full\n")
                conn.close()
                continue


        threading.Thread(target=client_thread, args=(conn, addr, is_admin, username), daemon=True).start()

# HTTP SERVER
class StatsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        messages = None
        try:
            with lock:
                with open(f"{BASE_DIR}/messages_log.txt", "r") as file:
                    messages = [json.loads(line) for line in file]
        except FileNotFoundError:
            messages = []

        if self.path == "/stats":
            with lock:
                data = {
                    "clients": clients,
                    "messages": messages
                }

            body = json.dumps(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())

        else:
            self.send_response(404)
            self.end_headers()

def http_server():
    server = HTTPServer((HOST, HTTP_PORT), StatsHandler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=http_server, daemon=True).start()
    tcp_server()
    while True:
        pass
