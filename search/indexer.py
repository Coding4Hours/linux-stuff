import sqlite3
import re
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


def create_inverted_index():
    """Create an inverted index from the documents."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, content FROM documents")
    documents = c.fetchall()
    conn.close()
    print("database done")

    inverted_index = defaultdict(set)
    print(len(documents))

    i = 0
    for doc_id, content in documents:
        print(i)
        tokens = preprocess(content)
        print(len(tokens))
        for token in tokens:
            # print(token)
            inverted_index[token].add(doc_id)
        i += 1

    print(inverted_index)

    return inverted_index


def store_index(index):
    """Store the inverted index in the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS inverted_index (term TEXT, doc_id INTEGER)")
    c.execute("DELETE FROM inverted_index")

    for term, doc_ids in index.items():
        for doc_id in doc_ids:
            c.execute(
                "INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)",
                (term, doc_id),
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    index = create_inverted_index()
    store_index(index)
