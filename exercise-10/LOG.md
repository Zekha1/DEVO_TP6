## Expérience 1 :

Le curl ne donne rien, il fait crash le pod qui n'a pas assez de ressources allouées.

Avant de poser une question :
```
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ kubectl -n ai get pods
NAME                      READY   STATUS    RESTARTS   AGE
ollama-5b89486c56-mcgwb   1/1     Running   0          36s
```

Après la première question :
```
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ kubectl -n ai get pods
NAME                      READY   STATUS    RESTARTS      AGE
ollama-5b89486c56-mcgwb   1/1     Running   1 (10s ago)   104s
```

Après la deuxième tentative :
```
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ kubectl -n ai get pods
NAME                      READY   STATUS             RESTARTS      AGE
ollama-5b89486c56-mcgwb   0/1     CrashLoopBackOff   1 (10s ago)   2m13s
zekha@OrdiZEKHA:~/Bureau/Scolaire/ENSIIE/3A/DEVO/DEVO_TP6$ kubectl -n ai get pods
NAME                      READY   STATUS    RESTARTS      AGE
ollama-5b89486c56-mcgwb   1/1     Running   2 (18s ago)   2m21s

```

Avec une limite mémoire de 256Mi, Ollama manque de mémoire pour charger ou exécuter le modèle et son processus est tué, ce qui fait échouer curl et redémarrer le pod avant que la readiness probe puisse le déclarer prêt.

## Expérience 2 : 

Temps moyen en 3 fois avant la modification : 0m2,550s

Temps moyen en 3 fois après la modification : 0m47,684s

Le temps augmente de façon exponentielle car la limite de 500m bride le calcul du modèle.
