# Rest API: manage user authentication
Through this project I built a `REST API` to manage users’ authentication and permissions. Behind the scenes, the authorization system was implemented using the [JWT: Json Web Token] standard (https://jwt.io/introduction).  The API also includes:

- email verification upon account creation
- password reset via email
- permissions system that will depend on the user's status 

<h3 align="left">
  <span>👉 </span>
  <a href="https://rest-api-auth-app.herokuapp.com">Test the API</a>
</h3>
<br>
<p align="center">
  <img src="img/api_graph.png" alt="API flowchart" width="600">
</p>
<br>


## What did I learn?
- **Create a REST API,** using the`Django` framwork. 
- **Design a permissions system,** using the `Json Web Token (JWT)` standard.
- **[PythonOOP](https://github.com/axelearning/REST-authentication-API/tree/master/authentication)**, write clean object oriented code according to some key principles
- **[Test-driven development](https://github.com/axelearning/REST-authentication-API/tree/master/tests/tests_authentication)**, a set of unit tests used for the API development
<br>

## Why this project?
Between November 2020 and June 2021 I co-funded a startup that aimed to simplify course creation and management for teachers. This API portion is one of the building blocks of this project: an educational platform for students and teachers. 
