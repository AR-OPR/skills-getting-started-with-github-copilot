from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data, dict)
    assert len(response_data) == expected_activity_count
    assert "Chess Club" in response_data


def test_signup_adds_participant_successfully():
    # Arrange
    activity_name = "Chess Club"
    activity_path = activity_name.replace(" ", "%20")
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_path}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    activity_path = activity_name.replace(" ", "%20")
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_path}/signup", params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Club"
    unknown_path = unknown_activity.replace(" ", "%20")

    # Act
    response = client.post(f"/activities/{unknown_path}/signup", params={"email": "test@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_successfully():
    # Arrange
    activity_name = "Chess Club"
    activity_path = activity_name.replace(" ", "%20")
    existing_email = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_path}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from {activity_name}"}
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    activity_path = activity_name.replace(" ", "%20")
    missing_email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_path}/signup", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Club"
    unknown_path = unknown_activity.replace(" ", "%20")

    # Act
    response = client.delete(f"/activities/{unknown_path}/signup", params={"email": "test@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
