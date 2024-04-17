from sqlalchemy.orm import Session

from app.config.settings import Config
from app.models.business_partners import BusinessPartner
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate
from app.security.jwt import JWTManager
from app.models.mappers.user_mapper import DataClassMapper
from app.exceptions.exceptions import InvalidCredentialsError, EntityExistsError
from app.security.passwords import PasswordManager


class BusinessPartnersService:
    def __init__(self, db: Session, business_partner_token: str = None):
        self.business_partner_token = business_partner_token
        self.db = db
        self.jwt_manager = JWTManager(Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM, Config.ACCESS_TOKEN_EXPIRE_MINUTES, Config.REFRESH_TOKEN_EXPIRE_MINUTES)

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
