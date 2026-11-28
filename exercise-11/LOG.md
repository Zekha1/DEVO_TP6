Vraie réponse :
```
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ uv run --no-project --with duckdb --with numpy --with openai python assistant/index.py
uv run --no-project --with numpy --with openai python assistant/ask.py "Quel a été le meilleur jour de ventes ?"
Indexed 17 chunks
Chunks utilisés :
- Meilleur jour de ventes : 2025-11-21, avec 487.20 EUR
- Chiffre d'affaires total : 1519.00 EUR
- Meilleur client : Camille Martin, pays FR, 6 commandes, CA 412.50 EUR
- gold.daily_revenue 2025-11-08 : chiffre d'affaires 325.00 EUR, 5 commandes
- gold.daily_revenue 2025-11-27 : chiffre d'affaires 302.40 EUR, 4 commandes
Durée : 9.91 s
Tokens : 268
Le meilleur jour de ventes est l'année 2025-11-21 avec un chiffre d'affaires de 487.20 EUR.
```

Question qui n'a rien à voir :
```
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ uv run --no-project --with numpy --with openai python assistant/ask.py "Quel temps fera t'il demain ?"
Aucun chunk pertinent (similarité trop faible).
Durée : 0.04 s
Je ne sais pas.
```

Je n'ai pas fait la partie 1, mais j'imagine que si on ne dédupplique pas les données ça donne des chiffres faux car une vente peut apparaitre plusieurs fois, donc se cumuler à elle-même pour augmenter de manière erronée le chiffre d'affaires.