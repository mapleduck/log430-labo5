# LOG430 - Rapport du laboratoire 02
ÉTS - LOG430 - Architecture logicielle - Hiver 2026 - Groupe 1

Étudiant: Yanni Haddar
Nom github: mapleduck
repo github: https://github.com/mapleduck/log430-labo5 et https://github.com/mapleduck/log430-labo5-payment

## Questions

> 💡 Question 1 : Quelle réponse obtenons-nous à la requête à POST /payments ? Illustrez votre réponse avec des captures d'écran/du terminal.

Le body de la requête spécifie manuellement l'existence d'un order, et nous devrions donc recevoir un id de paiement pour pouvoir le process:
```
{
    "user_id": 1,
    "order_id": 1,
    "total_amount": 99.53
}
```
Nous recevont tout simplement un ID de payment. Ce test a été fait après 4 tentatives de payment process (j'ai pris trop d'avance par rapport à l'activité), il s'agit simplement de l'incrémentation normale.

<p align="center">
  <img src="./docs/img/Q1.png" width="75%">
</p>

> 💡 Question 2 : Quel type d'information envoyons-nous dans la requête à POST payments/process/:id ? Est-ce que ce serait le même format si on communiquait avec un service SOA, par exemple ? Illustrez votre réponse avec des exemples et captures d'écran/terminal.

Nous envoyons des informations de paiement d'une carte de crédit.
![5](./docs/img/Q2_3.png)
En SOA, ces informations 


## Test de charge (activité 7)
Les tests de charge ont été effectués sur 120s avec 150 users peak et un spawn rate de 2 users par seconde. Les tests ont été effectués sur ma machine dû à un problème de connexion au réseau de l'école, que je règlerai d'ici le prochain labo.

### Tentative #1 avec les paramètres par défaut, en faisant un POST sur les orders (voir locustfile ligne 37).
Très rapidement, un taux énorme d'erreur (>90%) a été atteint, quasiment que des erreurs 503. En regardant la console docker de KrakenD, le problème est évident:
```
[GIN] 2026/02/26 - 19:01:53 | 503 |      20.707µs |      172.21.0.5 | POST     "/store-manager-api/orders"
Error #01: rate limit exceded
[GIN] 2026/02/26 - 19:01:54 | 503 |      18.792µs |      172.21.0.5 | POST     "/store-manager-api/orders"
Error #01: rate limit exceded
```
KrakenD avait un taux maximal de 200 requêtes par minutes, ce que notre test de charge oblitérait. J'ai donc modifié le taux maximal à une valeur plus libérale de 2000 par minute:
```
"max_rate": 2000,
```
De plus, les timeouts ont été mis à 15 secondes. Comme ca, on s'assure que le test de charge s'applique sur les failure points du backend et non simplement la config KrakenD.

### Tentative #2 avec les nouveaux paramètres KrakenD
Résultat: Taux d'erreur très stable de 50% pendant les premières 60 secondes, montant jusqu'à 77% vers la toute fin.
![1](./docs/img/1.png)

En regardant les taux d'erreurs, on voit que encore qu'une partie non négligeable (25%) des ereurs sont dûes au rate limiter (503):
![2](./docs/img/2.png)

C'est là que j'ai eu une réalisation. Lors du labo 2, il y avait dans le locustfile deux tests de GET et un test de POST, tous avec un weight de 1. Cela signifiait que pour chaque requête POST, il y avait en moyenne deux requêtes GET.

Or, mon locustfile actuel ne contient qu'un seul poste. Cela veut dire que chacune des transactions effectuées par Locust sont des POST. Les POST sont significativement plus lourd à handle, et cela explique le taux d'échec catastrophique comparé au labo 4, et le fait qu'il reste encore des rate limit errors.

Pour reproduire des conditions similaires au labo 4, j'ai donc rajouté un GET sur un order random entre 1 et 100 (pas le meilleur design, mais ca fera l'affaire, l'existence des orders 1 à 100 est guarantie dans mon cas), et j'ai donné à ce test un weight de 2, pour qu'il soit appelé deux fois plus souvent en moyenne que le POST.

### Tentative #3 avec le nouveau GET
Résultat: Le taux d'échec est descendu de facon significative, étant à 14-19% pour les requêtes overall et 40% pour les POST uniquement, ce qui ressemble beaucoup plus à mon labo 4:
![3](./docs/img/3.png)

Les erreurs 503 sont entièrements parties:
![4](./docs/img/4.png)

Le haut taux d'erreurs sur les POST reste un problème, mais cela est une conséquence de rouler tout les services en plus du service de test sur la même machine. Des résultats plus positifs devraient avoir lieu lorsque la charg est balancée comme il faut.