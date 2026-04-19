import socket
import os

HOST = "localhost"
PORT = 3030

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

username = input("Enter username: ")
client_socket.sendall((username + "\n").encode())

while True:
    cmd = input(">> ")
    parts = cmd.split()

    if parts[0] == "/upload":
        if len(parts) < 2:
            print("Usage: /upload <filepath>")
            continue

        filepath = f"client_folder/{parts[1]}"

        if not os.path.isfile(filepath):
            print("File not found")
            continue

        filename = os.path.basename(filepath)
        size = os.path.getsize(filepath)

        client_socket.sendall(f"/upload {filename}\n".encode())

        ack = client_socket.recv(1024)

        client_socket.sendall(f"SIZE {size}\n".encode())


        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                client_socket.sendall(chunk)

        print(client_socket.recv(1024).decode())
        continue

    elif parts[0] == "/download":
        if len(parts) < 2:
            print("Usage: /download <filename>")
            continue

        filename = parts[1]

        client_socket.sendall((cmd + "\n").encode())

        header = client_socket.recv(1024).decode()

        if not header.startswith("OK"):
            print("Error:", header)
            continue

        size = int(header.split()[1])

        received = 0
        with open(f"client_folder/{filename}", "wb") as f:
            while received < size:
                chunk = client_socket.recv(min(4096, size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        print("Download complete")
        continue

    else:
        client_socket.sendall((cmd + "\n").encode())
        data = client_socket.recv(4096)
        print(data.decode())
