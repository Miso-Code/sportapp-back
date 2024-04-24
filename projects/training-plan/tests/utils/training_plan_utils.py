from app.models.schemas.schema import TrainingPlanCreate, TrainingObjective
from app.models.training_plan import TrainingPlanSession


def generate_random_training_plan_create_data(faker):
    training_plan_data = generate_random_training_plan_create_data_dict(faker)
    return TrainingPlanCreate(**training_plan_data)


def generate_random_training_plan_create_data_dict(faker):
    training_objective = faker.random.choice(list(TrainingObjective))
    available_weekdays = list({faker.day_of_week().lower(), faker.day_of_week().lower(), faker.day_of_week().lower()})
    preferred_training_start_time = faker.time(pattern="%I:%M %p")
    available_training_hours = faker.random_int(min=1, max=10)

    training_plan_data = {
        "training_objective": training_objective,
        "available_weekdays": available_weekdays,
        "preferred_training_start_time": preferred_training_start_time,
        "available_training_hours": available_training_hours,
    }

    return training_plan_data


def generate_random_training_plan_session(faker):
    return TrainingPlanSession(**generate_random_training_plan_session_dict(faker))


def generate_random_training_plan_session_dict(faker):
    return {
        "weekday": faker.day_of_week().lower(),
        "start_time": faker.time(pattern="%I:%M %p"),
        "warm_up": faker.random_int(min=1, max=60),
        "cardio": faker.random_int(min=1, max=60),
        "strength": faker.random_int(min=1, max=60),
        "cool_down": faker.random_int(min=1, max=60),
        "user_id": str(faker.uuid4()),
    }
