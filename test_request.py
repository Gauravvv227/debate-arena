import requests

response = requests.post(
    "http://127.0.0.1:5000/api/argument",
    json={
        "topic": "Should homework be banned",
        "side": "for",
        "round": 1,
        "history": []
    },
    stream=True
)

print(response.status_code)
for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))