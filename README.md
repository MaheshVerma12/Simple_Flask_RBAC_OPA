This is a simple project to demonstrate how to implement Open Policy Agent (OPA) based role-based-access-control in a Flask project.
Redis has been used to cache the results of rbac queries to opa so that the expensive calls are not necessary to be made to opa 
frequently and also redis streams has been used so that if any policy changes, then to flush the existing expired cache a message can be
sent to a stream to a consumer group and any one of the consumers in the consumer group can flush the cache of redis db and acknowledge
the message. There is a background thread working as a daemon which is subscribed as a consumer to the consumer group stream of policy 
invalidation.
The api endpoints of this project are ->
(1) http://127.0.0.1:5000/ (GET)
    - Home endpoint 
    - Returns welcome message.

(2) http://127.0.0.1:5000/authorize (POST)
    - RBAC query endpoint 
    - Required payload in json body -> {"user":"", "action":"","resource":""}
    - Results -> {
    "result": true,
    "source": "OPA"
}, {
    "result": true,
    "source": "Redis Cache"
}

(3) If we push message to the policy_updated stream consumer group, then the existing redis cache for the redis namespace is flushed (deleted).

How to run this project via terminal ->
(1) Create a virtual environment -> python -m venv venv
(2) Activate venv -> venv/scripts/activate
(3) Install the requirements in the venv -> pip install -r requirements.txt
(4) Install the developer requirements -> pip install -r dev-requirements.txt
(5) Run the app -> python app.py 
(6) You can test the endpoints in an api client like 
Postman or Insomnia.
