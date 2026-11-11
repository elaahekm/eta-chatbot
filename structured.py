from typing import Literal

import ollama
from pydantic import BaseModel


class Trip(BaseModel):
    pickup_zone: int
    dropoff_zone: int
    hour: int
    day_of_week: Literal["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

question = "taxi from zone 132 to zone 161 on Saturday at 8am"

response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": question}],
    format=Trip.model_json_schema(),
)

trip = Trip.model_validate_json(response.message.content)
print(trip)

import requests

DAYS = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6}

r = requests.post(
    "http://127.0.0.1:8000/predict_eta",
    json={
        "pickup_zone": trip.pickup_zone,
        "dropoff_zone": trip.dropoff_zone,
        "hour": trip.hour,
        "day_of_week": DAYS[trip.day_of_week],
    },
    timeout=10,
)
result = r.json()
print(f"Result: {result['estimated_time_minutes']} min, {result['distance_km']} km")