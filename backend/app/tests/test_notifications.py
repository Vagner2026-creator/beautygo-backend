from app.models.notification import Notification
from app.tests.conftest import register_and_login, auth_header


def _create_notification(db, user_id, title="Teste", message="Mensagem", notif_type="test"):
    notif = Notification(user_id=user_id, title=title, message=message, type=notif_type)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def _get_user_id(client_fixture, token):
    return client_fixture.get("/api/v1/auth/me", headers=auth_header(token)).json()["id"]


def test_list_notifications_empty(client):
    token = register_and_login(client, "user@notif.com")
    r = client.get("/api/v1/notifications/", headers=auth_header(token))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_notifications_with_data(client, db):
    token = register_and_login(client, "user2@notif.com")
    user_id = _get_user_id(client, token)

    _create_notification(db, user_id, title="Agendamento", message="Você tem um agendamento")
    _create_notification(db, user_id, title="Confirmação", message="Confirmado!")

    r = client.get("/api/v1/notifications/", headers=auth_header(token))
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_list_notifications_requires_auth(client):
    r = client.get("/api/v1/notifications/")
    assert r.status_code == 401


def test_mark_notification_read(client, db):
    token = register_and_login(client, "user3@notif.com")
    user_id = _get_user_id(client, token)

    notif = _create_notification(db, user_id, title="Nova notificação", message="Olá")
    assert notif.read_at is None

    r = client.patch(f"/api/v1/notifications/{notif.id}/read", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["read_at"] is not None


def test_mark_notification_read_wrong_user(client, db):
    token1 = register_and_login(client, "user4@notif.com")
    user_id1 = _get_user_id(client, token1)

    token2 = register_and_login(client, "user5@notif.com")

    notif = _create_notification(db, user_id1, title="Privado", message="Só do user1")

    r = client.patch(f"/api/v1/notifications/{notif.id}/read", headers=auth_header(token2))
    assert r.status_code == 403


def test_mark_all_read(client, db):
    token = register_and_login(client, "user6@notif.com")
    user_id = _get_user_id(client, token)

    _create_notification(db, user_id, title="N1", message="M1")
    _create_notification(db, user_id, title="N2", message="M2")
    _create_notification(db, user_id, title="N3", message="M3")

    r = client.patch("/api/v1/notifications/read-all", headers=auth_header(token))
    assert r.status_code == 200

    r = client.get("/api/v1/notifications/", headers=auth_header(token))
    for item in r.json()["items"]:
        assert item["read_at"] is not None
