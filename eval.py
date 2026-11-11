from typing import Literal

import ollama
from pydantic import BaseModel


class Trip(BaseModel):
    pickup_zone: int
    dropoff_zone: int
    hour: int
    day_of_week: Literal["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]

TESTS = [
    ("taxi from zone 161 to 237 at 6pm Friday", (161, 237, 18, "Friday")),
    ("zone 132 to zone 161 on Saturday at 8am", (132, 161, 8, "Saturday")),
    ("trip from 48 to 230, Monday 9am", (48, 230, 9, "Monday")),
    ("how long from zone 100 to 200 on Sunday at 11pm", (100, 200, 23, "Sunday")),
    ("zone 90 to zone 140, Wednesday at noon", (90, 140, 12, "Wednesday")),
]

correct = 0
for question, expected in TESTS:
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
    {"role": "system", "content": "pickup_zone اولین مکانی است که در جمله می‌آید و dropoff_zone دومین مکان. day_of_week را دقیقاً به همان شکلی که کاربر نوشته کپی کن، بدون تغییر."},
    {"role": "user", "content": question},
],
        format=Trip.model_json_schema(),
    )
    t = Trip.model_validate_json(response.message.content)
    got = (t.pickup_zone, t.dropoff_zone, t.hour, t.day_of_week)
    ok = got == expected
    correct += ok
    print("OK  " if ok else "FAIL", question, "->", got)

print(f"Score: {correct}/{len(TESTS)}")