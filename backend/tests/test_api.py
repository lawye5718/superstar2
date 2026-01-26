"""Test API endpoints"""

import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health check and root endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.1.0"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.1.0"


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login/access-token",
            data={
                "username": test_user.email,
                "password": "testpass123A"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login/access-token",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login/access-token",
            data={
                "username": "nonexistent@example.com",
                "password": "password123A"
            }
        )
        assert response.status_code == 401


class TestUserEndpoints:
    """Test user-related endpoints"""
    
    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "newuser@example.com",
                "password": "Password123A",
                "username": "newuser"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert data["credits"] == 0.0
    
    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating user with duplicate email"""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": test_user.email,
                "password": "Password123A"
            }
        )
        assert response.status_code == 400
    
    def test_create_user_weak_password(self, client):
        """Test creating user with weak password"""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "weakpass@example.com",
                "password": "weak"  # No uppercase, no number
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_current_user(self, client, auth_token):
        """Test getting current user information"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "credits" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401  # Unauthorized - no credentials provided


class TestOrderEndpoints:
    """Test order-related endpoints"""
    
    def test_create_order_missing_template(self, client, auth_token):
        """Test creating order without template_id"""
        response = client.post(
            "/api/v1/orders/",
            json={},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_create_order_invalid_uuid(self, client, auth_token):
        """Test creating order with invalid template UUID"""
        response = client.post(
            "/api/v1/orders/",
            json={"template_id": "not-a-uuid"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_list_orders(self, client, auth_token):
        """Test listing user's orders"""
        response = client.get(
            "/api/v1/orders/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_user_password_validation(self, client):
        """Test password validation rules"""
        # No uppercase
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test1@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422
        
        # No number
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test2@example.com",
                "password": "PasswordABC"
            }
        )
        assert response.status_code == 422
        
        # Too short
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test3@example.com",
                "password": "Pass1"
            }
        )
        assert response.status_code == 422
    
    def test_email_validation(self, client):
        """Test email validation"""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "not-an-email",
                "password": "Password123A"
            }
        )
        assert response.status_code == 422
