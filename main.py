from typing import Optional, List

from fastapi import FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select


# class Hero(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     secret_name: str
#     age: Optional[int] = Field(default=None, index=True)
    
    
# class HeroCreate(SQLModel):
#     name : str
#     age : Optional[int]
    
# class HeroRead(SQLModel):
    # id : int
    # name: str
    # age: Optional[int]


# Inheritance type

class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)
    
class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
class HeroCreate(HeroBase):
    pass 

class HeroRead(HeroBase):
    id : int
    
class HeroUpdate(HeroBase):
    name : Optional[str] = None
    age : Optional[int] = None


url = "mysql://root@127.0.0.1:3306/modelfastapi"

engine = create_engine(url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# @app.post("/heroes/", response_model=HeroRead)
# def create_hero(hero: Hero):
#     with Session(engine) as session:
#         session.add(hero)
#         session.commit()
#         session.refresh(hero)
#         return hero


@app.post("/heroes/", response_model=HeroRead)
def create_hero(hero: HeroCreate):
    with Session(engine) as session:
        db_hero = Hero.from_orm(hero)
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero


@app.get("/heroes/", response_model=List[HeroRead])
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        if not heroes:
            raise HTTPException(status_code=404, detail="No datas found")
        return heroes

@app.get("/heroes/{hero_id}", response_model=HeroRead)
def read_hero(hero_id : int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="detail not found")
        return hero
    
@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(hero_id : int, hero : HeroUpdate):
    with Session(engine) as session:
        db_hero = session.get(Hero, hero_id)
        if not db_hero:
            raise HTTPException(status_code=404, detail="Data Not Found")
        
        hero_data = hero.dict(exclude_unset=True)
        for key,value in hero_data.items():
            setattr (db_hero, key, value)
            
        session.add(db_hero)
        session.commit()
        session.refresh(db_hero)
        return db_hero
    
    
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id : int):
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Data Not Found")
        session.delete(hero)
        session.commit()
        return {"ok": True}
        