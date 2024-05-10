from app.models.business_partners import BusinessPartner, ProductCategory, PaymentFrequency, PaymentType, BusinessPartnerProduct, ProductTransaction, TransactionStatus
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate, CreateBusinessPartnerProduct, ProductPurchase, PaymentData, SuggestBusinessPartnerProduct


def generate_random_user_login_data(faker, token=False):
    if token:
        return BusinessPartnerCredentials(refresh_token=faker.uuid4())
    else:
        return BusinessPartnerCredentials(email=faker.email(), password=f"{faker.password()}A123!", refresh_token=None)


def generate_random_business_partner_create_data(faker):
    return BusinessPartnerCreate(
        business_partner_name=faker.company(),
        email=faker.email(),
        password=faker.password(),
    )


def generate_random_business_partner(faker):
    return BusinessPartner(
        business_partner_id=faker.uuid4(),
        business_partner_name=faker.company(),
        email=faker.email(),
        hashed_password=faker.password(),
    )


def generate_random_business_partner_product_create_data(faker):
    return CreateBusinessPartnerProduct(
        category=faker.enum(ProductCategory),
        name=faker.company(),
        summary=faker.word(),
        url=faker.url(),
        price=faker.random_number(digits=2),
        payment_type=faker.enum(PaymentType),
        payment_frequency=faker.enum(PaymentFrequency),
        image_url=faker.url(),
        description=faker.text(),
        active=True,
        sport_id=str(faker.uuid4()),
    )


def generate_random_business_partner_suggested_filter(faker):
    return SuggestBusinessPartnerProduct(
        category=faker.enum(ProductCategory),
        sport_id=str(faker.uuid4()),
    )


def generate_random_business_partner_product(faker):
    return BusinessPartnerProduct(
        product_id=faker.uuid4(),
        category=faker.enum(ProductCategory),
        name=faker.company(),
        summary=faker.word(),
        url=faker.url(),
        price=faker.random_number(digits=2),
        payment_type=faker.enum(PaymentType),
        payment_frequency=faker.enum(PaymentFrequency),
        image_url=faker.url(),
        description=faker.text(),
        active=True,
    )


def generate_random_product_purchase(faker):
    return ProductPurchase(
        user_name=faker.name(),
        user_email=faker.email(),
        payment_data=PaymentData(
            card_number=faker.credit_card_number(),
            card_holder=faker.name(),
            card_expiration_date=faker.credit_card_expire(),
            card_cvv=faker.credit_card_security_code(),
            amount=faker.random_number(digits=2),
        ),
    )


def generate_random_product_transaction(faker):
    return ProductTransaction(
        product_transaction_id=faker.uuid4(),
        product_id=faker.uuid4(),
        user_id=faker.uuid4(),
        user_name=faker.name(),
        user_email=faker.email(),
        transaction_date=faker.date_time_this_year(),
        transaction_status=faker.enum(TransactionStatus),
        product_data={
            "category": faker.enum(ProductCategory).value,
            "name": faker.company(),
            "summary": faker.word(),
            "url": faker.url(),
            "price": faker.random_number(digits=2),
            "payment_type": faker.enum(PaymentType).value,
            "payment_frequency": faker.enum(PaymentFrequency).value,
            "image_url": faker.url(),
            "description": faker.text(),
            "active": True,
        },
    )
