from fastapi import APIRouter

reservation_router = APIRouter(prefix='/reservations')
restaurant_router = APIRouter(prefix='/restaurants')
dish_router = APIRouter(prefix='/dishes')
