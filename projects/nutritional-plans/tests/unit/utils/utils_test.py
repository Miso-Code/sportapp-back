import unittest
from unittest.mock import patch

from app.utils import utils
from app.models.model import WeekDay, FoodTrainingObjective, Dish, FoodCategory


class TestUtils(unittest.TestCase):

    @patch("app.utils.utils.datetime")
    def test_get_current_weekday(self, mock_datetime):
        mock_datetime.now.return_value.weekday.return_value = 0  # Monday
        self.assertEqual(utils.get_current_weekday(), WeekDay.MONDAY)

    def test_calculate_basal_metabolism_male(self):
        age = 30
        gender = "M"
        weight = 70
        height = 1.75
        expected_bmr = 1696
        self.assertEqual(utils.calculate_basal_metabolism(age, gender, weight, height), expected_bmr)

    def test_calculate_basal_metabolism_female(self):
        age = 30
        gender = "F"
        weight = 60
        height = 1.65
        expected_bmr = 1384
        self.assertEqual(utils.calculate_basal_metabolism(age, gender, weight, height), expected_bmr)

    def test_calculate_basal_metabolism_other(self):
        age = 30
        gender = "O"
        weight = 60
        height = 1.65
        expected_bmr = 1449
        self.assertEqual(utils.calculate_basal_metabolism(age, gender, weight, height), expected_bmr)

    def test_calculate_session_calories(self):
        weight = 70
        training_session = {"warm_up": 1, "cardio": 2, "strength": 1, "cool_down": 1}
        expected_calories = 1120
        self.assertEqual(utils.calculate_session_calories(weight, training_session), expected_calories)

    def test_calculate_daily_calories_lose_weight(self):
        base_calories = 2000
        training_objective = FoodTrainingObjective.LOSE_WEIGHT
        expected_calories = 1600  # Expected daily calories for losing weight
        self.assertEqual(utils.calculate_daily_calories(base_calories, training_objective), expected_calories)

    def test_calculate_daily_calories_tone_up(self):
        base_calories = 2000
        training_objective = FoodTrainingObjective.TONE_UP
        expected_calories = 2200  # Expected daily calories for toning up
        self.assertEqual(utils.calculate_daily_calories(base_calories, training_objective), expected_calories)

    def test_calculate_daily_calories_build_muscle_mass(self):
        base_calories = 2000
        training_objective = FoodTrainingObjective.BUILD_MUSCLE_MASS
        expected_calories = 2600  # Expected daily calories for building muscle mass
        self.assertEqual(utils.calculate_daily_calories(base_calories, training_objective), expected_calories)

    def test_calculate_daily_calories_maintain_fitness(self):
        base_calories = 2000
        training_objective = FoodTrainingObjective.MAINTAIN_FITNESS
        expected_calories = 2000  # Expected daily calories for maintaining fitness
        self.assertEqual(utils.calculate_daily_calories(base_calories, training_objective), expected_calories)

    def test_find_closest_dish(self):
        dishes = [
            Dish(name="Salad", category=FoodCategory.LUNCH, calories=150),
            Dish(name="Chicken Breast", category=FoodCategory.LUNCH, calories=250),
            Dish(name="Rice", category=FoodCategory.LUNCH, calories=200),
        ]
        food_category = FoodCategory.LUNCH
        target_calories = 300
        expected_dish = dishes[1]  # Chicken Breast has calories closest to 300
        self.assertEqual(utils.find_closest_dish(dishes, food_category, target_calories), expected_dish)
