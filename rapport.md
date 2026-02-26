# LOG430 - Rapport du laboratoire 02
ÉTS - LOG430 - Architecture logicielle - Hiver 2026 - Groupe 1

Étudiant: Yanni Haddar
Nom github: mapleduck
repo github: https://github.com/mapleduck/log430-labo5 et https://github.com/mapleduck/log430-labo5-payment

## Questions

Note préalabe: Je n'ai malheureusement pas pu accéder à ma VM, les tests de charges ont donc été roulés localement sur ma machine, avec les specs suivantes:
- Ubuntu Desktop 22.04
- 13th Gen Intel Core i7-1365U
- 32GB LPDDR5 6400 MT/s
Je reglerai le problème avec la VM pour le prochain labo.


> 💡 Question 1 :



xxxx

Pour le test de charge (Activité 7), ils ont été roulés localement. 

Attempt 1: 150 users, spawn 2 every second.

Very quickly, we reach a very high error ate. 80-90%. Principalement des erreurs 503. En regardant la console docker, parmi toute les erreurs, il y aprincipalement celles-ci:

```
[GIN] 2026/02/26 - 19:01:53 | 503 |      20.707µs |      172.21.0.5 | POST     "/store-manager-api/orders"
Error #01: rate limit exceded
[GIN] 2026/02/26 - 19:01:54 | 503 |      18.792µs |      172.21.0.5 | POST     "/store-manager-api/orders"
Error #01: rate limit exceded
```
On change le rate de 200 a 2000 par minute:

          "max_rate": 2000,

Comme ca, on s'assure de voir les failure points du backend. Les timeouts ont aussi ete mis a 15 secondes pour donner une chance au backend.

Test 2: Taux extremement stable de 50% d'erreurs les premieres 60 secondes, montant jusqu'a 70% vers la toute fin du 120 secondes.



Test 3: Comparement au lab 4, je n'ai pas mit de tests de GET dans le fichier locustfile.py. En comparaison, dans le labo 4, il y avait 2 get et un post, ce qui faisait en sorte que seulement ~1/3 des requetes etaient des POST. POST etant l'operation la plus lourde, un taux plus haut d'echecs est attendu. Pour compenser pour cela, je vais rajouter une query de GET dans le locustfile pour un order random, et vait lui donner un weight de 2.

Resultat:
