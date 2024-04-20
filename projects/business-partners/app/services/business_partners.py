import base64
import time
from tempfile import NamedTemporaryFile

from sqlalchemy import and_, or_, cast, String
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
        self.jwt_manager = JWTManager(
            Config.JWT_SECRET_KEY,
            Config.JWT_ALGORITHM,
            Config.ACCESS_TOKEN_EXPIRE_MINUTES,
            Config.REFRESH_TOKEN_EXPIRE_MINUTES,
        )
        self.aws_service = AWSClient()

    def create_business_partner(self, business_partner: BusinessPartnerCreate):
        existing_business_partner = (
            self.db.query(BusinessPartner)
            .filter(
                BusinessPartner.email == business_partner.email,
            )
            .first()
        )
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
            return self._process_email_password_login(
                business_partner_credentials.email,
                business_partner_credentials.password,
            )

    def _process_email_password_login(self, business_partner_credentials_email, business_partner_credentials_password):
        business_partner = (
            self.db.query(BusinessPartner)
            .filter(
                BusinessPartner.email == business_partner_credentials_email,
            )
            .first()
        )
        if not business_partner:
            raise InvalidCredentialsError("Invalid email or password")

        return self.jwt_manager.process_email_password_login(
            business_partner.business_partner_id,
            business_partner_credentials_password,
            business_partner.hashed_password,
        )

    def create_business_partner_product(self, create_product: CreateBusinessPartnerProduct, business_partner_id):
        business_partner = (
            self.db.query(BusinessPartner)
            .filter(
                BusinessPartner.business_partner_id == business_partner_id,
            )
            .first()
        )
        if not business_partner:
            raise NotFoundError(f"Business partner with id {business_partner_id} not found")
        if create_product.image_base64:
            create_product.image_url = self._upload_product_image(
                create_product.image_base64,
                create_product.name,
                business_partner_id,
            )
        product_dict = create_product.dict()
        del product_dict["image_base64"]
        product = BusinessPartnerProduct(**product_dict)
        business_partner.products.append(product)
        self.db.commit()

        return DataClassMapper.to_dict(product)

    def _upload_product_image(self, product_image_base64, product_name, business_partner_id):
        with NamedTemporaryFile(delete=True) as temp_file:
            image_content_base64 = bytes(product_image_base64.split(",")[1], encoding="utf-8")
            product_image_content = base64.decodebytes(image_content_base64)
            temp_file.write(product_image_content)

            current_timestamp_ms = int(time.time() * 1000)
            product_name_formatted = product_name.strip().lower().replace(" ", "_")
            image_name = f"{product_name_formatted}_{current_timestamp_ms}"
            image_url = self.aws_service.s3.upload_file(
                temp_file.name,
                Config.BUSINESS_PARTNERS_PRODUCTS_BUCKET_NAME,
                f"product_images/{business_partner_id}/{image_name}",
            )
        return image_url

    def update_business_partner_product(self, product_id, business_partner_id, update_product):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.business_partner_id == business_partner_id).first()
        if not business_partner:
            raise NotFoundError(f"Business partner with id {business_partner_id} not found")

        product = (
            self.db.query(BusinessPartnerProduct)
            .filter(BusinessPartnerProduct.product_id == product_id, BusinessPartnerProduct.business_partner_id == business_partner.business_partner_id)
            .first()
        )

        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        for field in update_product.dict(exclude={"image_base64"}, exclude_defaults=True).keys():
            setattr(product, field, getattr(update_product, field))

        if update_product.image_base64:
            product.image_url = self._upload_product_image(
                update_product.image_base64,
                product.name,
                business_partner_id,
            )

        self.db.commit()
        return DataClassMapper.to_dict(product)

    def delete_business_partner_product(self, product_id, business_partner_id):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.business_partner_id == business_partner_id).first()
        if not business_partner:
            raise NotFoundError(f"Business partner with id {business_partner_id} not found")

        product = (
            self.db.query(BusinessPartnerProduct)
            .filter(BusinessPartnerProduct.product_id == product_id, BusinessPartnerProduct.business_partner_id == business_partner.business_partner_id)
            .first()
        )

        if not product:
            raise NotFoundError(f"Product with id {product_id} not found")

        self.db.delete(product)
        self.db.commit()

        return {"message": "Product deleted"}

    def get_business_partner_products(self, business_partner_id, offset, limit):
        business_partner = self.db.query(BusinessPartner).filter(BusinessPartner.business_partner_id == business_partner_id).first()
        if not business_partner:
            raise NotFoundError(f"Business partner with id {business_partner_id} not found")

        products = (
            self.db.query(BusinessPartnerProduct)
            .filter(
                BusinessPartnerProduct.business_partner_id == business_partner_id,
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [DataClassMapper.to_dict(product) for product in products]

    def get_all_offered_products(self, search, offset, limit):
        if search:
            products = (
                self.db.query(BusinessPartnerProduct)
                .filter(
                    and_(
                        BusinessPartnerProduct.active,
                        or_(
                            cast(BusinessPartnerProduct.category, String).ilike(f"%{search}%"),
                            BusinessPartnerProduct.name.ilike(f"%{search}%"),
                            BusinessPartnerProduct.summary.ilike(f"%{search}%"),
                        ),
                    ),
                )
                .order_by(BusinessPartnerProduct.name.asc())
                .limit(limit)
                .offset(offset)
                .all()
            )
        else:
            products = self.db.query(BusinessPartnerProduct).filter(BusinessPartnerProduct.active).order_by(BusinessPartnerProduct.name.asc()).limit(limit).offset(offset).all()

        return [DataClassMapper.to_dict(product) for product in products]
