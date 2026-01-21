from flask import Flask,  request, jsonify
from config import Config
import json 
import threading 
import time 
import requests
import redis 


app=Flask(__name__)

app.config.from_object(Config) 

redis_client=redis.Redis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    decode_responses=True
)

#Helper Functions
def cache_key(user,action,resource):
    return f"auth:{user}:{action}:{resource}"

def query_opa(user,action,resource):
    opa_url=app.config["OPA_URL"]
    query={
        "input":{
            "user":user,
            "action":action,
            "resource":resource 
        }
    }
    try:
        response=requests.post(opa_url,json=query)
        data=response.json()
    except Exception as e:
        data={"result":True} 
    return data.get("result",False) 

#API Endpoints
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message":"Be happy."}), 200 

#API endpoint to return the authorization query first check Redis Cache and if not found then query opa.
@app.route("/authorize", methods=["POST"])
def authorize():
    body=request.json
    user=body.get("user")
    action=body.get("action")
    resource=body.get("resource")
    
    cache_key_value=cache_key(user,action,resource)

    cached_result=redis_client.get(cache_key_value)
    if cached_result:
        return jsonify(
            {
                "result":json.loads(cached_result),
                "source":"Redis Cache"
            }
        ), 200
    try:
        opa_result=query_opa(user,action,resource)
        redis_client.setex(
            cache_key_value,
            app.config["AUTH_INVALIDATION_TIME"],
            json.dumps(opa_result) 
        )
        return jsonify(
            {
                "result":opa_result,
                "source":"OPA" 
            }
        ), 200

    except Exception as e:
        return jsonify({"error":str(e)}), 500
    
#STREAM CONSUMER (BACKGROUND)
def listen_with_consumer_group():
    while True:
        try:
            events=redis_client.xreadgroup(
                groupname=app.config["CONSUMER_GROUP"],
                consumername=app.config["CONSUMER_NAME"],
                streams={app.config["STREAM_NAME"]:">"},
                block=5000,
                count=10
            )

            if not events:
                continue

            first_stream_item=events[0]
            stream=first_stream_item[0]
            messages=first_stream_item[1]

            for msg_id, message_data in messages:
                print(f"Message received from stream {stream}: {message_data}")
                redis_client.flushdb()
                redis_client.xack(
                    app.config["STREAM_NAME"],
                    app.config["CONSUMER_GROUP"],
                    msg_id
                )

        except Exception as e:
            print(f"Error in consumer group: {e}")
            time.sleep(2)

#Start the background listener daemon. 
threading.Thread(
    target=listen_with_consumer_group,
    daemon=True
).start() 
        

if __name__=="__main__":
    app.run(debug=True) 
