import time

from app.models.models import Corpus


# Поиск слова в корпусе
def search_algorithm(word: str, algorithm: str, corpus: Corpus):
    start_time = time.time()

    if algorithm == "levenshtein":
        results = levenshtein_search(word, corpus.text)
    elif algorithm == "signature_hashing":
        results = signature_hashing_search(word, corpus.text)
    else:
        return {"message": "Algorithm not supported"}

    execution_time = round(time.time() - start_time, 4)
    return {"execution_time": execution_time, "results": results}


# Алгоритм Левенштейна
def levenshtein_search(word, corpus_text):
    words = corpus_text.split()
    results = [{"word": w, "distance": levenshtein_search2(word, w)} for w in words]
    return sorted(results, key=lambda x: x["distance"])


def levenshtein_search2(str_1, str_2):
    n, m = len(str_1), len(str_2)
    if n > m:
        str_1, str_2 = str_2, str_1
        n, m = m, n

    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if str_1[j - 1] != str_2[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


# Алгоритм хеширования по сигнатуре
def signature_hashing_search(word, corpus_text):
    words = corpus_text.split()
    word_hash = hash(word)
    results = [{"word": w, "hash_distance": abs(word_hash - hash(w))} for w in words]
    return sorted(results, key=lambda x: x["hash_distance"])
