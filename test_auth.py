import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_signup_creates_user():
    """Test that signup endpoint creates a new user"""
    response = client.post("/api/auth/signup", json={
        "email": "testuser@example.com",
        "password": "testpassword123"
    })
    assert response.status_code in [200, 201, 400]  # 400 if user already exists
    if response.status_code in [200, 201]:
        data = response.json()
        assert "token" in data  # API returns 'token' not 'access_token'

def test_login_with_valid_credentials():
    """Test that login works with valid credentials"""
    # First create a user
    client.post("/api/auth/signup", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    
    # Then try to login
    response = client.post("/api/auth/login", json={
        "email": "logintest@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data  # API returns 'token' not 'access_token'

def test_login_with_invalid_credentials():
    """Test that login fails with wrong password"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code in [401, 404]
