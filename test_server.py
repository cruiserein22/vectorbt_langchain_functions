import requests
import json

print(
    requests.post(
        "http://0.0.0.0:10000",
        json={
            "query": "what is meta's threads product?"
        }
    ).json()
)
