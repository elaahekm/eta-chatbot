import requests
import ollama
from typing import TypedDict, Optional, Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    params: Optional[dict]
    eta: Optional[float]
    answer: Optional[str]


class Trip(BaseModel):
    pickup_zone: int
    dropoff_zone: int
    hour: int
    day_of_week: Literal["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]


def extract_node(state: State) -> dict:
    print("مرحله ۱: استخراج پارامترها")
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": state["question"]}],
        format=Trip.model_json_schema(),
    )
    trip = Trip.model_validate_json(response.message.content)
    return {"params": trip.model_dump()}




def predict_node(state: State) -> dict:
    print("مرحله ۲: صدا زدن API")
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
    print("مرحله ۳: ساختن جواب نهایی")
    p = state["params"]
    text = (
        f"از زون {p['pickup_zone']} به زون {p['dropoff_zone']} "
        f"ساعت {p['hour']} روز {p['day_of_week']} "
        f"حدود {state['eta']} دقیقه طول می‌کشه."
    )
    return {"answer": text}




builder = StateGraph(State)
builder.add_node("extract", extract_node)
builder.add_node("predict", predict_node)
builder.add_node("answer", answer_node)

builder.add_edge(START, "extract")
builder.add_edge("extract", "predict")
builder.add_edge("predict", "answer")
builder.add_edge("answer", END)

graph = builder.compile()



if __name__ == "__main__":
    result = graph.invoke({"question": "taxi from zone 132 to zone 161 on Saturday at 8am"})
    print(result["answer"])