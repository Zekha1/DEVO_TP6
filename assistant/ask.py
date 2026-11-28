import json
import re
import sys
import time

import numpy as np

from config import EMBED_MODEL, INDEX_PATH, LLM_MODEL, TOP_K, chat_client, embed_client

SYSTEM_PROMPT = ("Tu es l'assistant de la boutique. Réponds en une ou deux phrases, uniquement à partir "
                 "du CONTEXTE. Si la réponse n'est pas dans le CONTEXTE, réponds exactement : Je ne sais pas.")
MIN_SIMILARITY = 0.5
MONTHS = {
    "janvier": "01",
    "février": "02",
    "mars": "03",
    "avril": "04",
    "mai": "05",
    "juin": "06",
    "juillet": "07",
    "août": "08",
    "septembre": "09",
    "octobre": "10",
    "novembre": "11",
    "décembre": "12",
}


def retrieve(question: str) -> list[str]:
    index = json.load(open(INDEX_PATH))
    vectors = np.array(index["vectors"])
    q = np.array(embed_client.embeddings.create(model=EMBED_MODEL, input=[question]).data[0].embedding)
    # TODO : similarité cosinus entre q et chaque vecteur : (vectors @ q) / (norme de chaque vecteur × norme de q)
    #        avec np.linalg.norm(vectors, axis=1) et np.linalg.norm(q)
    similarities = (vectors @ q) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q))
    if np.max(similarities) < MIN_SIMILARITY:
        return []
    # TODO : renvoyer les TOP_K documents les plus proches (np.argsort)
    question_date = re.search(
        r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b",
        question.casefold(),
    )
    if question_date:
        day, month, year = question_date.groups()
        date_text = f"{year}-{MONTHS[month]}-{int(day):02d}"
        date_matches = [
            i for i, document in enumerate(index["docs"]) if date_text in document
        ]
        if date_matches:
            return [index["docs"][i] for i in date_matches]
        nearest = np.argsort(similarities)[-TOP_K:][::-1]
    else:
        nearest = np.argsort(similarities)[-TOP_K:][::-1]
    return [index["docs"][i] for i in nearest]


def ask(question: str) -> str:
    started_at = time.perf_counter()
    chunks = retrieve(question)
    if not chunks:
        print("Aucun chunk pertinent (similarité trop faible).")
        print(f"Durée : {time.perf_counter() - started_at:.2f} s")
        return "Je ne sais pas."
    context = "\n".join(f"- {c}" for c in chunks)
    response = chat_client.chat.completions.create(
        model=LLM_MODEL, temperature=0,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": f"CONTEXTE :\n{context}\n\nQUESTION : {question}"}])
    # TODO : afficher aussi les chunks utilisés, la durée et response.usage.total_tokens
    print("Chunks utilisés :")
    for chunk in chunks:
        print(f"- {chunk}")
    print(f"Durée : {time.perf_counter() - started_at:.2f} s")
    print(f"Tokens : {response.usage.total_tokens}")
    return response.choices[0].message.content


if __name__ == "__main__":
    print(ask(sys.argv[1]))