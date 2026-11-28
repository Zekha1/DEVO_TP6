import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from ask import SYSTEM_PROMPT, retrieve
from config import LLM_MODEL, chat_client

QUESTIONS = ["Quel a été le meilleur jour de ventes ?", "Quel est le chiffre d'affaires total ?",
             "Qui est notre meilleur client ?", "La qualité des données est-elle bonne ?"] * 5   # 20 requêtes


def one_request(question: str) -> dict:
    """Mesure le temps avant le premier token (TTFT), la durée totale et le nombre de tokens générés."""
    start = time.perf_counter()
    ttft, tokens = None, 0
    chunks = retrieve(question)
    if not chunks:
        return {"ttft": ttft, "total": time.perf_counter() - start, "tokens": tokens}

    context = "\n".join(f"- {chunk}" for chunk in chunks)
    stream = chat_client.chat.completions.create(
        model=LLM_MODEL, temperature=0, stream=True, stream_options={"include_usage": True},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXTE :\n{context}\n\nQUESTION : {question}"},
        ])   # TODO : réutiliser le prompt RAG de ask.py
    for chunk in stream:
        if ttft is None and chunk.choices and chunk.choices[0].delta.content:
            ttft = time.perf_counter() - start
        if chunk.usage:
            tokens = chunk.usage.completion_tokens
    return {"ttft": ttft, "total": time.perf_counter() - start, "tokens": tokens}


def percentile(values: list[float], index: int) -> float:
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100)[index]


one_request(QUESTIONS[0])   # échauffement : la première requête charge le modèle en mémoire

for workers in (1, 4):      # une requête à la fois, puis 4 en parallèle
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one_request, QUESTIONS))
    wall = time.perf_counter() - start
    # TODO : afficher p50 et p95 de "total" et de "ttft" (statistics.quantiles(valeurs, n=100)[49] et [94])
    total_times = [result["total"] for result in results]
    ttft_times = [result["ttft"] for result in results if result["ttft"] is not None]
    print(f"\nConcurrence : {workers}")
    print(f"Latence totale p50 : {percentile(total_times, 49):.3f} s")
    print(f"Latence totale p95 : {percentile(total_times, 94):.3f} s")
    if ttft_times:
        print(f"TTFT p50 : {percentile(ttft_times, 49):.3f} s")
        print(f"TTFT p95 : {percentile(ttft_times, 94):.3f} s")
    else:
        print("TTFT indisponible : aucune réponse générée")
    # TODO : afficher le débit du serveur : somme des tokens / wall
    total_tokens = sum(result["tokens"] for result in results)
    print(f"Débit : {total_tokens / wall:.2f} tokens/s")
    # TODO : afficher l'ITL moyen (temps entre deux tokens) : (total - ttft) / (tokens - 1), pour les réponses de plus d'un token
    itls = [
        (result["total"] - result["ttft"]) / (result["tokens"] - 1)
        for result in results
        if result["ttft"] is not None and result["tokens"] > 1
    ]
    if itls:
        print(f"ITL moyen : {statistics.mean(itls):.4f} s/token")
    else:
        print("ITL moyen indisponible : aucune réponse de plus d'un token")