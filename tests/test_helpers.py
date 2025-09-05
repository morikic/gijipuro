# tests/test_helpers.py
import pytest
from utils.helpers import sort_results

# テスト用のダミーデータ
@pytest.fixture
def sample_songs():
    return [
        {"trackName": "あいうえお"},
        {"trackName": "かきくけこ"},
        {"trackName": "ABC"},
        {"trackName": "XYZ"},
    ]

def test_sort_50on_asc(sample_songs):
    """50音順・昇順で正しくソートされるかテスト"""
    sorted_list = sort_results(sample_songs, sort_mode="50音", order="昇順")
    # 曲名のリストだけを抽出
    names = [s["trackName"] for s in sorted_list]
    # 「あいうえお」が「かきくけこ」より前に、「ABC」が「XYZ」より前に来ることを期待
    assert names == ["あいうえお", "かきくけこ", "ABC", "XYZ"]

def test_sort_alpha_desc(sample_songs):
    """アルファベット順・降順で正しくソートされるかテスト"""
    sorted_list = sort_results(sample_songs, sort_mode="アルファベット", order="降順")
    names = [s["trackName"] for s in sorted_list]
    assert names == ["XYZ", "かきくけこ", "ABC", "あいうえお"]