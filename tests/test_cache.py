from types import SimpleNamespace

from nextinspace.cache import Cache


def test_round_trip(tmp_path):
    cache = Cache(tmp_path)
    cache.put("k", {"results": [1, 2]})
    age, data = cache.get("k")
    assert data == {"results": [1, 2]}
    assert age >= 0


def test_age(tmp_path, monkeypatch):
    clock = SimpleNamespace(time=lambda: 1000.0)
    monkeypatch.setattr("nextinspace.cache.time", clock)
    cache = Cache(tmp_path)
    cache.put("k", [])
    clock.time = lambda: 1250.0
    assert cache.get("k") == (250.0, [])


def test_keys_are_distinct(tmp_path):
    cache = Cache(tmp_path)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a")[1] == 1
    assert cache.get("b")[1] == 2


def test_missing_key(tmp_path):
    assert Cache(tmp_path).get("nope") is None
    assert Cache(tmp_path / "does-not-exist").get("nope") is None


def test_corrupt_response(tmp_path):
    cache = Cache(tmp_path)
    cache.put("k", {"a": 1})
    (path,) = (tmp_path / "responses").iterdir()
    path.write_text('{"fetched_at": 1, "da')
    assert cache.get("k") is None


def test_no_temp_files_left(tmp_path):
    cache = Cache(tmp_path)
    cache.put("k", 1)
    cache.save_listing([])
    assert not list(tmp_path.rglob("*.tmp"))


def test_listing_round_trip(tmp_path):
    cache = Cache(tmp_path)
    assert cache.load_listing() == []
    refs = [{"kind": "launch", "id": "abc"}, {"kind": "event", "id": "7"}]
    cache.save_listing(refs)
    assert cache.load_listing() == refs


def test_corrupt_listing(tmp_path):
    (tmp_path / "last_listing.json").write_text("[{")
    assert Cache(tmp_path).load_listing() == []
