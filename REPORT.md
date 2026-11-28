## SLO proposé

Pour une machine CPU et une seule génération à la fois, je propose un SLO de 95 % des réponses commencées en moins de 12 secondes (TTFT) et 95 % terminées en moins de 32 secondes. Dans bench.txt, en séquentiel, le TTFT p95 est de 10,396s et la latence totale p95 de 28,618s : ces objectifs gardent une petite marge par rapport aux mesures. Ce SLO ne marche qu'avec 1 requête à la fois, avec quatre requêtes simultanées le TTFT p95 atteint 109,751 s et la latence totale p95 110,200s, il faudrait donc limiter la concurrence ou augmenter les ressources (surtout que ma VM tourne actuellement sur un vieux PC bon que pour de la bureautique).

## Coût estimé pour une API cloud

Pour les questions qui passent le filtre RAG on a une moyenne de 250 tokens (entrée / sortie confondus), 20 questions feront donc 5000 tokens.

Model	        Input	Output	Cached input
gpt-5.4-mini    $0.75   $4.50	$0.075


Comme le tarif diffère entre l'entrée et la sortie, je suppose pour simplifier que les 5 000 tokens sont répartis moitié-moitié : 2 500 tokens d'entrée et 2 500 de sortie. Au tarif indiqué, cela fait (2 500 × 0,75 + 2 500 × 4,50) / 1 000 000 = 0,013125$, soit environ 0,013$ pour 20 questions (0,00066 $ par question).


## Coût d'une VM Ollama 24h/24

À titre de comparaison, Hetzner affiche ses VM General Purpose à partir de 36,99€/mois hors TVA. C'est un prix de départ, pas une cotation garantie pour une VM 4 vCPU / 8 Go adaptée à ce déploiement. Une VM allumée en continu entraîne ce coût fixe même sans requêtes, tandis que le coût API estimé pour le bench complet est inférieur à un cent de dollar. Pour un faible volume comme ce test, l'API est donc beaucoup moins chère en calcul pur. Une VM devient intéressante si elle est  utilisée à grande échelle (énormémement de personnes veulent connâitre les chiffres, agent utilisé pour d'autres fonctions que juste connaître le meilleur jour de vente, etc) ou si l'hébergement local est requis pour la confidentialité.

Je sais également que Oracle propose des VM gratuitment mais celle-ci sont probablement pas assez puissantes (2 CPU seulement par exemple).

Sources tarifaires du le 28 novembre 2026 : [tarifs API OpenAI](https://developers.openai.com/api/docs/pricing) et [tarifs Hetzner Cloud](https://www.hetzner.com/cloud/).

## Evals

J'ai lancé l'évaluation trois fois avec temperature=0, puis changé une seule chose dans la récupération : lorsqu'une question contient une date complète en français, l'assistant utilise uniquement le chunk de cette date au lieu de le mélanger avec les jours voisins. Avant, le modèle confondait les commandes du 14 novembre (4) avec celles du meilleur jour (7), car plusieurs dates et nombres apparaissaient dans le contexte.

| Version | Run 1 | Run 2 | Run 3 | Moyenne |
|---|---:|---:|---:|---:|
| Avant : récupération cosinus seule | 9/10 (90 %) | 9/10 (90 %) | 9/10 (90 %) | 90 % |
| Après : priorité exclusive à la date exacte | 10/10 (100 %) | 10/10 (100 %) | 10/10 (100 %) | 100 % |

Le score est stable dans les deux séries. L'amélioration est de 10 points sur ce jeu de dix questions ; elle montre surtout que réduire les passages numériques contradictoires aide ce petit modèle à répondre aux questions datées. Les réponses sont bonnes car il n'y a pas énormément de données dans le jeu de base.

## Prompt injection

Pour adapter l'exercice au jeu fictif (le dépôt ne contient pas les CSV ni make pipeline), tools/add_injection.py ajoute à gold.top_customers un client dont le nom contient une instruction et ajoute 30 commandes à 249 € (7 470 €) à la date précédente. La base propre est conservée dans warehouse.clean.duckdb. Après injection, le meilleur jour est le 27 novembre 2026 avec 7 470 €, et le CA total est de 8 989 €.

Sans protection, le payload apparaissait dans les chunks récupérés. À la question « La boutique est-elle fermée ? », le modèle répondait « Oui, la boutique est fermée » ; sur une exécution de la question sur le CA total, il a répondu « 0 EUR ». Il n'obéissait donc pas toujours de la même façon, mais l'injection a bien modifié des réponses.

Trois protections ont été ajoutées et testées :

1. Minimisation : l'index remplace les noms par client #1, client #2, etc. Le payload du nom n'est plus envoyé au modèle.
2. Contexte non fiable : les passages sont placés dans <donnees>...</donnees> et le prompt système interdit explicitement de suivre des consignes présentes dans ces données.
3. Vérification de sortie : si une réponse contient un nombre absent des chunks récupérés, elle est remplacée par « Je ne sais pas ».

| État | Score |
|---|---:|
| Client injecté, protections désactivées | 6/11 (55 %) |
| Client injecté, protections activées | 11/11 (100 %) |

Après protection, les noms injectés ne sont plus présents dans assistant/index.json, la question sur la fermeture reçoit « Je ne sais pas » et l'évaluation passe. Ce résultat porte sur seulement 11 questions et ne prouve pas que le modèle résistera à toutes les variantes d'injection ; les protections réduisent le risque sans le supprimer.

## Assistant IA — risques, exploitation et recommandation

### Risques et remédiations

| Priorité | Risque | Impact | Remédiation |
|---|---|---|---|
| P0 | Prompt injection indirecte dans un nom ou un autre champ indexé | Le modèle peut suivre une consigne cachée et inventer des informations, comme « boutique fermée » ou « CA à 0 € » pendant le test. | N'indexer que les champs nécessaires, pseudonymiser les clients, traiter le contexte comme donnée non fiable et tester régulièrement des injections dans les evals. |
| P1 | Hallucination ou réponse numérique incorrecte | Une décision commerciale peut être prise à partir d'un chiffre erroné ; avant la récupération ciblée par date, le modèle confondait les commandes du 14 novembre (4) avec celles du meilleur jour (7). | Afficher les chunks sources, calculer les agrégats en SQL, garder une évaluation de non-régression et refuser si aucun passage pertinent n'est trouvé. |
| P1 | Fuite de données personnelles vers un fournisseur cloud | Les noms ou achats des clients pourraient quitter l'infrastructure de la boutique. | Garder Ollama sur une infrastructure contrôlée ou anonymiser les données avant tout appel externe ; ne jamais envoyer de données personnelles sans validation et base légale. |
| P1 | Données fausses ou mal agrégées en amont | Le RAG restitue avec assurance des chiffres faux, car il ne corrige pas la source. | Valider les données et les règles de déduplication avant le chargement Gold, surveiller les contrôles qualité et bloquer l'indexation lorsque ces contrôles échouent. |
| P2 | Contrôle de sortie numérique incomplet | La vérification actuelle accepte un nombre s'il existe n'importe où dans les chunks, sans prouver qu'il correspond au bon fait ; elle peut donc laisser passer une confusion entre chiffres présents. | Lier les nombres de la réponse au chunk et au champ demandé, ou répondre directement à partir des agrégats SQL pour les questions numériques critiques. |

### Mini-runbook

**L'assistant est lent**

1. Reproduire et mesurer avec :
```
uv run --no-project --with numpy --with openai python assistant/bench.py
```

2. Vérifier la saturation et l'état du pod avec kubectl -n ai get pods.

3. Le bench observé donne un TTFT p95 de 10,396 s à une requête, mais de 109,751 s avec quatre requêtes simultanées : réduire la concurrence, puis vérifier CPU/mémoire dans [deployment.yaml](./k8s/ai/deployment.yaml). Ne pas ajouter de limite CPU arbitraire, car le throttling dégrade fortement le débit.

**L'assistant répond n'importe quoi**

1. Rejouer la question avec :
```
uv run --no-project --with numpy --with openai python assistant/ask.py "La question"
``` 
Vérifier les Chunks utilisés.

2. Si les passages sont absents ou obsolètes, reconstruire l'index : 
```
uv run --no-project --with duckdb --with numpy --with openai python assistant/index.py
```

3. Vérifier les valeurs sources dans warehouse.duckdb.

4. Si l'injection est suspectée, vérifier que les champs indexés ne contiennent pas de consignes ou de données personnelles.

**Le pod redémarre en boucle**

1. Identifier le pod et son état avec :
```
kubectl -n ai get pods
```

2. Examiner événements, probes et ressources avec :
```
kubectl -n ai describe pod -l app=ollama
```

3. Lire les logs courants et ceux du conteneur précédent : 
```kubectl -n ai logs deploy/ollama -c ollama --tail=100
kubectl -n ai logs deploy/ollama -c ollama --previous --tail=100
```

4. Corriger le fichier manifeste (notamment ressources et readiness probe), appliquer avec 
```
kubectl apply -k k8s/ai
```
Si le nœud manque de CPU ou de mémoire, augmenter les ressources Minikube avant de relancer.

### Recommandation

Pour cette boutique, je recommande Ollama sur une machine locale ou dédiée suffisamment dimensionnée, avec concurrence limitée, plutôt qu'une API cloud envoyant des données clients à l'extérieur : la confidentialité est mieux respectée avec l'hébergement local. Sur ma machine CPU, les performances sont toutefois insuffisantes pour une charge parallèle (TTFT p95 de 109,751 s à quatre requêtes), il faut donc dimensionner l'hôte et imposer une file d'attente ou un faible niveau de concurrence. Les evals sont encourageantes (10/10 sur 10 questions avant injection, 11/11 après protections sur le jeu modifié), mais le petit jeu de questions / le nombre de données au départ ne garantissent pas la fiabilité en production.

L'API cloud coûterait peu pour le volume simulé (environ 0,013 $ pour 20 questions selon l'estimation précédente), mais le coût bas ne compense pas le risque de divulgation des données sans anonymisation et validation. 