from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.config.settings import Config
from app.models.schemas.schema import SubscriptionPaymentStatus, UpdateSubscriptionTypeResponse, UpdateSubscriptionType, PremiumSportsmanAppointment
from app.security.jwt import JWTManager
from app.models.users import User, NutritionalLimitation, TrainingLimitation, UserSubscriptionType, Trainer, UserSportsmanAppointment
from app.models.mappers.user_mapper import DataClassMapper
from app.exceptions.exceptions import NotFoundError, InvalidCredentialsError, PlanPaymentError
from app.security.passwords import PasswordManager
from app.services.external import ExternalServices


class UsersServiceHelpers:
    @staticmethod
    def create_user_dict(user_data):
        return {"user_id": str(user_data[0]), "first_name": user_data[1], "last_name": user_data[2], "email": user_data[3]}

    @staticmethod
    def process_training_limitations(training_limitations_to_update: list[TrainingLimitation], db):
        training_limitations = []
        for training_limitation in training_limitations_to_update:
            if training_limitation.limitation_id:
                limitation_id = training_limitation.limitation_id
                limitation = db.query(TrainingLimitation).filter(TrainingLimitation.limitation_id == limitation_id).first()
                if limitation:
                    limitation.name = training_limitation.name
                    limitation.description = training_limitation.description
                    training_limitations.append(limitation)
                else:
                    raise NotFoundError(f"Training limitation with id {limitation_id} not found")
            else:
                training_limitations.append(UsersServiceHelpers.create_training_limitation(training_limitation))

        return training_limitations

    @staticmethod
    def create_training_limitation(training_limitation):
        return TrainingLimitation(name=training_limitation.name, description=training_limitation.description)


class UsersService:
    def __init__(self, db: Session, user_token: str = None):
        self.user_token = user_token
        self.db = db
        self.jwt_manager = JWTManager(Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM, Config.ACCESS_TOKEN_EXPIRE_MINUTES, Config.REFRESH_TOKEN_EXPIRE_MINUTES)
        self.external_services = ExternalServices()

    def create_users(self, users_create):
        values_to_insert = []
        for user_create in users_create:
            user = user_create.model_dump()
            user["hashed_password"] = PasswordManager.get_password_hash(user["password"])
            del user["password"]
            values_to_insert.append(user)
        if not values_to_insert:
            return []
        insert_statement = insert(User).values(values_to_insert).returning(User.user_id, User.first_name, User.last_name, User.email)
        created_users = self.db.execute(insert_statement).fetchall()
        self.db.commit()
        return [UsersServiceHelpers.create_user_dict(user) for user in created_users]

    def complete_user_registration(self, user_id, user_additional_information):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        user.identification_type = user_additional_information.identification_type
        user.identification_number = user_additional_information.identification_number
        user.gender = user_additional_information.gender
        user.country_of_birth = user_additional_information.country_of_birth
        user.city_of_birth = user_additional_information.city_of_birth
        user.country_of_residence = user_additional_information.country_of_residence
        user.city_of_residence = user_additional_information.city_of_residence
        user.residence_age = user_additional_information.residence_age
        user.birth_date = user_additional_information.birth_date

        self.db.commit()

        return DataClassMapper.to_dict(user)

    def authenticate_user(self, user_credentials):
        if user_credentials.refresh_token:
            return self._process_refresh_token_login(user_credentials.refresh_token)
        else:
            return self._process_email_password_login(user_credentials.email, user_credentials.password)

    def get_user_personal_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_personal_profile(user)

    def get_user_sports_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_sports_profile(user)

    def get_user_nutritional_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_nutritional_profile(user)

    # noinspection PyMethodMayBeStatic
    def get_nutritional_limitations(self):
        nutritional_limitations = self.db.query(NutritionalLimitation).all()
        return [DataClassMapper.to_dict(limitation) for limitation in nutritional_limitations]

    def update_user_personal_information(self, user_id, personal_profile):
        user = self.get_user_by_id(user_id)
        for field in personal_profile.dict(exclude_defaults=True).keys():
            setattr(user, field, getattr(personal_profile, field))

        self.db.commit()
        return DataClassMapper.to_user_personal_profile(user)

    def update_user_nutritional_information(self, user_id, nutritional_profile):
        user = self.get_user_by_id(user_id)
        if nutritional_profile.food_preference:
            user.food_preference = nutritional_profile.food_preference

        user.nutritional_limitations = []
        for limitation_id in nutritional_profile.nutritional_limitations:
            limitation = self.db.query(NutritionalLimitation).filter(NutritionalLimitation.limitation_id == UUID(limitation_id)).first()
            if limitation:
                user.nutritional_limitations.append(limitation)
            else:
                raise NotFoundError(f"Nutritional limitation with id {limitation_id} not found")

        self.db.commit()
        return DataClassMapper.to_user_nutritional_profile(user)

    def update_user_sports_information(self, user_id, sports_profile):
        user = self.get_user_by_id(user_id)
        for field in sports_profile.dict(exclude={"favourite_sport_id", "training_limitations"}, exclude_defaults=True).keys():
            setattr(user, field, getattr(sports_profile, field))

        if sports_profile.favourite_sport_id:
            sport = self.external_services.get_sport(sports_profile.favourite_sport_id, self.user_token)
            user.favourite_sport_id = sport["sport_id"]

        if sports_profile.available_weekdays:
            user.available_weekdays = ",".join(sports_profile.available_weekdays)

        user.training_limitations = UsersServiceHelpers.process_training_limitations(sports_profile.training_limitations, self.db)

        should_update_training_plan = user.training_objective and user.available_training_hours and user.available_weekdays and user.preferred_training_start_time

        if should_update_training_plan:
            self.external_services.create_training_plan(DataClassMapper.to_training_plan_create(user), self.user_token)

        self.db.commit()
        return DataClassMapper.to_user_sports_profile(user)

    def get_user_by_id(self, user_id):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return user

    def _process_email_password_login(self, user_credentials_email, user_credentials_password):
        user = self.db.query(User).filter(User.email == user_credentials_email).first()
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not PasswordManager.verify_password(user_credentials_password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        return self.jwt_manager.generate_tokens(user.user_id, user.subscription_type)

    def _process_refresh_token_login(self, refresh_token):
        user_id = self.jwt_manager.decode_refresh_token(refresh_token)

        user = self.db.query(User).filter(User.user_id == UUID(user_id)).first()

        return self.jwt_manager.generate_tokens(user.user_id, user.subscription_type)

    def update_user_plan(self, user_id, update_subscription_type: UpdateSubscriptionType):
        user = self.get_user_by_id(user_id)

        if update_subscription_type.subscription_type == UserSubscriptionType.FREE:
            user.subscription_type = update_subscription_type.subscription_type
            user.subscription_start_date = None
            user.subscription_end_date = None
            self.db.commit()
            return DataClassMapper.to_dict(UpdateSubscriptionTypeResponse(status=SubscriptionPaymentStatus.SUCCESS, message="Subscription updated successfully"), pydantic=True)
        else:
            payment_approved, error = self.external_services.process_payment(update_subscription_type.payment_data)

            if payment_approved:
                user.subscription_type = update_subscription_type.subscription_type
                user.subscription_start_date = datetime.now()
                user.subscription_end_date = user.subscription_start_date + timedelta(days=30)
                self.db.commit()
                response = UpdateSubscriptionTypeResponse(
                    status=SubscriptionPaymentStatus.SUCCESS,
                    message="Subscription updated successfully",
                    subscription_start_date=user.subscription_start_date,
                    subscription_end_date=user.subscription_end_date,
                )

                return DataClassMapper.to_dict(response, pydantic=True)
            else:
                error = error["error"]
                message = f"Failed to process payment. {error}"
                raise PlanPaymentError(message)

    def schedule_premium_sportsman_appointment(self, user_id, appointment_data: PremiumSportsmanAppointment):
        user = self.get_user_by_id(user_id)

        trainer = self.db.query(Trainer).filter(Trainer.trainer_id == appointment_data.trainer_id).first()

        if not trainer:
            raise NotFoundError(f"Trainer with id {appointment_data.trainer_id} not found")

        appointment = UserSportsmanAppointment(
            user_id=user.user_id,
            appointment_date=appointment_data.appointment_date,
            appointment_type=appointment_data.appointment_type,
            appointment_location=appointment_data.appointment_location,
            trainer_id=trainer.trainer_id,
            appointment_reason=appointment_data.appointment_reason,
        )

        self.db.add(appointment)
        self.db.commit()

        return DataClassMapper.to_dict(appointment)

    def get_scheduled_appointments(self, user_id):
        user = self.get_user_by_id(user_id)
        appointments = self.db.query(UserSportsmanAppointment).filter(UserSportsmanAppointment.user_id == user.user_id).all()
        return [DataClassMapper.to_dict(appointment) for appointment in appointments]

    def get_premium_trainers(self):
        trainers = self.db.query(Trainer).all()

        return [DataClassMapper.to_dict(trainer) for trainer in trainers]
