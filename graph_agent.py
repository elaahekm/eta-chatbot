from typing import Literal, TypedDict

import ollama
import requests
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from tools import get_weather


class State(TypedDict):
    question: str
    params: dict | None
    eta: float | None
    answer: str | None
    weather: str | None
    need_weather: bool | None


class Trip(BaseModel):
    pickup_zone: int
    dropoff_zone: int
    hour: int
    day_of_week: Literal["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]


def extract_node(state: State) -> dict:
    print("Step 1: Extracting parameters")
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": state["question"]}],
        format=Trip.model_json_schema(),
    )
    trip = Trip.model_validate_json(response.message.content)
    return {"params": trip.model_dump()}




def predict_node(state: State) -> dict:
    print("Step 2: Calling the API")
    p = state["params"]
    days = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6}
    r = requests.post(
        "http://localhost:8000/predict_eta",
        json={
            "pickup_zone": p["pickup_zone"],
            "dropoff_zone": p["dropoff_zone"],
            "hour": p["hour"],
            "day_of_week": days[p["day_of_week"]],
        },
    )
    return {"eta": r.json()["estimated_time_minutes"]}




def answer_node(state: State) -> dict:
    print("Step 3: Building the final answer")
    p = state["params"]
    text = (
        f"From zone {p['pickup_zone']} to zone {p['dropoff_zone']} "
        f"at {p['hour']}:00 on {p['day_of_week']}. "
        f"{(' Weather: ' + state['weather']) if state.get('weather') else ''}"
    )
    return {"answer": text}

def decide_node(state: State) -> dict:
    print("Step: Deciding")
    q = state["question"].lower()
    return {"need_weather": "weather" in q or "هوا" in q}

def weather_node(state: State) -> dict:
    print("Step: Getting weather")
    return {"weather": get_weather("Tehran")}


builder = StateGraph(State)
builder.add_node("extract", extract_node)
builder.add_node("predict", predict_node)
builder.add_node("answer", answer_node)
builder.add_node("weather", weather_node)
builder.add_node("decide", decide_node)

builder.add_edge(START, "extract")
builder.add_edge("extract", "decide")
builder.add_conditional_edges(
    "decide",
    lambda s: "weather" if s["need_weather"] else "predict",
)
builder.add_edge("weather", "predict")
builder.add_edge("predict", "answer")
builder.add_edge("answer", END)

graph = builder.compile()



if __name__ == "__main__":
    result = graph.invoke({"question": "taxi from zone 132 to zone 161 on Saturday at 8am, what is the weather?"})
    print(result["answer"])