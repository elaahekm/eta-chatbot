from graph_agent import decide_node


def test_decide_needs_weather_when_asked():
    state = {"question": "What is the weather in Tehran?"}
    result = decide_node(state)
    assert result["need_weather"] is True

def test_decide_no_weather_for_trip_question():
    state = {"question": "How long is a trip from zone 132 to 161?"}
    result = decide_node(state)
    assert result["need_weather"] is False