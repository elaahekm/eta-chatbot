from tools import get_weather


def test_get_weather_returns_string():
    result = get_weather("Tehran")
    assert isinstance(result, str)

def test_get_weather_has_city_name():
    result = get_weather("Tehran")
    assert "Tehran" in result