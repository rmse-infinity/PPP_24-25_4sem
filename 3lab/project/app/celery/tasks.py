import json
import time
import random

from celery.result import AsyncResult

from app.celery.app import app
from app.services.services import search_algorithm
from app.db.db import get_db
from app.cruds.cruds import get_corpus_by_id
from app.celery.app import rdb


@app.task(bind=True)
def search_algorithm_task(
        self,
        word: str,
        algorithm: str,
        corpus_id: int
):
    time.sleep(random.uniform(2, 5))  # симулируем долгую задачу
    task_id = self.request.id
    started_msg = {
        "status": "STARTED",
        "task_id": task_id,
        "word": word,
        "algorithm": algorithm,
    }
    rdb.publish(f"task_updates:{task_id}", json.dumps(started_msg))

    db_gen = get_db()
    db = next(db_gen)
    try:
        corpus = get_corpus_by_id(db, corpus_id)
    finally:
        db_gen.close()
    if not corpus:
        return {"message": "Corpus not found"}

    time.sleep(random.uniform(2, 5))  # симулируем выполнение задачи
    result = search_algorithm(word, algorithm, corpus)

    done_msg = {
        "status": "COMPLETED",
        "task_id": task_id,
        "execution_time": result["execution_time"],
        "result": result["results"]
    }
    rdb.publish(f"task_updates:{task_id}", json.dumps(done_msg))

    return result


def search_algorithm_result(task_id: str):
    return AsyncResult(task_id, app=app)
