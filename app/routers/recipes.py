from fastapi import APIRouter, status, Query
from typing import List
import pandas as pd
from pydantic import BaseModel
from loguru import logger
import time

current_time = round(time.time())
logger.add(f'runtime_{current_time}.log')
router = APIRouter()

json = {
  "id": "string",
  "name": "имя",
  "list_ingrid": "string",
  "image_url": "string",
  "list_resipe": "string",
  "ingridient_keywords": [
    "string"
  ],
  "cal": 0,
  "protein": 0,
  "carb": 0,
  "recept_link": "string",
  "fats": 0,
  "difficulty": "string"
}


def calc_diff(row):
    diff = len(row['ingridient_keywords']) + len(row['list_resipe'])
    if diff > 820:  # new_df['difficulty'].mean()
        return 'hard'
    else:
        return 'simple'


logger.info('Готовы к новым рецептам!')
df = pd.read_csv('eda.csv')
df['difficulty'] = df.apply(lambda row: calc_diff(row), axis=1)


class Recipe(BaseModel):
    id: str
    name: str
    list_ingrid: str
    image_url: str
    list_resipe: str
    ingridient_keywords: list
    cal: int
    protein: int
    carb: int
    recept_link: str
    fats: int
    difficulty: str


@router.get('/recipes/')
def search_recipe(query: str):
    logger.info(f'Поиск: "{query}"')
    mask = df['name'].apply(lambda x: query in x)
    return df[mask].to_dict(orient='index')


@router.get('/recipes/{recipe_id}')
def fetch_recipe(recipe_id: str) -> dict:
    logger.info(f'Поиск id: "{recipe_id}"')
    mask = df['id'].apply(lambda x: recipe_id in x)
    return df[mask].to_dict(orient='index')


@router.get('/recipes/get/random')
def random_recipe():
    logger.info(f'Выдан случайный рецепт')
    return df.sample(1).iloc[0].to_dict()


@router.get('/recipes/diet/')
def cal_recipe(calories: int, topn: int):
    logger.info(f'Поиск по калорийности: "{calories}"')
    all_rec = df.loc[df['cal'] <= calories].sort_values(by='cal')
    rec_list = all_rec.head(topn).to_dict(orient='index')
    return rec_list


@router.get('/recipes/get/difficulty')
def recipes_diff(difficulty: str, topn: int):
    logger.info(f'Поиск по сложности: "{difficulty}"')
    new_df = df[df['difficulty'] == difficulty]
    return new_df.head(topn).to_dict(orient='index')


@router.put('/recipes/new/')
def add_recipe(recipe_json: Recipe):
    recipe_dict = recipe_json.dict()
    recipe_name = recipe_dict['name']
    logger.info(f'Добавлен новый рецепт: "{recipe_name}"')
    series = pd.Series(recipe_dict.values(), index=df.columns)
    df.loc[-1] = recipe_dict.values()

    #проверка
    #mask = df['name'].apply(lambda x: recipe_dict['name'] in x)
    #return df[mask].to_dict(orient='index')
    return df.iloc[-1].to_dict()


@router.post('/recipes/search_by_ingredients/')
def find_by_ingredients(ingredients: List[str] = Query(None)):
    logger.info(f'Поиск по ингредиентам: "{ingredients}"')
    mask = df['list_ingrid'].apply(lambda x: all(ingredient in x.lower() for ingredient in ingredients))
    return df[mask].head(5).to_dict(orient='index')
