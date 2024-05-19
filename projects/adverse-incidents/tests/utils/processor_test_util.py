def generate_random_incident(fake):
    latitude_from = fake.pyfloat(min_value=-80, max_value=80)
    latitude_to = fake.pyfloat(min_value=latitude_from, max_value=90)
    longitude_from = fake.pyfloat(min_value=-170, max_value=170)
    longitude_to = fake.pyfloat(min_value=longitude_from, max_value=180)
    return {
        "description": fake.text(),
        "bounding_box": {"latitude_from": latitude_from, "latitude_to": latitude_to, "longitude_from": longitude_from, "longitude_to": longitude_to},
    }


# Generates 3 random incidents
def generate_random_incidents(fake):
    latitude_per_incident = 90 / 3
    longitude_per_incident = 180 / 3

    incidents = []

    for i in range(3):
        incidents.append(
            {
                "description": fake.text(),
                "bounding_box": {
                    "latitude_from": i * latitude_per_incident,
                    "latitude_to": (i + 1) * latitude_per_incident,
                    "longitude_from": i * longitude_per_incident,
                    "longitude_to": (i + 1) * longitude_per_incident,
                },
            },
        )

    return incidents


def generate_random_users_training(fake, incidents, users_per_incident: int):
    users_training = []
    for incident in incidents:
        for _ in range(users_per_incident):
            latitude = fake.pyfloat(min_value=incident["bounding_box"]["latitude_from"], max_value=incident["bounding_box"]["latitude_to"])
            longitude = fake.pyfloat(min_value=incident["bounding_box"]["longitude_from"], max_value=incident["bounding_box"]["longitude_to"])
            users_training.append({"user_id": fake.uuid4(), "latitude": latitude, "longitude": longitude})

    return users_training
