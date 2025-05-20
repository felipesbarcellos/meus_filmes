import sys
import os
import pytest

# Adiciona o diretório pai ao sys.path para importar o app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
import os
import pytest
import json

# Adiciona o diretório pai ao sys.path para importar o app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, db, User

@pytest.fixture
def client():
    # Usa um banco de dados em memória para os testes
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200

def test_register_success(client):
    data = {"name": "Test User", "email": "test@example.com", "password": "123456"}
    response = client.post("/api/register", json=data)
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_register_missing_fields(client):
    data = {"email": "test2@example.com"}
    response = client.post("/api/register", json=data)
    assert response.status_code == 400

def test_register_duplicate_email(client):
    data = {"name": "User1", "email": "dup@example.com", "password": "abc123"}
    client.post("/api/register", json=data)
    response = client.post("/api/register", json=data)
    assert response.status_code == 409

def test_login_success(client):
    # Primeiro registra o usuário
    reg_data = {"name": "Login User", "email": "login@example.com", "password": "pass123"}
    client.post("/api/register", json=reg_data)
    login_data = {"email": "login@example.com", "password": "pass123"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_login_invalid_credentials(client):
    login_data = {"email": "notfound@example.com", "password": "wrong"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 401

def test_login_missing_fields(client):
    response = client.post("/api/login", json={"email": "a@b.com"})
    assert response.status_code == 400

def test_recovery_success(client):
    # Registra usuário para testar recovery
    reg_data = {"name": "Recovery User", "email": "recovery@example.com", "password": "pass123"}
    client.post("/api/register", json=reg_data)
    response = client.post("/api/recovery", json={"email": "recovery@example.com"})
    assert response.status_code == 200
    assert "Recovery instructions sent to email" in response.get_json()["msg"]

def test_recovery_missing_email(client):
    response = client.post("/api/recovery", json={})
    assert response.status_code == 400

def test_recovery_email_not_found(client):
    response = client.post("/api/recovery", json={"email": "notfound@example.com"})
    assert response.status_code == 404
