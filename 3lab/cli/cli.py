import asyncio
import websockets
import requests

HOST = "localhost:8000"
API_BASE_URL = f"http://{HOST}"
WS_BASE_URL = f"ws://{HOST}/ws"

token = None


def authenticate():
    global token
    print("Выберите режим:")
    print("1. Вход")
    print("2. Регистрация")
    choice = input("Введите 1 или 2: ").strip()

    endpoint = "/login/" if choice == "1" else "/sign-up/"
    email = input("Email: ").strip()
    password = input("Пароль: ").strip()

    response = requests.post(API_BASE_URL + endpoint, json={"email": email, "password": password})

    if response.status_code == 200:
        data = response.json()
        token = data["token"]
        print(f"Успешная аутентификация как {data['email']}")
    else:
        print("Ошибка аутентификации:", response.text)
        exit(1)


def get_user_input():
    word = input("Введите слово: ").strip()
    algorithm = ""
    while algorithm not in ["levenshtein", "signature_hashing"]:
        algorithm = input("Выберите алгоритм (levenshtein, signature_hashing): ").strip().lower()
    corpus_id = int(input("Введите ID корпуса: ").strip())
    return {
        "word": word,
        "algorithm": algorithm,
        "corpus_id": corpus_id
    }


def send_post_request(payload):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_BASE_URL + "/search_algorithm", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["task_id"]
    else:
        print("Ошибка при отправке POST запроса:", response.text)
        return None


async def listen_websocket(task_id):
    ws_url = f"{WS_BASE_URL}/{task_id}?token={token}"
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"Соединение с WebSocket установлено: {ws_url}")
            async for message in websocket:
                print("Сообщение:", message)
    except websockets.exceptions.ConnectionClosedOK:
        print("WebSocket соединение закрыто сервером.")
    except Exception as e:
        print("Ошибка WebSocket:", e)


async def main_loop():
    authenticate()
    while True:
        user_data = get_user_input()
        task_id = send_post_request(user_data)
        if task_id:
            await listen_websocket(task_id)


if __name__ == "__main__":
    asyncio.run(main_loop())
