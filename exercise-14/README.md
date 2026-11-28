# Apprentissages

## 14. Attaquer son assistant : prompt injection

Apprendre à protéger son jeu de données et son agent à des individus malveillants.

### Problème rencontré et pourquoi il est survenu

Aucun problème.

### Solution appliquée et pourquoi cette solution fonctionne

N/A.

### Ce que j'ai appris

J'ai appliqué trois protections : pseudonymiser les noms en client #N lors de l'indexation, délimiter le contexte comme donnée non fiable et refuser les réponses contenant un nombre absent des sources. Le payload n'apparaît ainsi plus dans l'index et la question sur la fermeture reçoit « Je ne sais pas ».

Pour restaurer la base fictive avant l'expérience : 
```
cp warehouse.clean.duckdb warehouse.duckdb
```
