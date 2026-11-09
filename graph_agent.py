import requests
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    question: str
    params: Optional[dict]
    eta: Optional[float]
    answer: Optional[str]



def extract_node(state: State) -> dict:
    print("مرحله ۱: استخراج پارامترها")
    return {"params": {"zone": "Midtown", "hour": 18, "weekday": 4}}    




def predict_node(state: State) -> dict:
    print("مرحله ۲: صدا زدن API")
    r = requests.post(
        "http://localhost:8000/predict_eta",
        json={"pickup_zone": 161, "dropoff_zone": 236, "hour": 18, "day_of_week": 4},
    )
    return {"eta": r.json()["estimated_time_minutes"]}




def answer_node(state: State) -> dict:
    print("مرحله ۳: ساختن جواب نهایی")
    p = state["params"]
    text = f"زمان رسیدن از {p['zone']} ساعت {p['hour']} حدود {state['eta']} دقیقه است."
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
    result = graph.invoke({"question": "ETA from Midtown at 6pm Friday?"})
    print(result["answer"])