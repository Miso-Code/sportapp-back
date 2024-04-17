from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate
from app.services.business_partners import BusinessPartnersService

router = APIRouter(
    prefix="/business-partners",
    tags=["business-partners"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registration")
async def register_business_partner(business_partner: BusinessPartnerCreate, db: Session = Depends(get_db)):
    register_user_response = BusinessPartnersService(db).create_business_partner(business_partner)
    return JSONResponse(content=register_user_response, status_code=201)


@router.post("/login")
async def login_business_partner(business_partner_credentials: BusinessPartnerCredentials, db: Session = Depends(get_db)):
    register_user_response = BusinessPartnersService(db).authenticate_business_partner(business_partner_credentials)
    return JSONResponse(content=register_user_response, status_code=200)
