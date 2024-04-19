from app.models.business_partners import BusinessPartner, ProductCategory, PaymentFrequency, PaymentType, BusinessPartnerProduct
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate, CreateBusinessPartnerProduct


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
