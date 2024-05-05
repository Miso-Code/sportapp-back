from app.models.model import WeekDay, FoodType, Dish, FoodCategory, FoodTrainingObjective


def generate_random_training_plan_data(fake):
    return [
        {
            "weekday": WeekDay.MONDAY.value,
            "warm_up": fake.pyfloat(min_value=0.1, max_value=1),
            "cardio": fake.pyfloat(min_value=0.1, max_value=1),
            "strength": fake.pyfloat(min_value=0.1, max_value=1),
            "cool_down": fake.pyfloat(min_value=0.1, max_value=1),
        },
        {
            "weekday": WeekDay.WEDNESDAY.value,
            "warm_up": fake.pyfloat(min_value=0.1, max_value=1),
            "cardio": fake.pyfloat(min_value=0.1, max_value=1),
            "strength": fake.pyfloat(min_value=0.1, max_value=1),
            "cool_down": fake.pyfloat(min_value=0.1, max_value=1),
        },
        {
            "weekday": WeekDay.FRIDAY.value,
            "warm_up": fake.pyfloat(min_value=0.1, max_value=1),
            "cardio": fake.pyfloat(min_value=0.1, max_value=1),
            "strength": fake.pyfloat(min_value=0.1, max_value=1),
            "cool_down": fake.pyfloat(min_value=0.1, max_value=1),
        },
    ]


def generate_random_dishes_data(fake, food_type: FoodType, objective: FoodTrainingObjective):
    return [
        Dish(
            name=fake.word(),
            name_es=fake.word(),
            category=FoodCategory.BREAKFAST,
            calories=fake.random_int(min=100, max=500),
            protein=fake.random_int(min=5, max=30),
            carbs=fake.random_int(min=5, max=30),
            fat=fake.random_int(min=5, max=30),
            food_type=food_type,
            objective=objective,
        ),
        Dish(
            name=fake.word(),
            name_es=fake.word(),
            category=FoodCategory.LUNCH,
            calories=fake.random_int(min=100, max=500),
            protein=fake.random_int(min=5, max=30),
            carbs=fake.random_int(min=5, max=30),
            fat=fake.random_int(min=5, max=30),
            food_type=food_type,
            objective=objective,
        ),
        Dish(
            name=fake.word(),
            name_es=fake.word(),
            category=FoodCategory.DINNER,
            calories=fake.random_int(min=100, max=500),
            protein=fake.random_int(min=5, max=30),
            carbs=fake.random_int(min=5, max=30),
            fat=fake.random_int(min=5, max=30),
            food_type=food_type,
            objective=objective,
        ),
        Dish(
            name=fake.word(),
            name_es=fake.word(),
            category=FoodCategory.SNACK,
            calories=fake.random_int(min=100, max=500),
            protein=fake.random_int(min=5, max=30),
            carbs=fake.random_int(min=5, max=30),
            fat=fake.random_int(min=5, max=30),
            food_type=food_type,
            objective=objective,
        ),
        Dish(
            name=fake.word(),
            name_es=fake.word(),
            category=FoodCategory.RECOVERY_SNACK,
            calories=fake.random_int(min=100, max=500),
            protein=fake.random_int(min=5, max=30),
            carbs=fake.random_int(min=5, max=30),
            fat=fake.random_int(min=5, max=30),
            food_type=food_type,
            objective=objective,
        ),
    ]
