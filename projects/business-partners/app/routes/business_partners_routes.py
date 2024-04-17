from uuid import UUID
from typing import Annotated

from fastapi import Depends, APIRouter, Header, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.models.schemas.schema import BusinessPartnerCredentials, BusinessPartnerCreate, CreateBusinessPartnerProduct
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


@router.post("/products")
async def create_business_partner_product(create_product: CreateBusinessPartnerProduct, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    register_user_response = BusinessPartnersService(db).create_business_partner_product(create_product, user_id)
    return JSONResponse(content=register_user_response, status_code=201)


@router.get("/products")
async def get_all_business_partner_products(user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    register_user_response = BusinessPartnersService(db).get_all_business_partner_products(user_id)
    return JSONResponse(content=register_user_response, status_code=200)
