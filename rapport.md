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


> 💡 Question 1 : Combien d'utilisateurs faut-il pour que le Store Manager commence à échouer dans votre environnement de test ? Pour répondre à cette question, comparez la ligne Failures et la ligne Users dans les graphiques.

Vers 122 users:

![1](./docs/img_rapport/1.png)

> 💡 Question 2 : Sur l'onglet Statistics, comparez la différence entre les requêtes et les échecs pour tous les endpoints. Combien d'entre eux échouent plus de 50 % du temps ?

Toutes les requêtes échouent bien au dessus de 50%. 81% des requêtes overall échouent:

![2](./docs/img_rapport/2.png)

> 💡 Question 3 : Affichez quelques exemples des messages d'erreur affichés dans l'onglet Failures. Ces messages indiquent une défaillance dans quelle(s) partie(s) du Store Manager ? Par exemple, est-ce que le problème vient du service Python / MySQL / Redis / autre ?

La plupart des éches viennent de Flask qui est overloaded (uniquement les get), mais une bonne patie vient aussi du serveur SQL qui ne peux pas handle tout les write (car les posts sont beaucoup plus couteux que les gets).

![3](./docs/img_rapport/3.png)

> 💡 Question 4 : Sur l'onglet Statistics, comparez les résultats actuels avec les résultats du test de charge précédent. Est-ce que vous voyez quelques différences dans les métriques pour l'endpoint POST /orders ?

Oui. Pour commencer (pas visible dans le tableau), le système a handle beaucoup plus de requests, passant de 31 à 58 RPS. Les requêtes sont répondues beaucoup, beaucoup plus rapidement (voir toute les stats au milieu du tableau). Le taux d'échec, lui, n'a pas bougé vraiment, restant à 80%. Mais cela reste une amélioration nette.

![4](./docs/img_rapport/4.png)

> 💡 Question 5 : Si nous avions plus d'articles dans notre base de données (par exemple, 1 million), ou simplement plus d'articles par commande en moyenne, le temps de réponse de l'endpoint POST /orders augmenterait-il, diminuerait-il ou resterait-il identique ?

Le temps de réponse resterait relativement identique. Même avec 1 million de produits, la recherche d'articles par product_id reste très performante car elle utilise la clé primaire de la table Product, qui est très efficace selon mes recherches. Et grâce à l'optimisation n+1 rajoutée, une requête récupère tout les prix d'un coup.

> 💡 Question 6 : Sur l'onglet Statistics, comparez les résultats actuels avec les résultats du test de charge précédent. Est-ce que vous voyez quelques différences significatives dans les métriques pour les endpoints POST /orders, GET /orders/reports/highest-spenders et GET /orders/reports/best-sellers ? Dans quelle mesure la performance s'est-elle améliorée ou détériorée (par exemple, en pourcentage)?

Énorme amélioration pour les GET (0% failure rate) et temps de réponse divisé par 5. Mais pour les POSTS seulement, aucune amélioration notable.

![5](./docs/img_rapport/5.png)

> 💡 Question 7 : La génération de rapports repose désormais entièrement sur des requêtes adressées à Redis, ce qui réduit la charge pesant sur MySQL. Cependant, le point de terminaison POST /orders reste à la traîne par rapport aux autres en termes de performances dans notre scénario de test. Alors, qu'est-ce qui limite les performances de l'endpoint POST /orders ?

La performance de POST /orders est limitée par les opérations d'écriture MySQL (il n'est pas sur REDIS) nécessaires pour garantir la persistance des données et la gestion des stocks. Contrairement aux rapports qui lisent un cache pre-calculated dans Redis, chaque commande doit valider et enregistrer plusieurs entries dnas l BD, etant limité par les ressources disques et le serveur MySQL.

> 💡 Question 8 : Sur l'onglet Statistics, comparez les résultats actuels avec les résultats du test de charge précédent. Est-ce que vous voyez quelques différences significatives dans les métriques pour les endpoints POST /orders, GET /orders/reports/highest-spenders et GET /orders/reports/best-sellers ? Dans quelle mesure la performance s'est-elle améliorée ou détériorée (par exemple, en pourcentage) ? La réponse dépendra de votre environnement d'exécution (par exemple, vous obtiendrez de meilleures performances en exécutant 2 instances de Store Manager sur 2 machines virtuelles plutôt que sur une seule).

Il y a une nette dégradation des performanes par rapport au test précédent, sauf dans une métrique: la rapidité de réponse des GET. Le taux d'échec, qui était à 35%, est passé à 59%. Les RPS sont passées de 64 à 53.

Ma théorie est que, en étant sur une seule machine, l'effet de balance est contre-productif, car le nombre de coeurs sont limités et les requêtes se partagent toutes les mêmes ressources pour leur exécution. Il n'y a pas de réel load balancing car tout roule sur la même machine. Il y a juste un risque augmenté de collisions.

Je n'ai aucun doute qu'en ayant deux (ou même un cluster) de machines sur lesquelles il est réellement possible de faire du load balancing, même si ces machines étaient significativement plus faibles que mon laptop, les résultats seraient notablement meilleurs, car nginx est optimisée pour cela, par pour tout rouler sur une seule machine.

![6](./docs/img_rapport/6.png)

> 💡 Question 9 : Dans le fichier nginx.conf, il existe un attribut qui configure l'équilibrage de charge. Quelle politique d'équilibrage de charge utilisons-nous actuellement ? Consultez la documentation officielle de Nginx si vous avez des questions.

`least_conn` dans Upstream est le paramètre utilisé. Selon la doc, cette politique distribue de manière intelligente en envoyant les requêtes au serveur qui a le moins de connexions en cours à cet instant.