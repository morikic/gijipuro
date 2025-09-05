# tests/test_search_result.py
from components.search_result import filter_results_by_type

def test_filter_by_track_name():
    """曲名で正しくフィルタリングされるかテスト"""
    results = [
        {"trackName": "Superstar", "artistName": "Artist A"},
        {"trackName": "Star Light", "artistName": "Artist B"},
    ]
    filtered = filter_results_by_type(results, "star", "曲名")
    assert len(filtered) == 2 # 2件ともヒットするはず

    filtered_super = filter_results_by_type(results, "super", "曲名")
    assert len(filtered_super) == 1
    assert filtered_super[0]["trackName"] == "Superstar"