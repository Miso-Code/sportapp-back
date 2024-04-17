import base64
import time
from tempfile import NamedTemporaryFile

from sqlalchemy.orm import Session

from app.aws.aws_service import AWSClient
from app.config.settings import Config
from app.models.business_partners import BusinessPartner, BusinessPartnerProduct
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate, CreateBusinessPartnerProduct
from app.security.jwt import JWTManager
from app.models.mappers.user_mapper import DataClassMapper
from app.exceptions.exceptions import InvalidCredentialsError, EntityExistsError, NotFoundError
from app.security.passwords import PasswordManager


class BusinessPartnersService:
    def __init__(self, db: Session, business_partner_token: str = None):
        self.business_partner_token = business_partner_token
        self.db = db
        self.jwt_manager = JWTManager(Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM, Config.ACCESS_TOKEN_EXPIRE_MINUTES, Config.REFRESH_TOKEN_EXPIRE_MINUTES)
        self.aws_service = AWSClient()

    def create_business_partner(self, business_partner: BusinessPartnerCreate):
        existing_business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.email == business_partner.email).first()
        if existing_business_partner:
            raise EntityExistsError("Business partner with this email already exists")

        business_partner_dict = business_partner.dict()
        business_partner_dict["hashed_password"] = PasswordManager.get_password_hash(business_partner_dict["password"])
        del business_partner_dict["password"]

        business_partner = BusinessPartner(**business_partner_dict)
        self.db.add(business_partner)
        self.db.commit()
        return DataClassMapper.to_dict(business_partner)

    def authenticate_business_partner(self, business_partner_credentials: BusinessPartnerCredentials):
        if business_partner_credentials.refresh_token:
            return self.jwt_manager.process_refresh_token_login(business_partner_credentials.refresh_token)
        else:
            return self._process_email_password_login(business_partner_credentials.email, business_partner_credentials.password)

    def _process_email_password_login(self, business_partner_credentials_email, business_partner_credentials_password):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.email == business_partner_credentials_email).first()
        if not business_partner:
            raise InvalidCredentialsError("Invalid email or password")

        return self.jwt_manager.process_email_password_login(
            business_partner.business_partner_id,
            business_partner_credentials_password,
            business_partner.hashed_password,
        )

    def create_business_partner_product(self, create_service: CreateBusinessPartnerProduct, business_partner_id):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.business_partner_id == business_partner_id).first()
        if not business_partner:
            raise NotFoundError(f"Business partner with id {business_partner_id} not found")

        if create_service.image_base64:
            create_service.image_url = self._upload_product_image(create_service.image_base64, business_partner_id)
        product_dict = create_service.dict()
        print(product_dict)
        del product_dict["image_base64"]
        product = BusinessPartnerProduct(**product_dict)
        business_partner.products.append(product)
        self.db.commit()

        return DataClassMapper.to_dict(product)

    def _upload_product_image(self, product_image_base64, business_partner_id):
        with NamedTemporaryFile(delete=False) as temp_file:
            image_type = product_image_base64.split(",")[0].split("/")[1].split("+")[0]
            image_content_base64 = bytes(product_image_base64.split(",")[1], encoding="utf-8")
            product_image_content = base64.decodebytes(image_content_base64)
            temp_file.write(product_image_content)

            current_timestamp_ms = int(time.time() * 1000)
            image_name = f"logo_{current_timestamp_ms}.{image_type}"
            image_url = self.aws_service.s3.upload_file(temp_file.name, Config.BUSINESS_PARTNERS_PRODUCTS_BUCKET_NAME, f"product_images/{business_partner_id}/{image_name}")
        print(image_url)
        return image_url

    def get_all_business_partner_products(self, user_id):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.business_partner_id == user_id).first()
        if not business_partner:
            raise NotFoundError(f"Business partner with id {user_id} not found")

        return [DataClassMapper.to_dict(product) for product in business_partner.products]
