import pytest
# from test.unit.webapp import client
from main import app

@pytest.fixture()
def test_app():
    app.config.update({
        "TESTING": True,
    })

    yield app

@pytest.fixture()
def client(test_app):
    return test_app.test_client()

def test_home_page(client):
    response = client.get("/")
    assert b"Welcome" in response.data

def test_login_page(client):
    response = client.get("/login")
    assert b"Login Page" in response.data

def test_login_with_invalid_credentials(client):
    response = client.post("/login", data={
        "email": "sampleCustomer@samplet.com",
        "password": "wrong_pswd"
    })
    assert response.status_code == 200

def test_logout(client):
    response = client.get("/logout")
    assert b"Redirecting..." in response.data

def test_add_item_page(client):
    response = client.get("/addItem")
    assert b"Add Items" in response.data

def test_cart_page(client):
    response = client.get("/cart")
    assert response.status_code == 302
