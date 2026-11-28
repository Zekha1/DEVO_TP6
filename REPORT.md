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