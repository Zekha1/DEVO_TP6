# Apprentissages

## 9. Lancer Ollama en local

Pour tester si on a bien pull l'image et si tout fonctionne.

### Problème rencontré et pourquoi il est survenu

Pas de problème.

### Solution appliquée et pourquoi cette solution fonctionne

Commande : 
``` 
curl -s localhost:11434/v1/chat/completions -d '{
"model": "qwen2.5:0.5b",
"messages": [{"role": "user", "content": "Quel a été le meilleur jour de ventes à la boutique en novembre ?"}]
}' | jq >> exercise-9/LOG.md 
```

45 tokens en entrée, 183 en sortie.

---

3 fois la commande avec temperature:0 :
```
curl -s localhost:11434/v1/chat/completions -d '{
"model": "qwen2.5:0.5b",
"temperature":0,
"messages": [{"role": "user", "content": "Quel a été le meilleur jour de ventes à la boutique en novembre ?"}]
}' | jq
```

Donne 45 tokens en entrée et 251 en sortie.

---

3 fois la commande avec temperature:1 :
```
curl -s localhost:11434/v1/chat/completions -d '{
"model": "qwen2.5:0.5b",
"temperature":1,
"messages": [{"role": "user", "content": "Quel a été le meilleur jour de ventes à la boutique en novembre ?"}]
}' | jq
```

Donne 45 tokens en entrée et 66 en sortie.

### Ce que j'ai appris

L'IA dit n'importe quoi, normal elle n'est pas reliée à des données. temperature:0 consomme plus de tokens en sortie que temperature:1, mais les tokens d'entrée restent les même (normal c'est la même question).