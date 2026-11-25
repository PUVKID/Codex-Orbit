"""Rust 거리 검증기를 실제 기상 응답 수락 경로에서 호출합니다."""
import ctypes
import math
import sys
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def _distance_function():
    root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
    try:
        library = ctypes.CDLL(str(root / 'assets' / 'orbit_weather_guard.dll'))
        function = library.orbit_weather_distance
        function.argtypes = [ctypes.c_double] * 4
        function.restype = ctypes.c_double
        function._library = library
        return function
    except (OSError, AttributeError) as error:
        raise ValueError('날씨 위치 검증기를 불러올 수 없습니다') from error

def validate_weather_grid(location, data):
    """도시 좌표를 검증하고 제공된 기상 격자가 25km 이내인지 확인합니다."""
    values = [location.get('latitude'), location.get('longitude')]
    # 격자 좌표가 없는 기존 자료도 요청 좌표의 유효성은 Rust로 검증합니다.
    grid = [data.get('latitude', values[0]), data.get('longitude', values[1])]
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values + grid):
        raise ValueError('날씨 위치 좌표 형식')
    distance = _distance_function()(*(values + grid))
    if not 0 <= distance <= 25:
        raise ValueError('요청 지역과 날씨 제공 지역이 다릅니다')
    return distance
