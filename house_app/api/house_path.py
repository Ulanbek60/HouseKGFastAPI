from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from house_app.db.models import HouseData
from house_app.db.schema import HouseDataSchema
from house_app.db.database import SessionLocal
from typing import List

house_router = APIRouter(prefix='/house', tags=['House'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@house_router.post('/create', response_model=HouseDataSchema)
async def create_house(house: HouseDataSchema, db: Session = Depends(get_db)):
    house_db = HouseData(**house.dict())
    db.add(house_db)
    db.commit()
    db.refresh(house_db)
    return house_db


@house_router.get('/', response_model=List[HouseDataSchema])
async def get_all_houses(db: Session = Depends(get_db)):
    return db.query(HouseData).all()


@house_router.get('/{house_id}', response_model=HouseDataSchema)
async def get_house_by_id(house_id: int, db: Session = Depends(get_db)):
    house = db.query(HouseData).filter(HouseData.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail='Дом не найден')
    return house


@house_router.put('/{house_id}', response_model=HouseDataSchema)
async def update_house(house_id: int, house: HouseDataSchema, db: Session = Depends(get_db)):
    house_db = db.query(HouseData).filter(HouseData.id == house_id).first()
    if not house_db:
        raise HTTPException(status_code=404, detail='Дом не найден')

    for key, value in house.dict().items():
        setattr(house_db, key, value)

    db.commit()
    db.refresh(house_db)
    return house_db


@house_router.delete('/{house_id}')
async def delete_house(house_id: int, db: Session = Depends(get_db)):
    house = db.query(HouseData).filter(HouseData.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail='Дом не найден')

    db.delete(house)
    db.commit()
    return {"message": "Дом успешно удалён"}
