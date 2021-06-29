# Rest API avec Django 

à travers ce projet j'ai implémenté un `REST API` qui permet de gérer l'authentification et les permissions des utilisateurs. En coulisse, le système d’autorisation à était mis en oeuvre en utilisant le standard [JWT: Json Web Token](https://jwt.io/introduction).  L'API comprend également:

- une vérification par email lors de la création d'un compte
- une réinitialisation de mot de passe par email
- l'implémentation d'un système de permissions qui dépendra du statut de l'utilisateur 
<br>
<p align="center">
  <img src="img/api_graph.png" alt="organigramme de l'API" width="600">
</p>
<br>


## Qu'est ce que j'ai appris ?

- **Création d'un rest API,** en utilisant le framwork`Django` 
- **Mise en place d'un système de permissions,** à l'aide du standard `Json Web Token (JWT)`
- **Remaniement du code,** en appliquant les méthodes  apprise dans le livre [Clean code](https://www.amazon.fr/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- **Mise en place d'un développement pilotés par les tests**
<br>

## Pourquoi ce projet ?

Entre novembre 2020 et Juin 2021 j'ai co-créé une startup qui avait pour objectif de simplifier la création et la gestions de cours pour les enseignants. Cette portion d'API est l'une des briques de ce projet: une plateforme éducative à destinations des élèves et des professeurs. 
<br>
<br>

<h3 align="right">
  <span>👉 </span>
  <a href="https://rest-api-auth-app.herokuapp.com">tester l'api</a>
</h3>
<br>
