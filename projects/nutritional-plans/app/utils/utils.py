from datetime import datetime

from app.models.model import WeekDay, FoodTrainingObjective, Dish, FoodCategory

day_of_the_week_mapping = {0: WeekDay.MONDAY, 1: WeekDay.TUESDAY, 2: WeekDay.WEDNESDAY, 3: WeekDay.THURSDAY, 4: WeekDay.FRIDAY, 5: WeekDay.SATURDAY, 6: WeekDay.SUNDAY}


def get_current_weekday():
    return day_of_the_week_mapping[datetime.now().weekday()]


def calculate_basal_metabolism(age: int, gender: str, weight: float, height: float):
    if gender == "M":
        # Formula for men: BMR = 88.362 + (13.397 * weight in kg) + (4.799 * height in cm) - (5.677 * age in years)
        bmr = 88.362 + (13.397 * weight) + (4.799 * height * 100) - (5.677 * age)
    elif gender == "F":
        # Formula for women: BMR = 447.593 + (9.247 * weight in kg) + (3.098 * height in cm) - (4.330 * age in years)
        bmr = 447.593 + (9.247 * weight) + (3.098 * height * 100) - (4.330 * age)
    else:
        # Average formula between male and female
        bmr_male = 88.362 + (13.397 * weight) + (4.799 * height * 100) - (5.677 * age)
        bmr_female = 447.593 + (9.247 * weight) + (3.098 * height * 100) - (4.330 * age)
        bmr = (bmr_male + bmr_female) / 2
    return round(bmr)


def calculate_session_calories(weight: float, training_session: dict):
    warm_up_calories_burned = training_session["warm_up"] * 2 * weight
    cardio_calories_burned = training_session["cardio"] * 3.5 * weight
    strength_calories_burned = training_session["strength"] * 5.5 * weight
    cool_down_calories_burned = training_session["cool_down"] * 1.5 * weight
    total_calories_burned = warm_up_calories_burned + cardio_calories_burned + strength_calories_burned + cool_down_calories_burned
    return round(total_calories_burned)


def calculate_daily_calories(base_calories: float, training_objective: FoodTrainingObjective):
    if training_objective == FoodTrainingObjective.LOSE_WEIGHT:
        return base_calories * 0.8
    elif training_objective == FoodTrainingObjective.TONE_UP:
        return base_calories * 1.1
    elif training_objective == FoodTrainingObjective.BUILD_MUSCLE_MASS:
        return base_calories * 1.3
    elif training_objective == FoodTrainingObjective.MAINTAIN_FITNESS:
        return base_calories


def find_closest_dish(dishes: list[Dish], food_category: FoodCategory, target_calories: float):
    closest_dish = None
    min_difference = float("inf")

    for dish in dishes:
        if dish.category != food_category:
            continue
        difference = abs(dish.calories - target_calories)

        if difference < min_difference:
            min_difference = difference
            closest_dish = dish

    return closest_dish
