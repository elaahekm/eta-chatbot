import json
import requests
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

@tool
def predict_eta(pickup_zone: int, dropoff_zone: int, hour: int, day_name: str) -> dict:
    """Predict taxi trip time. day_name: English weekday name like Friday."""
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_of_week = days.index(day_name.strip().lower())
    r = requests.post(
        "http://127.0.0.1:8000/predict_eta",
        json={"pickup_zone": pickup_zone, "dropoff_zone": dropoff_zone,
              "hour": hour, "day_of_week": day_of_week},
    )
    return r.json()

llm = ChatOllama(model="llama3.2:3b")
agent = create_agent(llm, tools=[predict_eta])

result = agent.invoke({"messages": [("user", "taxi from zone 161 to 237 at 6pm Friday, how long?")]})

for m in result["messages"]:
    if m.type == "tool":
        data = json.loads(m.content)
        print(f"ETA: {data['estimated_time_minutes']} minutes, distance: {data['distance_km']} km")