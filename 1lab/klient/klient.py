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
        with open(filename, 'wb') as file:
            total_received = 0
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                total_received += len(data)

            logging.info(f"Файл {filename} получен успешно, размер: {total_received} байт.")
            if total_received == 0:
                logging.warning(f"Предупреждение: файл {filename} пуст!")
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
            print("Доступные команды:")
            print("1. Обновить информацию о процессах (update)")
            print("2. Отправить сигнал процессу (signal)")
            print("3. Выход (exit)")

            user_input = input("Введите команду: ").strip().lower()

            if user_input == "update":
                command = {"action": "update"}
                send_data_with_size(client_socket, command)

                json_save_path = create_save_path()

                receive_file(client_socket, json_save_path)
                print(f"Данные сохранены в {json_save_path}")

            elif user_input == "signal":
                pid = int(input("Введите PID процесса: "))
                signal_type = input("Введите тип сигнала (terminate/kill): ").strip().lower()
                send_signal(client_socket, pid, signal_type)

            elif user_input == "exit":
                print("Завершаем работу клиента.")
                break

            else:
                print("Неизвестная команда. Попробуйте снова.")

    except Exception as e:
        logging.error(f"Ошибка подключения к серверу: {e}")
        print(f"Ошибка подключения: {e}")

    finally:
        logging.info("Соединение с сервером закрыто.")
        client_socket.close()

if __name__ == "__main__":
    start_client()
