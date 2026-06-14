import random
import uvicorn
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from jinja2.lexer import integer_re
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session




DATABASE_URL = "mysql+pymysql://root:admin@localhost/mech_flask_demo"


engine = create_engine(DATABASE_URL)

Sessionlocal = sessionmaker(autoflush=False, autocommit= False, bind= engine)

Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key= True, index= True)
    username = Column(String(10), unique= True, index= True)

    mech_type = Column(String(15))

    rating = Column(Integer)


class UserResponse(BaseModel):
    id: int
    username: str
    mech_type: str
    rating: int
    model_config = ConfigDict(from_attributes= True)


class UserCreate(BaseModel):
    username: str
    mech_type: str
    rating: int

app = FastAPI(
    title= "mech pilots api!",
    description= "бэкенд- система управления пилотами боевых роботов"
)


def get_db():
    db = Sessionlocal()

    try:
        yield db

    finally:
        db.close()

@app.get("/pilots", response_model= list[UserResponse])

def get_all_pilots(db: Session = Depends(get_db)):
    pilots = db.query(DBUser).all()
    return pilots


@app.get("/register/random")

def register_random_pilots(db: Session = Depends(get_db)):
    random_id = random.randint(100, 700)
    new_pilot= DBUser(
        username = f"pilot_{random_id}",
        mech_type= "Тестировщик",
        rating = 80
    )
    try:
        db.add(new_pilot)
        db.commit()
        db.refresh(new_pilot)
        return {"status": "success", "message": f"случайный пилот pilot_{random_id} успешно сохранен!"}
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=400, detail= f"ошибка базы данных: {error}")


@app.post("/register", status_code= status.HTTP_201_CREATED)

def create_pilot(user_data: UserCreate, db: Session = Depends(get_db)):
    new_pilot = DBUser(**user_data.model_dump())
    try:
        db.add(new_pilot)
        db.commit()
        return {"status": "success", "message": "Данные успешно записаны в БД"}
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=400, detail = f"ошибка в записи: {error}")


if __name__ == "__main__":
    uvicorn.run("gdfg:app", host= "127.0.0.1", port= 8000, reload= True)

