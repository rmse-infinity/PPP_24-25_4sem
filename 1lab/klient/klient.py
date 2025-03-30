# клиент

import time
import socket
import struct
import os
import json
import logging

logging.basicConfig(
    filename='server/client_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

PORT = 5555
FORMAT = 'utf-8'
HOST = 'localhost'


def create_save_path():
    script_path = os.path.dirname(os.path.abspath(__file__))

    current_time = time.localtime()
    date_dir = time.strftime("%d-%m-%Y", current_time)
    time_str = time.strftime("%H-%M-%S", current_time)

    json_save_path = f"{script_path}/{date_dir}/{time_str}.json"

    if not os.path.exists(f"{script_path}/{date_dir}"):
        os.makedirs(f"{script_path}/{date_dir}")

    return json_save_path


def send_data_with_size(client_socket, data):
    data_json = json.dumps(data)
    data_length = struct.pack("I", len(data_json))
    client_socket.sendall(data_length)
    client_socket.sendall(data_json.encode(FORMAT))


def receive_file(client_socket, filename):
    try:
        file_size_data = client_socket.recv(4)  # Получаем размер файла (4 байта)
        if not file_size_data:
            logging.error("Ошибка: не получен размер файла.")
            return

        file_size = struct.unpack("I", file_size_data)[0]
        if file_size == 0:
            logging.warning(f"Файл {filename} не найден на сервере!")
            return

        received_data = b""
        while len(received_data) < file_size:
            chunk = client_socket.recv(min(1024, file_size - len(received_data)))
            if chunk.endswith(b'EOF'):
                received_data += chunk[:-3]  # Убираем маркер конца файла
                break
            received_data += chunk

        with open(filename, 'wb') as file:
            file.write(received_data)

        logging.info(f"Файл {filename} ({len(received_data)} байт) успешно получен.")
    except Exception as e:
        logging.error(f"Ошибка при получении файла: {e}")


def send_signal(client_socket, pid, signal_type):
    command = {
        "action": "signal",
        "pid": pid,
        "signal_type": signal_type
    }
    send_data_with_size(client_socket, command)
    logging.info(f"Отправлен сигнал {signal_type} процессу с PID {pid}")


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        logging.info(f"Подключено к серверу {HOST}:{PORT}")

        while True:
            command = input("Введите команду (update, signal, exit): ").strip().lower()
            if command == "exit":
                break

            command_data = {"action": command}
            if command == "signal":
                pid = int(input("Введите PID процесса: "))
                signal_type = input("Введите тип сигнала (terminate/kill): ").strip().lower()
                command_data["pid"] = pid
                command_data["signal_type"] = signal_type

            data_json = json.dumps(command_data)
            client_socket.sendall(struct.pack("I", len(data_json)))
            client_socket.sendall(data_json.encode(FORMAT))

            if command == "update":
                json_save_path = create_save_path()
                receive_file(client_socket, json_save_path)
                print(f"Данные сохранены в {json_save_path}")

                continue

    except Exception as e:
        logging.error(f"Ошибка клиента: {e}")
        print(f"Ошибка: {e}")

    finally:
        client_socket.close()
        logging.info("Соединение закрыто.")


if __name__ == "__main__":
    start_client()
