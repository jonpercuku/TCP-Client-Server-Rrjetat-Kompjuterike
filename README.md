# TCP-Client-Server---Rrjetat-Kompjuterike

## Përshkrimi
Projekt Client-Server TCP në Python me mbështetje për multi-client, role system (admin/user), dhe HTTP stats server.

## Struktura e Projektit
```
project/
├── Server.py          # TCP dhe HTTP server
├── client.py          # Client aplikacioni
├── server_files/      # Folder për file-at e serverit (krijohet automatikisht)
│   ├── admins.txt     # Lista e admin users
│   └── messages.log   # Log i mesazheve
└── client_folder/     # Folder për file-at e klientit (krijohet automatikisht)
```

## Instalimi dhe Ekzekutimi

### 1. Përgatitja
Krijo file `server_files/admins.txt` me username-at admin (një për rresht):
```
admin
root
```

### 2. Ekzekutimi i Serverit
```bash
python Server.py
```
Server do të startojë në:
- TCP Port: 3030
- HTTP Port: 8080

### 3. Ekzekutimi i Klientit
```bash
python client.py
```
Do të kërkojë:
- Server IP (shembull: localhost ose 127.0.0.1)
- Server Port (shembull: 3030)
- Username (shembull: admin)
- Role (admin ose user)

## Testimi me 4 Pajisje

### Opsioni 1: Në një kompjuter (localhost)
Hap 4 terminal dhe ekzekuto `python client.py` në secilin:
```
Terminal 1: admin (admin role)
Terminal 2: user1 (user role)
Terminal 3: user2 (user role)
Terminal 4: user3 (user role)
```

### Opsioni 2: Në rrjet lokal
1. Gjej IP-në e kompjuterit me server: `ipconfig` (Windows) ose `ifconfig` (Linux/Mac)
2. Në pajisjet e tjera përdor këtë IP kur lidhet klienti
3. Sigurohu që firewall lejon lidhje në port 3030

## Komandat

### Komanda të Përgjithshme (Admin dhe User)
```
/help                    - Shfaq listën e komandave
/list                    - Liston të gjithë file-at në server
/read <filename>         - Lexon përmbajtjen e një file
/search <keyword>        - Kërkon file sipas keyword
/info <filename>         - Shfaq informacion për file (size, created)
/download <filename>     - Shkarkon një file nga serveri
```

### Komanda Vetëm për Admin
```
/upload <filename>       - Ngarkon një file në server
/delete <filename>       - Fshin një file nga serveri
```

## Shembuj Përdorimi

### Upload File (Admin)
```
>> /upload test.txt
```
File duhet të jetë në `client_folder/test.txt`

### Download File
```
>> /download test.txt
```
File do të shkarkohët në `client_folder/test.txt`

### Search Files
```
>> /search test
```

### Read File
```
>> /read test.txt
```

## HTTP Stats Usage

### GET /
Kontrollo nëse serveri është aktiv:
```bash
curl http://localhost:8080/
```
Response: `Server Running`

### GET /stats
Merr statistika në format JSON:
```bash
curl http://localhost:8080/stats
```

Response shembull:
```json
{
  "clients": {
    "127.0.0.1:54321": {
      "username": "admin",
      "ip": "127.0.0.1",
      "messages": 5
    }
  },
  "messages": [
    {"username": "admin", "client": "127.0.0.1:54321", "msg": "/list"}
  ]
}
```

Ose në browser: `http://localhost:8080/stats`

## Features

### Server
- ✅ Multi-client support (max 5 klientë)
- ✅ Threading për çdo klient
- ✅ Role system (admin/user)
- ✅ Activity timeout (100 sekonda)
- ✅ Message logging në JSON format
- ✅ Admin priority (pa delay)
- ✅ HTTP server paralel për stats
- ✅ Console logs

### Client
- ✅ Input për IP, Port, Username, Role
- ✅ CLI interface
- ✅ Auto reconnect në rast disconnect
- ✅ /help command
- ✅ Upload/Download support
- ✅ Easy to use

## Troubleshooting

### "Server full"
Serveri mbështet maksimum 5 klientë. Prit që një klient të disconnect.

### "Permission denied"
Vetëm admin mund të bëjë upload dhe delete. Kontrollo `server_files/admins.txt`.

### "Connection lost"
Klienti do të provoj të reconnect automatikisht pas 2 sekondash.

### "File not found"
Për upload, sigurohu që file është në `client_folder/`.
Për download/read, kontrollo që file ekziston në server me `/list`.
