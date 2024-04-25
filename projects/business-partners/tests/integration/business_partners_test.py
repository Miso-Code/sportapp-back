import faker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from http import HTTPStatus

from app.config.settings import Config
from app.models.business_partners import ProductCategory, PaymentType, PaymentFrequency
from main import app
from app.config.db import base, get_db
from tests.utils.business_partners_util import generate_random_business_partner_create_data, generate_random_product_purchase


class Constants:
    BUSINESS_PARTNERS_BASE_PATH = "/business-partners"
    APPLICATION_JSON = "application/json"


fake = faker.Faker()

# use an in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

base.metadata.create_all(bind=test_engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture()
def test_db():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


def test_create_business_partner(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)
    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response_json["business_partner_name"] == business_partner_create.business_partner_name
    assert response_json["email"] == business_partner_create.email
    assert response_json["business_partner_id"] is not None
    assert "hashed_password" not in response_json


def test_create_business_partner_with_existing_email(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_repeated_create_dict = {"business_partner_name": fake.company(), "email": business_partner_create.email, "password": fake.password()}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_repeated_create_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response_json["message"] == "Business partner with this email already exists"


def test_login_business_partner(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    login_business_partner_dict = {"email": business_partner_create.email, "password": business_partner_create.password}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/login", json=login_business_partner_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert Constants.APPLICATION_JSON in response.headers["content-type"]
    assert response_json["access_token"] is not None
    assert response_json["access_token_expires_minutes"] is not None
    assert response_json["access_token_expires_minutes"] == Config.ACCESS_TOKEN_EXPIRE_MINUTES
    assert response_json["refresh_token"] is not None
    assert response_json["refresh_token_expires_minutes"] is not None
    assert response_json["refresh_token_expires_minutes"] == Config.REFRESH_TOKEN_EXPIRE_MINUTES


def test_login_business_partner_with_incorrect_password(test_db):
    login_business_partner_dict = {"email": fake.email(), "password": fake.password()}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/login", json=login_business_partner_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_json["message"] == "Invalid email or password"


def test_create_business_partner_product(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    assert response.status_code == HTTPStatus.CREATED


def test_create_business_partner_product_business_partner_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    product_data = {
        "product_id": fake.uuid4(),
        "business_partner_id": fake.uuid4(),
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    business_partner_id = fake.uuid4()

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Business partner with id {business_partner_id} not found"


def test_get_business_partner_products(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = [
        {
            "category": fake.enum(ProductCategory).value,
            "name": fake.word(),
            "summary": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType).value,
            "payment_frequency": fake.enum(PaymentFrequency).value,
            "image_url": fake.url(),
            "description": fake.text(),
        }
        for _ in range(3)
    ]

    for product in product_data:
        response = client.post(
            f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
            json=product,
            headers={"user-id": business_partner_id},
        )

        assert response.status_code == HTTPStatus.CREATED

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        headers={"user-id": business_partner_id},
    )
    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_json) == 3
    for i, product in enumerate(response_json):
        assert "product_id" in response_json[i]
        assert response_json[i]["business_partner_id"] == product["business_partner_id"]
        assert response_json[i]["category"] == product["category"]
        assert response_json[i]["name"] == product["name"]
        assert response_json[i]["url"] == product["url"]
        assert response_json[i]["price"] == product["price"]
        assert response_json[i]["payment_type"] == product["payment_type"]
        assert response_json[i]["payment_frequency"] == product["payment_frequency"]
        assert response_json[i]["image_url"] == product["image_url"]
        assert response_json[i]["description"] == product["description"]


def test_get_business_partner_products_business_partner_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = [
        {
            "category": fake.enum(ProductCategory).value,
            "name": fake.word(),
            "summary": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType).value,
            "payment_frequency": fake.enum(PaymentFrequency).value,
            "image_url": fake.url(),
            "description": fake.text(),
        }
        for _ in range(3)
    ]

    for product in product_data:
        response = client.post(
            f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
            json=product,
            headers={"user-id": business_partner_id},
        )

        assert response.status_code == HTTPStatus.CREATED

    fake_business_partner = fake.uuid4()

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        headers={"user-id": fake_business_partner},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Business partner with id {fake_business_partner} not found"


def test_update_business_partner_product(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    updated_product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.patch(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        json=updated_product_data,
        headers={"user-id": business_partner_id},
    )

    assert response.status_code == HTTPStatus.OK


def test_update_business_partner_product_product_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    assert response.status_code == HTTPStatus.CREATED

    product_id = fake.uuid4()

    updated_product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.patch(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        json=updated_product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Product with id {product_id} not found"


def test_update_business_partner_product_partner_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    business_partner_id_fake = fake.uuid4()

    response = client.delete(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        headers={"user-id": business_partner_id_fake},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Business partner with id {business_partner_id_fake} not found"


def test_get_business_partner_product(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_json["product_id"] == product_id
    assert response_json["business_partner_id"] == business_partner_id
    assert response_json["category"] == product_data["category"]
    assert response_json["name"] == product_data["name"]
    assert response_json["url"] == product_data["url"]
    assert response_json["price"] == product_data["price"]
    assert response_json["payment_type"] == product_data["payment_type"]
    assert response_json["payment_frequency"] == product_data["payment_frequency"]
    assert response_json["image_url"] == product_data["image_url"]
    assert response_json["description"] == product_data["description"]


def test_get_business_partner_product_product_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_id = fake.uuid4()

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Product with id {product_id} not found"


def test_get_business_partner_product_partner_not_found(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    business_partner_id_fake = fake.uuid4()

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        headers={"user-id": business_partner_id_fake},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response_json["message"] == f"Business partner with id {business_partner_id_fake} not found"


def test_delete_business_partner_product(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    response = client.delete(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}",
        headers={"user-id": business_partner_id},
    )

    assert response.status_code == HTTPStatus.OK


def test_get_offered_business_partners_products(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    print(response.json())

    business_partner_id = response.json()["business_partner_id"]

    product_data = [
        {
            "category": fake.enum(ProductCategory).value,
            "name": fake.word(),
            "summary": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType).value,
            "payment_frequency": fake.enum(PaymentFrequency).value,
            "image_url": fake.url(),
            "description": fake.text(),
        }
        for _ in range(3)
    ]

    product_data[0]["active"] = False

    for product in product_data:
        response = client.post(
            f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
            json=product,
            headers={"user-id": business_partner_id},
        )

        assert response.status_code == HTTPStatus.CREATED

    response = client.get(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/available")

    response_json = response.json()

    print(response_json)

    assert response.status_code == HTTPStatus.OK
    assert len(response_json) == 2
    for i, product in enumerate(response_json):
        assert "product_id" in response_json[i]
        assert response_json[i]["business_partner_id"] == product["business_partner_id"]
        assert response_json[i]["category"] == product["category"]
        assert response_json[i]["name"] == product["name"]
        assert response_json[i]["url"] == product["url"]
        assert response_json[i]["price"] == product["price"]
        assert response_json[i]["payment_type"] == product["payment_type"]
        assert response_json[i]["payment_frequency"] == product["payment_frequency"]
        assert response_json[i]["image_url"] == product["image_url"]
        assert response_json[i]["description"] == product["description"]
        assert response_json[i]["active"] == product["active"]


def test_get_offered_business_partners_products_with_search(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = [
        {
            "category": fake.enum(ProductCategory).value,
            "name": fake.word(),
            "summary": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType).value,
            "payment_frequency": fake.enum(PaymentFrequency).value,
            "image_url": fake.url(),
            "description": fake.text(),
        }
        for _ in range(3)
    ]

    product_data[0]["name"] = "something"

    for product in product_data:
        response = client.post(
            f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
            json=product,
            headers={"user-id": business_partner_id},
        )

        assert response.status_code == HTTPStatus.CREATED

    search = "SoMeThInG"

    response = client.get(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/available?search={search}")

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_json) == 1
    for i, product in enumerate(response_json):
        assert "product_id" in response_json[i]
        assert response_json[i]["business_partner_id"] == product["business_partner_id"]
        assert response_json[i]["category"] == product["category"]
        assert response_json[i]["name"] == product["name"]
        assert response_json[i]["url"] == product["url"]
        assert response_json[i]["price"] == product["price"]
        assert response_json[i]["payment_type"] == product["payment_type"]
        assert response_json[i]["payment_frequency"] == product["payment_frequency"]
        assert response_json[i]["image_url"] == product["image_url"]
        assert response_json[i]["description"] == product["description"]
        assert response_json[i]["active"] == product["active"]


def test_purchase_product(test_db, mocker):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    purchase_data = generate_random_product_purchase(fake).dict()

    user_id = fake.uuid4()

    mocker.patch("app.services.external.ExternalServices.process_payment", return_value=(True, {}))

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}/purchase",
        json=purchase_data,
        headers={"user-id": user_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_json["transaction_id"] is not None
    assert response_json["transaction_date"] is not None
    assert response_json["transaction_status"] == "completed"
    assert response_json["message"] == "Product purchased successfully"


def test_purchase_product_payment_failed(test_db, mocker):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    purchase_data = generate_random_product_purchase(fake).dict()

    user_id = fake.uuid4()

    mocker.patch("app.services.external.ExternalServices.process_payment", return_value=(False, {"error": "Payment failed"}))

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}/purchase",
        json=purchase_data,
        headers={"user-id": user_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response_json["transaction_id"] is not None
    assert response_json["transaction_date"] is not None
    assert response_json["transaction_status"] == "failed"
    assert response_json["message"] == "Purchasing product failed. Error: Payment failed"


def test_get_business_partner_product_transactions(test_db, mocker):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_id = response.json()["business_partner_id"]

    product_data = {
        "category": fake.enum(ProductCategory).value,
        "name": fake.word(),
        "summary": fake.word(),
        "url": fake.url(),
        "price": fake.random_number(),
        "payment_type": fake.enum(PaymentType).value,
        "payment_frequency": fake.enum(PaymentFrequency).value,
        "image_url": fake.url(),
        "description": fake.text(),
    }

    response = client.post(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products",
        json=product_data,
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.CREATED

    product_id = response_json["product_id"]

    mocker.patch("app.services.external.ExternalServices.process_payment", return_value=(True, {}))

    user_id = fake.uuid4()

    for _ in range(3):
        purchase_data = generate_random_product_purchase(fake).dict()
        response = client.post(
            f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}/purchase",
            json=purchase_data,
            headers={"user-id": user_id},
        )

        assert response.status_code == HTTPStatus.OK

    response = client.get(
        f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/products/{product_id}/purchase",
        headers={"user-id": business_partner_id},
    )

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(response_json) == 3
    for i, transaction in enumerate(response_json):
        assert "product_transaction_id" in response_json[i]
        assert response_json[i]["product_id"] == product_id
        assert response_json[i]["user_id"] == user_id
        assert "user_name" in response_json[i]
        assert "user_email" in response_json[i]
        assert "transaction_date" in response_json[i]
        assert response_json[i]["transaction_status"] == "completed"
        assert "product_data" in response_json[i]
