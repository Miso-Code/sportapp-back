import faker
import pytest
from fastapi.testclient import TestClient

from app.config.settings import Config
from app.utils import faker_utils
from main import app


class Constants:
    ADVERSE_INCIDENTS_PROVIDER_BASE_PATH = "/incidents"
    APPLICATION_JSON = "application/json"


fake = faker.Faker()

client = TestClient(app)
client.headers = {"X-API-Key": "secret"}


@pytest.fixture
def mock_get_all_incidents_titles():
    fake.add_provider(faker_utils.AdverseIncidentFakerProvider)
    all_incidents = fake.all_adverse_incidents()
    all_incidents_messages = [f"{incident['name']}: {incident['description']}" for incident in all_incidents]
    return all_incidents_messages


def test_generate_incidents(mock_get_all_incidents_titles):
    Config.MAX_ADVERSE_INCIDENTS = 1
    response = client.post(f"{Constants.ADVERSE_INCIDENTS_PROVIDER_BASE_PATH}/")
    response_json = response.json()

    assert response.status_code == 200
    assert response.headers["content-type"] == Constants.APPLICATION_JSON
    print(response_json)
    assert len(response_json) == 1
    assert "description" in response_json[0]
    assert "bounding_box" in response_json[0]
    assert "latitude_from" in response_json[0]["bounding_box"]
    assert "longitude_from" in response_json[0]["bounding_box"]
    assert "latitude_to" in response_json[0]["bounding_box"]
    assert "longitude_to" in response_json[0]["bounding_box"]
    assert response_json[0]["bounding_box"]["latitude_from"] <= response_json[0]["bounding_box"]["latitude_to"]
    assert response_json[0]["bounding_box"]["longitude_from"] <= response_json[0]["bounding_box"]["longitude_to"]
    assert response_json[0]["bounding_box"]["latitude_from"] >= -90
    assert response_json[0]["bounding_box"]["latitude_to"] <= 90
    assert response_json[0]["bounding_box"]["longitude_from"] >= -180
    assert response_json[0]["bounding_box"]["longitude_to"] <= 180
    assert response_json[0]["description"] in mock_get_all_incidents_titles
