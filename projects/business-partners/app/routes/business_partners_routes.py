from uuid import UUID
from typing import Annotated, Optional

from fastapi import Depends, APIRouter, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.models.schemas.schema import (
    BusinessPartnerCredentials,
    BusinessPartnerCreate,
    CreateBusinessPartnerProduct,
    ProductPurchase,
    UpdateBusinessPartnerProduct,
    SuggestBusinessPartnerProduct,
)
from app.services.business_partners import BusinessPartnersService

router = APIRouter(
    prefix="/business-partners",
    tags=["business-partners"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registration")
async def register_business_partner(business_partner: BusinessPartnerCreate, db: Session = Depends(get_db)):
    register_business_partner_response = BusinessPartnersService(db).create_business_partner(business_partner)
    return JSONResponse(content=register_business_partner_response, status_code=201)


@router.post("/login")
async def login_business_partner(business_partner_credentials: BusinessPartnerCredentials, db: Session = Depends(get_db)):
    auth_data = BusinessPartnersService(db).authenticate_business_partner(business_partner_credentials)
    return JSONResponse(content=auth_data, status_code=200)


@router.post("/products")
async def create_business_partner_product(create_product: CreateBusinessPartnerProduct, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    register_product_response = BusinessPartnersService(db).create_business_partner_product(create_product, user_id)
    return JSONResponse(content=register_product_response, status_code=201)


@router.get("/products")
async def get_all_business_partner_products(
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0, le=1000),
    limit: int = Query(10, gt=0, le=100),
):
    get_products_response = BusinessPartnersService(db).get_business_partner_products(user_id, offset, limit)
    return JSONResponse(content=get_products_response, status_code=200)


@router.get("/products/available")
async def get_all_offered_products(
    db: Session = Depends(get_db),
    search: Annotated[str | None, Query(max_length=50)] = None,
    offset: int = Query(0, ge=0, le=1000),
    limit: int = Query(10, gt=0, le=100),
):
    get_offered_products_response = BusinessPartnersService(db).get_all_offered_products(search, offset, limit)
    return JSONResponse(content=get_offered_products_response, status_code=200)


@router.get("/products/suggested")
async def get_suggested_product(
    db: Session = Depends(get_db),
    category: Annotated[str | None, Query(max_length=50)] = None,
    sport_id: Annotated[UUID | None, Query()] = None,
):
    suggested_product_filter = (
        SuggestBusinessPartnerProduct(
            category=category,
            sport_id=sport_id,
        )
        if category is not None or sport_id is not None
        else None
    )
    get_suggested_product_response = BusinessPartnersService(db).get_suggested_product(suggested_product_filter)
    return JSONResponse(content=get_suggested_product_response, status_code=200)


@router.get("/products/purchase")
async def get_products_transactions(
    user_id: Annotated[UUID, Header()],
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0, le=1000),
    limit: int = Query(10, gt=0, le=100),
):
    get_product_transactions_response = BusinessPartnersService(db).get_products_transactions(user_id, offset, limit)
    return JSONResponse(content=get_product_transactions_response, status_code=200)


@router.patch("/products/{product_id}")
async def update_business_partner_product(product_id: UUID, update_product: UpdateBusinessPartnerProduct, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    update_product_response = BusinessPartnersService(db).update_business_partner_product(product_id, user_id, update_product)
    return JSONResponse(content=update_product_response, status_code=200)


@router.get("/products/{product_id}")
async def get_business_partner_product(product_id: UUID, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    get_product_response = BusinessPartnersService(db).get_business_partner_product(product_id, user_id)
    return JSONResponse(content=get_product_response, status_code=200)


@router.delete("/products/{product_id}")
async def delete_business_partner_product(product_id: UUID, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    delete_product_response = BusinessPartnersService(db).delete_business_partner_product(
        product_id,
        user_id,
    )
    return JSONResponse(content=delete_product_response, status_code=200)


@router.post("/products/{product_id}/purchase")
async def purchase_product(product_id: UUID, product_purchase: ProductPurchase, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    purchase_product_response = BusinessPartnersService(db).purchase_product(product_id, user_id, product_purchase)
    return JSONResponse(content=purchase_product_response, status_code=200)
