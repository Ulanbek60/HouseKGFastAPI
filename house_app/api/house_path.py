from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from house_app.db.models import HouseData
from house_app.db.schema import HouseDataSchema
from house_app.db.database import SessionLocal
from typing import List
import joblib
import os
import numpy as np
import pandas as pd
from pathlib  import Path
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression


BASE_DIR = Path(__file__).resolve().parent.parent.parent


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


model_path = BASE_DIR / 'house_price_model_job.pkl'
scaler_path = BASE_DIR / 'scaler.pkl'

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

model_features = [
  "GrLivArea",
  "YearBuilt",
  "GarageCars",
  "TotalBsmtSF",
  "FullBath",
  "OverallQual",
  "Neighborhood",
]

@house_router.post('/predict/')
async def predict_price(house: HouseDataSchema, db: Session = Depends(get_db)):
    input_data = {
        "GrLivArea": house.GrLivArea,
        "YearBuilt": house.YearBuilt,
        "GarageCars": house.GarageCars,
        "TotalBsmtSF": house.TotalBsmtSF,
        "FullBath": house.FullBath,
        "OverallQual": house.OverallQual
    }
    input_df = pd.DataFrame([input_data])

    input_scaled = scaler.transform(input_df)
    predicted_price  = model.predict(input_scaled)[0]
    return {'predicted_price: ': round(predicted_price )}

