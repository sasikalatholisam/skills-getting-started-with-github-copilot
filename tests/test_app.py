"""
Tests for Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create test client
client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that /activities endpoint returns 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_activities_contain_required_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_activities_has_entries(self):
        """Test that activities list is not empty"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_valid_activity(self):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test_student@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_with_invalid_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_duplicate_student(self):
        """Test that duplicate signups are prevented"""
        email = "duplicate_test@mergington.edu"
        activity = "Programming Class"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds participant to activity"""
        email = "new_participant@mergington.edu"
        activity = "Gym Class"
        
        # Get initial count
        response1 = client.get("/activities")
        initial_count = len(response1.json()[activity]["participants"])
        
        # Signup
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Check updated count
        response2 = client.get("/activities")
        new_count = len(response2.json()[activity]["participants"])
        
        assert new_count == initial_count + 1
        assert email in response2.json()[activity]["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""

    def test_remove_valid_participant(self):
        """Test successful removal of a participant"""
        email = "remove_test@mergington.edu"
        activity = "Tennis Club"
        
        # First signup
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Then remove
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_participant(self):
        """Test removal of non-existent participant"""
        response = client.delete(
            "/activities/Chess Club/remove",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_from_invalid_activity(self):
        """Test removal from non-existent activity"""
        response = client.delete(
            "/activities/Invalid Activity/remove",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_decreases_participant_count(self):
        """Test that removal decreases participant count"""
        email = "decrease_test@mergington.edu"
        activity = "Art Studio"
        
        # Signup
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        response1 = client.get("/activities")
        count_before = len(response1.json()[activity]["participants"])
        
        # Remove
        client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        
        response2 = client.get("/activities")
        count_after = len(response2.json()[activity]["participants"])
        
        assert count_after == count_before - 1
        assert email not in response2.json()[activity]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
