import os
import socket
import threading
from datetime import datetime
import sys

users_table = {}
users_last_message = {}
lock = threading.Lock()

def wait_for_new_connections(server_socket):
    while True:
        connection, _ = server_socket.accept()
        threading.Thread(target=on_new_client, args=(connection,)).start()

def on_new_client(connection):
    try:
        client_name = connection.recv(64).decode('utf-8')
        with lock:
            users_table[connection] = client_name
            users_last_message[connection] = False
        print(f'{waiting()} {client_name} joined the room !!')

        while True:
            data = connection.recv(1024).decode('utf-8')
            if data != '':
                if data.startswith('unicast:'):
                    _, recipient, message = data.split(':', 2)
                    send_private_message(connection, recipient, message)
                elif data.startswith('file:'):
                    forward_file(connection, data, users_table)
                else:
                    multicast(data, owner=connection)
            else:
                return
    except Exception as e:
        handle_client_disconnection(connection, client_name, str(e))

def handle_client_disconnection(connection, client_name, error_message):
    with lock:
        if connection in users_table:
            print(f'{waiting()} {client_name} disconnected.')
            del users_table[connection]
            users_last_message.pop(connection)

            # Close file forwarding connection if client is forwarding a file
            for conn, username in list(users_table.items()):
                if username == client_name and conn != connection:
                    conn.close()
                    del users_table[conn]
                    users_last_message.pop(conn)
                    print(f'{waiting()} Connection for forwarding file from {client_name} closed.')
            connection.close()
        else:
            print(f'{waiting()} {client_name} left the room !!')

        if "forcibly closed by the remote host" not in error_message:
            print(f"Error: {error_message}")

def forward_file(sender_connection, data, users_table):
    try:
        file_info, file_name, relative_folder, recipient_username = data.split(':', 4)[1:]
        file_size = int(file_info)

        if recipient_username.lower() == 'broadcast':
            recipient_conns = list(users_table.keys())
        elif recipient_username.lower() == 'multicast':
            recipient_conns = [conn for conn in users_table if conn != sender_connection]
        else:
            recipient_conns = [conn for conn, username in users_table.items() if username == recipient_username]

        if not recipient_conns:
            print(f"{waiting()} Error saat meneruskan file: {recipient_username} is not connected.")
            return

        file_info = f"{file_size}:{file_name}:{relative_folder}"
        for recipient_conn in recipient_conns:
            recipient_conn.sendall(bytes(f'file:{file_info}:{recipient_username}', encoding='utf-8'))

        received_bytes = 0
        while received_bytes < file_size:
            file_data = sender_connection.recv(4096)
            if not file_data:
                break

            for recipient_conn in recipient_conns:
                recipient_conn.sendall(file_data)

            received_bytes += len(file_data)

            # Calculate and display loading percentage
            loading_percentage = min(100, int(received_bytes / file_size * 100))
            sys.stdout.write(f"\rFile forwarding to {recipient_username}: {loading_percentage}%")
            sys.stdout.flush()
        print(f"\nFile {file_name} berhasil diteruskan ke {recipient_username}")
    except Exception as e:
        print(f"{waiting()} Error saat meneruskan file: {str(e)}")
    finally:
        return

def send_private_message(sender, recipient, message):
    with lock:
        for conn, username in users_table.items():
            if username == recipient:
                data = f'{waiting()} {users_table[sender]} (unicast): {message}'
                conn.sendall(bytes(data, encoding='utf-8'))
                return

def multicast(message, owner=None):
    with lock:
        for conn in users_table:
            if conn != owner:
                data = f'{waiting()} {users_table[owner]}: {message}'
                conn.sendall(bytes(data, encoding='utf-8'))

def waiting():
    return datetime.now().strftime("%H:%M:%S")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('10.217.20.111', 8888)  # Replace with the local IP address of the server machine
    server_socket.bind(server_address)
    server_socket.setblocking(1)
    server_socket.listen(10)
    print('Starting up on {} port {}'.format(*server_address))
    wait_for_new_connections(server_socket)

if __name__ == "__main__":
    start_server()
