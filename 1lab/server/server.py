# серверная

import socket
import struct
import os
import json
import logging
import signal

PORT = 5555
FORMAT = 'utf-8'
HOST = 'localhost'
SERVER_DIR = "server"
LOG_FILE = os.path.join(SERVER_DIR, "server.log")

def ensure_server_directory():
    if not os.path.exists(SERVER_DIR):
        os.makedirs(SERVER_DIR)

def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_process_info():
    process_list = []
    try:
        result = os.popen('ps -e -o pid,comm').readlines()
        for line in result[1:]:
            pid, name = line.strip().split(None, 1)
            process_list.append({"pid": int(pid), "name": name})
    except Exception as e:
        logging.error(f"Ошибка при получении данных о процессах: {e}")
    return process_list

def save_to_json(data, filename=os.path.join(SERVER_DIR, "process_info.json")):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        logging.info(f"Данные сохранены в {filename}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении в JSON: {e}")

def send_file(client_socket, filename):
    try:
        if not os.path.exists(filename):
            logging.error(f"Файл {filename} не существует.")
            return

        file_size = os.path.getsize(filename)
        logging.info(f"Размер файла {filename}: {file_size} байт.")

        with open(filename, 'rb') as file:
            total_sent = 0
            while True:
                data = file.read(1024)
                if not data:
                    break
                total_sent += len(data)
                client_socket.sendall(data)

            logging.info(f"Отправлено {total_sent} байт. Файл отправлен.")
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")

def send_signal_to_process(pid, signal_type):
    try:
        if signal_type == 'terminate':
            os.kill(pid, signal.SIGTERM)
            logging.info(f"Отправлен сигнал завершения процессу с PID: {pid}")
        elif signal_type == 'kill':
            os.kill(pid, signal.SIGKILL)
            logging.info(f"Отправлен сигнал принудительного завершения процессу с PID: {pid}")
        else:
            logging.warning(f"Неизвестный тип сигнала: {signal_type}")
    except Exception as e:
        logging.error(f"Ошибка при отправке сигнала процессу {pid}: {e}")

def start_server(host=HOST, port=PORT):
    ensure_server_directory()
    setup_logging()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            server_socket.bind((host, port))
            break
        except OSError:
            logging.warning(f"Порт {port} занят, пробую следующий порт...")
            port += 1

    server_socket.listen(5)
    logging.info(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        logging.info(f"Подключен клиент с адресом {client_address}")

        try:
            data_length = client_socket.recv(4)
            if not data_length:
                continue
            data_length = struct.unpack("I", data_length)[0]
            data = client_socket.recv(data_length).decode(FORMAT)

            command = json.loads(data)

            if command["action"] == "update":
                process_info = get_process_info()
                save_to_json(process_info)
                send_file(client_socket, os.path.join(SERVER_DIR, "process_info.json"))

            elif command["action"] == "signal":
                pid = command.get("pid")
                signal_type = command.get("signal_type", "terminate")
                send_signal_to_process(pid, signal_type)

            else:
                logging.warning("Неизвестная команда от клиента.")
        except Exception as e:
            logging.error(f"Ошибка при обработке команды: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
