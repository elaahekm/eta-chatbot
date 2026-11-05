import ollama
import requests

DAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

def predict_eta(pickup_zone, dropoff_zone, hour, day_of_week):
    day = str(day_of_week).strip().lower()
    day = DAYS[day] if day in DAYS else int(day)
    r = requests.post(
        "http://127.0.0.1:8000/predict_eta",
        json={
            "pickup_zone": int(pickup_zone),
            "dropoff_zone": int(dropoff_zone),
            "hour": int(hour),
            "day_of_week": day,
        },
        timeout=10,
    )
    return r.json()

tools = [{
    "type": "function",
    "function": {
        "name": "predict_eta",
        "description": "Predict NYC taxi trip time and distance between two zones",
        "parameters": {
            "type": "object",
            "properties": {
                "pickup_zone": {"type": "integer", "description": "pickup zone ID"},
                "dropoff_zone": {"type": "integer", "description": "dropoff zone ID"},
                "hour": {"type": "integer", "description": "hour of day, 0-23"},
                "day_of_week": {
                    "type": "string",
                    "enum": ["Monday", "Tuesday", "Wednesday", "Thursday",
                             "Friday", "Saturday", "Sunday"],
                    "description": "day name",
                },
            },
            "required": ["pickup_zone", "dropoff_zone", "hour", "day_of_week"],
        },
    },
}]

messages = [{
    "role": "system",
    "content": (
        "You help users estimate NYC taxi trip time. "
        "Use the predict_eta tool with zone IDs (numbers). "
        "Report the minutes and kilometers exactly as the tool returns them. "
        "Do not convert to seconds. Answer briefly."
    ),
}]

while True:
    q = input("You: ")
    if q.strip().lower() in ("exit", "quit"):
        break
    messages.append({"role": "user", "content": q})
    response = ollama.chat(model="llama3.2:3b", messages=messages, tools=tools)
    messages.append(response.message)

    for call in response.message.tool_calls or []:
        result = predict_eta(**call.function.arguments)
        print("DEBUG:", call.function.arguments, result)
        print(f"Result: {result['estimated_time_minutes']} min, {result['distance_km']} km")
        messages.append({
            "role": "tool",
            "tool_name": call.function.name,
            "content": str(result),
        })

    if not response.message.tool_calls:
        print("Bot:", response.message.content)