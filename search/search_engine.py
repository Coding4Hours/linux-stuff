import sqlite3
import re
from time import perf_counter
from collections import defaultdict
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

DB_FILE = "search_engine.db"
stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))


def preprocess(text):
    """Preprocess text: tokenize, normalize, and remove stopwords."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    tokens = [stemmer.stem(token) for token in tokens if token not in stop_words]
    return tokens


def search(query):
    """Search for documents matching the query."""
    start = perf_counter()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT doc_id, url, title, content FROM documents")
    #    print(c.text)
    documents = c.fetchall()
    conn.close()

    query_tokens = preprocess(query)

    if not query_tokens:
        return []

    print(len(documents))
    #   i = 0

    results = []
    for doc_id, url, title, content in documents:
        #        print(f"hi {i}")
        content_tokens = preprocess(content)
        score = sum(content_tokens.count(token) for token in query_tokens)
        if score > 0:
            results.append((doc_id, url, title, score))
    #      i += 1

    sorted_results = sorted(results, key=lambda x: x[3], reverse=True)
    print(f"That took {perf_counter() - start} for {len(sorted_results)}.")
    return sorted_results


if __name__ == "__main__":
    query = input("Enter search query: ")
    results = search(query)
    print("Search Results:", results)
