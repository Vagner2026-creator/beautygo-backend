from app.models.state import State
from app.models.city import City


def _seed(db):
    state = State(name="São Paulo", uf="SP")
    db.add(state)
    db.flush()
    city = City(name="Campinas", state_id=state.id)
    db.add(city)
    db.commit()
    db.refresh(state)
    db.refresh(city)
    return state, city


def test_list_states_empty(client):
    r = client.get("/api/v1/locations/states")
    assert r.status_code == 200
    assert r.json() == []


def test_list_states(client, db):
    _seed(db)
    r = client.get("/api/v1/locations/states")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["uf"] == "SP"


def test_list_cities_by_state(client, db):
    state, city = _seed(db)
    r = client.get(f"/api/v1/locations/states/{state.id}/cities")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "Campinas"


def test_list_cities_invalid_state(client):
    # Estado inexistente retorna 404
    r = client.get("/api/v1/locations/states/99999/cities")
    assert r.status_code == 404


def test_search_cities(client, db):
    _seed(db)
    # Parâmetro correto é ?name= (não ?q=)
    r = client.get("/api/v1/locations/cities/search?name=Camp")
    assert r.status_code == 200
    assert any(c["name"] == "Campinas" for c in r.json())


def test_search_cities_no_results(client):
    r = client.get("/api/v1/locations/cities/search?name=XYZinexistente")
    assert r.status_code == 200
    assert r.json() == []


def test_get_city_by_id(client, db):
    _, city = _seed(db)
    r = client.get(f"/api/v1/locations/cities/{city.id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Campinas"


def test_get_city_invalid_id(client):
    r = client.get("/api/v1/locations/cities/99999")
    assert r.status_code == 404
