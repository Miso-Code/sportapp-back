import json
from datetime import datetime
from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session

from app.aws.aws import AWSClient
from app.config.settings import Config
from app.models.mappers.data_mapper import DataClassMapper
from app.models.model import (
    FoodTrainingObjective,
    FoodIntake,
    Dish,
    FoodCategory,
    WeekDay,
    FoodType,
)
from app.models.schemas.schema import (
    SessionCalories,
    NutritionalPlanCreate,
)
from app.services.external import ExternalServices
from app.utils import utils


class NutritionalPlansService:
    def __init__(self, db: Session):
        self.db = db
        self.sqs = AWSClient().sqs
        self.external_services = ExternalServices()
        self.notification_queue = Config.NUTRITIONAL_PLAN_ALERTS_QUEUE

    def notify_caloric_intake(self, user_id: UUID, user_auth_token: str, session_calories: SessionCalories, lang: str) -> dict:
        training_objective = self._get_training_objective(user_id, user_auth_token)
        message = self._process_caloric_intake(session_calories, training_objective, user_id, lang)
        self._notify_user(user_id, message)
        return {"user_id": str(user_id), "message": message}

    def create_nutritional_plan(
        self,
        user_id: UUID,
        user_auth_token: str,
        nutritional_plan_create: NutritionalPlanCreate,
    ):
        self._clear_previous_plan(user_id)

        basal_metabolism = self._calculate_basal_metabolism(nutritional_plan_create)
        training_plan = self.external_services.get_training_plan(user_id, user_auth_token)
        dishes = self._get_filtered_dishes(nutritional_plan_create)

        for weekday in WeekDay:
            session = self._get_session_for_weekday(training_plan, weekday)
            self._generate_daily_food_intake(
                user_id,
                dishes,
                basal_metabolism,
                nutritional_plan_create,
                session,
                weekday,
            )

        return {"user_id": str(user_id), "message": "Nutritional plan created successfully"}

    def _clear_previous_plan(self, user_id):
        self.db.query(FoodIntake).filter(FoodIntake.user_id == user_id).delete()
        self.db.commit()

    def get_nutritional_plan(self, user_id: UUID, language: str) -> list[dict]:
        if language == "es":
            query = self.db.query(FoodIntake.week_day, Dish.name_es, Dish.category, Dish.calories, Dish.protein, Dish.carbs, Dish.fat)
        else:
            query = self.db.query(FoodIntake.week_day, Dish.name, Dish.category, Dish.calories, Dish.protein, Dish.carbs, Dish.fat)

        results = query.join(Dish, FoodIntake.dish_id == Dish.dish_id).filter(FoodIntake.user_id == user_id).order_by(FoodIntake.week_day).all()

        return [DataClassMapper.to_dict(result) for result in results]

    def _get_training_objective(self, user_id: UUID, user_auth_token: str) -> FoodTrainingObjective:
        user_sport_profile = self.external_services.get_user_sport_profile(user_id, user_auth_token)
        return FoodTrainingObjective(user_sport_profile["training_objective"])

    def _process_caloric_intake(self, session_calories: SessionCalories, training_objective: FoodTrainingObjective, user_id: UUID, lang: str) -> str:
        calories_remaining = session_calories.calories_burn_expected - session_calories.calories_burn
        current_weekday = utils.get_current_weekday()
        current_recover_snack = self._get_current_recover_snack(user_id, current_weekday)

        if calories_remaining < 0:
            message = self._generate_positive_message(abs(calories_remaining), training_objective, current_recover_snack, lang)
        else:
            message = self._generate_negative_message(calories_remaining, lang)
        return message

    def _get_current_recover_snack(self, user_id: UUID, current_weekday: WeekDay) -> Optional[Dish]:
        return (
            self.db.query(Dish)
            .join(FoodIntake, Dish.dish_id == FoodIntake.dish_id)
            .filter(FoodIntake.user_id == user_id, FoodIntake.week_day == current_weekday, Dish.category == FoodCategory.RECOVERY_SNACK)
            .first()
        )

    def _generate_positive_message(self, calories_remaining: float, training_objective: FoodTrainingObjective, recover_snack: Dish, lang: str) -> str:
        if lang == "es":
            if training_objective == FoodTrainingObjective.LOSE_WEIGHT:
                message = "Recuerda beber solo agua para mantener baja tu ingesta calórica y alcanzar tu objetivo."
            else:
                if recover_snack:
                    portion = self._calculate_snack_portion(calories_remaining, recover_snack.calories)
                    message = f"Recuerda comer {portion} porciones de tu snack de recuperación: {recover_snack.name_es}. Te quedan {calories_remaining} calorías por consumir."
                else:
                    message = f"Recuerda comer tu snack de recuperación. Te quedan {calories_remaining} calorías por consumir."
        else:
            if training_objective == FoodTrainingObjective.LOSE_WEIGHT:
                message = "Remember to drink water only to keep your caloric intake low and achieve your goal."
            else:
                if recover_snack:
                    portion = self._calculate_snack_portion(calories_remaining, recover_snack.calories)
                    message = f"Remember to eat {portion} portions of your recovery snack: {recover_snack.name}. You have {calories_remaining} calories left to consume."
                else:
                    message = f"Remember to eat your recovery snack. You have {calories_remaining} calories left to consume."

        return message

    def _generate_negative_message(self, calories_remaining: float, lang: str) -> str:
        if lang == "es":
            return f"Solamente bebe agua. Te quedan {calories_remaining} para consumir, !sigue así!"
        else:
            return f"Only drink water. You have {calories_remaining} left to consume, keep it up!"

    def _calculate_snack_portion(self, calories_remaining: float, recover_snack_calories: float) -> float:
        if recover_snack_calories == 0:
            return 0
        portions = calories_remaining / recover_snack_calories
        return round(portions * 2) / 2

    def _notify_user(self, user_id: UUID, message: str):
        sqs_message = {
            "user_id": str(user_id),
            "message": message,
            "date": datetime.now().isoformat(),
        }
        self.sqs.send_message(self.notification_queue, json.dumps(sqs_message))

    def _calculate_basal_metabolism(self, nutritional_plan_create: NutritionalPlanCreate) -> float:
        return utils.calculate_basal_metabolism(
            nutritional_plan_create.age,
            nutritional_plan_create.gender,
            nutritional_plan_create.weight,
            nutritional_plan_create.height,
        )

    def _get_filtered_dishes(self, nutritional_plan_create: NutritionalPlanCreate) -> List[Dish]:
        query = self.db.query(Dish).filter(
            Dish.objective == nutritional_plan_create.training_objective,
        )
        if nutritional_plan_create.food_preference == FoodType.VEGETARIAN:
            query = query.filter(Dish.food_type == nutritional_plan_create.food_preference, Dish.category == FoodType.VEGAN)
        elif nutritional_plan_create.food_preference == FoodType.VEGAN:
            query = query.filter(Dish.food_type == nutritional_plan_create.food_preference)
        return query.all()

    def _get_session_for_weekday(self, training_plan: list, weekday: WeekDay) -> Optional[dict]:
        for session in training_plan:
            if session["weekday"] == weekday.value:
                return session
        return None

    def _generate_daily_food_intake(
        self,
        user_id: UUID,
        dishes: List[Dish],
        basal_metabolism: float,
        nutritional_plan_create: NutritionalPlanCreate,
        training_session: Optional[dict],
        weekday: WeekDay,
    ):
        if training_session:
            session_calories = utils.calculate_session_calories(nutritional_plan_create.weight, training_session)
            total_daily_calories = basal_metabolism + session_calories
        else:
            total_daily_calories = basal_metabolism

        meals_calories = self._calculate_meal_calories(total_daily_calories)
        for category, calories in meals_calories.items():
            dish = self._get_dish_for_meal(dishes, category, calories, nutritional_plan_create.training_objective, nutritional_plan_create.food_preference)
            food_intake = FoodIntake(user_id=user_id, dish_id=dish.dish_id, week_day=weekday)
            self.db.add(food_intake)
        self.db.commit()

    def _calculate_meal_calories(self, total_daily_calories: float) -> dict:
        return {
            FoodCategory.BREAKFAST: round(total_daily_calories * 0.25),
            FoodCategory.LUNCH: round(total_daily_calories * 0.35),
            FoodCategory.DINNER: round(total_daily_calories * 0.15),
            FoodCategory.SNACK: round(total_daily_calories * 0.1),
            FoodCategory.RECOVERY_SNACK: round(total_daily_calories * 0.1),
        }

    def _get_dish_for_meal(
        self,
        dishes: List[Dish],
        food_category: FoodCategory,
        calories: float,
        training_objective: FoodTrainingObjective,
        food_preference: FoodType,
    ) -> Dish:
        dish = utils.find_closest_dish(dishes, food_category, calories)
        if not dish:
            dish = self._create_dish(food_category, calories, training_objective, food_preference)
        else:
            dishes.remove(dish)
        return dish

    def _create_dish(
        self,
        category: FoodCategory,
        calories: float,
        training_objective: FoodTrainingObjective,
        food_preference: FoodType,
    ) -> Dish:
        dish = Dish(
            name=f"Prepare a dish for {category.value} with {calories} calories",
            name_es=f"Prepara un plato para {category.value} con {calories} calorías",
            category=category,
            calories=calories,
            carbs=0,
            protein=0,
            fat=0,
            objective=training_objective,
            food_type=food_preference,
        )
        self.db.add(dish)
        self.db.commit()
        return dish
