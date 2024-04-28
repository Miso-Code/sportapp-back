import unittest
from faker import Faker
from app.models.schemas.schema import UserCreate, UserCredentials, UserAdditionalInformation, UpdateSubscriptionType
from app.models.users import UserIdentificationType, Gender, UserSubscriptionType

from app.exceptions.exceptions import InvalidValueError

fake = Faker()


class TestUserCreate(unittest.TestCase):
    def test_valid_user_create(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = f"{fake.password()}A123!"

        user_data = {"first_name": first_name, "last_name": last_name, "email": email, "password": password}
        user = UserCreate(**user_data)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.password, password)

    def test_invalid_password(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = fake.word()

        user_data = {"first_name": first_name, "last_name": last_name, "email": email, "password": password}
        password_requirements = (
            "Password must be between 8 and 64 characters long and contain at least " "one digit, one lowercase letter, one uppercase letter, and one special " "character"
        )
        with self.assertRaises(InvalidValueError) as context:
            UserCreate(**user_data)
        self.assertEqual(
            str(context.exception),
            password_requirements,
        )


class TestUserAdditionalInformation(unittest.TestCase):
    def test_valid_additional_information(self):
        identification_type = fake.enum(UserIdentificationType)
        identification_number = fake.numerify(text="############")
        gender = fake.enum(Gender)
        country_of_birth = fake.country()
        city_of_birth = fake.city()
        country_of_residence = fake.country()
        city_of_residence = fake.city()
        residence_age = fake.random_int(min=1, max=100)
        birth_date = fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d")

        user_data = {
            "identification_type": identification_type,
            "identification_number": identification_number,
            "gender": gender,
            "country_of_birth": country_of_birth,
            "city_of_birth": city_of_birth,
            "country_of_residence": country_of_residence,
            "city_of_residence": city_of_residence,
            "residence_age": residence_age,
            "birth_date": birth_date,
        }

        user = UserAdditionalInformation(**user_data)

        self.assertEqual(user.identification_type, identification_type)
        self.assertEqual(user.identification_number, identification_number)
        self.assertEqual(user.gender, gender)
        self.assertEqual(user.country_of_birth, country_of_birth)
        self.assertEqual(user.city_of_birth, city_of_birth)
        self.assertEqual(user.country_of_residence, country_of_residence)
        self.assertEqual(user.city_of_residence, city_of_residence)
        self.assertEqual(user.residence_age, residence_age)
        self.assertEqual(user.birth_date, birth_date)

    def test_invalid_additional_information_birth_date(self):
        identification_type = fake.enum(UserIdentificationType)
        identification_number = fake.numerify(text="############")
        gender = fake.enum(Gender)
        country_of_birth = fake.country()
        city_of_birth = fake.city()
        country_of_residence = fake.country()
        city_of_residence = fake.city()
        residence_age = fake.random_int(min=1, max=100)
        birth_date = "invalid-date-format"

        user_data = {
            "identification_type": identification_type,
            "identification_number": identification_number,
            "gender": gender,
            "country_of_birth": country_of_birth,
            "city_of_birth": city_of_birth,
            "country_of_residence": country_of_residence,
            "city_of_residence": city_of_residence,
            "residence_age": residence_age,
            "birth_date": birth_date,
        }

        with self.assertRaises(InvalidValueError) as context:
            UserAdditionalInformation(**user_data)
        self.assertEqual(str(context.exception), "Birth date must be in the format YYYY-MM-DD")


class TestUserCredentials(unittest.TestCase):
    def test_valid_credentials_email_password(self):
        email = fake.email()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        credentials = {"email": email, "password": password}

        credentials = UserCredentials(**credentials)
        self.assertEqual(credentials.email, email)
        self.assertEqual(credentials.password, password)

    def test_valid_credentials_token(self):
        token = fake.word()

        credentials = {"refresh_token": token}

        credentials = UserCredentials(**credentials)
        self.assertEqual(credentials.refresh_token, token)

    def test_invalid_credentials(self):
        email = fake.email()

        # Invalid credentials scenarios
        # 1. Providing refresh_token along with email and password
        with self.assertRaises(InvalidValueError) as context:
            UserCredentials(refresh_token="refresh_token", email=email, password=fake.password())
        self.assertEqual(str(context.exception), "Cannot provide refresh_token along with email and password")

        # 2. Not providing refresh_token or both email and password
        with self.assertRaises(InvalidValueError) as context:
            UserCredentials(email=email)
        self.assertEqual(str(context.exception), "Either provide refresh_token or both email and password")

        # 3. Not providing any data
        with self.assertRaises(InvalidValueError) as context:
            UserCredentials()
        self.assertEqual(str(context.exception), "Either provide refresh_token or both email and password")

    def test_invalid_credentials_email(self):
        email = fake.word()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        with self.assertRaises(InvalidValueError) as context:
            UserCredentials(email=email, password=password)
        self.assertEqual(str(context.exception), "Invalid email address")


class TestUpdateSubscriptionType(unittest.TestCase):
    def test_valid_body_update_subscription_type_free(self):
        update = UpdateSubscriptionType(
            subscription_type=UserSubscriptionType.FREE,
        )

        self.assertEqual(update.subscription_type, UserSubscriptionType.FREE)

    def test_valid_body_update_subscription_type_premium(self):
        card_number = fake.credit_card_number()
        card_holder = fake.name()
        card_expiration_date = fake.credit_card_expire()
        card_cvv = fake.credit_card_security_code()
        amount = fake.random_int(min=1, max=1000)

        update = UpdateSubscriptionType(
            subscription_type=UserSubscriptionType.PREMIUM,
            payment_data={"card_number": card_number, "card_holder": card_holder, "card_expiration_date": card_expiration_date, "card_cvv": card_cvv, "amount": amount},
        )

        self.assertEqual(update.subscription_type, UserSubscriptionType.PREMIUM)
        self.assertEqual(update.payment_data.card_number, card_number)
        self.assertEqual(update.payment_data.card_holder, card_holder)
        self.assertEqual(update.payment_data.card_expiration_date, card_expiration_date)
        self.assertEqual(update.payment_data.card_cvv, card_cvv)
        self.assertEqual(update.payment_data.amount, amount)

    def test_valid_body_update_subscription_type_intermediate(self):
        card_number = fake.credit_card_number()
        card_holder = fake.name()
        card_expiration_date = fake.credit_card_expire()
        card_cvv = fake.credit_card_security_code()
        amount = fake.random_int(min=1, max=1000)

        update = UpdateSubscriptionType(
            subscription_type=UserSubscriptionType.INTERMEDIATE,
            payment_data={"card_number": card_number, "card_holder": card_holder, "card_expiration_date": card_expiration_date, "card_cvv": card_cvv, "amount": amount},
        )

        self.assertEqual(update.subscription_type, UserSubscriptionType.INTERMEDIATE)
        self.assertEqual(update.payment_data.card_number, card_number)
        self.assertEqual(update.payment_data.card_holder, card_holder)
        self.assertEqual(update.payment_data.card_expiration_date, card_expiration_date)
        self.assertEqual(update.payment_data.card_cvv, card_cvv)
        self.assertEqual(update.payment_data.amount, amount)

    def test_invalid_body_update_non_free_subscriptions(self):
        with self.assertRaises(InvalidValueError) as context:
            UpdateSubscriptionType(
                subscription_type=UserSubscriptionType.PREMIUM.value,
            )
        self.assertEqual(str(context.exception), "Payment data is required for premium and intermediate subscriptions")

        with self.assertRaises(InvalidValueError) as context:
            UpdateSubscriptionType(
                subscription_type=UserSubscriptionType.INTERMEDIATE.value,
            )
        self.assertEqual(str(context.exception), "Payment data is required for premium and intermediate subscriptions")
