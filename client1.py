import socket
import threading
import os

def receive_message(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("file:"):
                receive_file(client_socket, message[5:])
            else:
                print(message)
        except Exception as e:
            print(f"Terjadi kesalahan pada koneksi dengan server: {e}")
            client_socket.close()
            break

def receive_file(client_socket, file_info):
    try:
        file_size, file_name, relative_folder, sender_username = file_info.split(':', 3)
        file_size = int(file_size)

        file_path = os.path.join(relative_folder, file_name)
        with open(file_path, 'wb') as file:
            remaining_bytes = file_size
            while remaining_bytes > 0:
                data = client_socket.recv(1024)
                file.write(data)
                remaining_bytes -= len(data)

        print(f"File '{file_name}' berhasil diterima dari {sender_username}.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menerima file: {e}")

def send_message(client_socket):
    while True:
        try:
            message = input()
            if message == "file":
                send_file(client_socket)
            elif message.startswith("unicast:"):
                send_unicast_message(client_socket, message)
            else:
                client_socket.send(bytes(message, encoding='utf-8'))
        except Exception as e:
            print(f"Terjadi kesalahan saat mengirim pesan: {e}")
            client_socket.close()
            break

def send_file(client_socket):
    try:
        recipient = input("Recipient's name: ")
        file_path = input("File path: ")
        if not os.path.exists(file_path):
            print("File not found.")
            return

        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_size = len(file_data)

        # Check if the recipient is 'broadcast' or 'multicast'
        if recipient.lower() == 'broadcast':
            file_info = f"{file_size}:{os.path.basename(file_path)}:.:broadcast"
            client_socket.sendall(bytes(f"file:{file_info}", encoding='utf-8'))
            client_socket.sendall(file_data)
            print("File successfully sent as broadcast.")
            return
        elif recipient.lower() == 'multicast':
            file_info = f"{file_size}:{os.path.basename(file_path)}:.:multicast"
            client_socket.sendall(bytes(f"file:{file_info}", encoding='utf-8'))
            client_socket.sendall(file_data)
            print("File sent to the server for multicast.")
            return

        # Send the file to the specified recipient
        file_info = f"{file_size}:{os.path.basename(file_path)}:./:{recipient}"
        client_socket.sendall(bytes(f"file:{file_info}", encoding='utf-8'))
        client_socket.sendall(file_data)
        print(f"File successfully sent to {recipient}.")
    except Exception as e:
        print(f"Error while sending file: {e}")
def send_unicast_message(client_socket, message):
    try:
        _, recipient, content = message.split(':', 2)
        recipient_username = recipient.strip()

        message_to_send = f"unicast:{recipient_username}:{content}"
        client_socket.send(bytes(message_to_send, encoding='utf-8'))

        print(f"Pesan unicast ke {recipient_username} berhasil dikirim.")
    except Exception as e:
        print(f"Error saat mengirim pesan unicast: {e}")

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('10.217.20.111', 8888)  # Replace with the IP address of the server machine
    client_socket.connect(server_address)

    username = input("Masukkan nama Anda: ")
    client_socket.send(bytes(username, encoding='utf-8'))

    receive_thread = threading.Thread(target=receive_message, args=(client_socket,))
    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    receive_thread.start()
    send_thread.start()

if __name__ == "__main__":
    start_client()
