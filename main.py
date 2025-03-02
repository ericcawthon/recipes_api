from fastapi import FastAPI
app = FastAPI()

import mysql.connector
from dbconfig import config

connection = mysql.connector.connect(**config)
cursor = connection.cursor(dictionary=True)

def lookup_tags(recipe_id):
    select_query = """SELECT t.id, t.tag_name FROM recipes_tags rt
                    LEFT JOIN tags t ON rt.tag_id = t.id 
                    WHERE rt.recipe_id = """ + str(recipe_id) + """ ORDER BY t.tag_name"""
    cursor.execute(select_query)
    results = cursor.fetchall()

    return results

def lookup_notes(recipe_id):
    select_query = """SELECT note, sort_order FROM recipes_notes WHERE recipe_id = """ + str(recipe_id) + """ ORDER BY sort_order"""
    cursor.execute(select_query)
    results = cursor.fetchall()

    return results

def lookup_ingredients(recipe_id):
    select_query = """SELECT ri.sort_order, i.ingredient_name, ri.quantity, uom.uom_name, uom.uom_abbr
                    FROM recipes_ingredients ri 
                    LEFT JOIN ingredients i ON ri.ingredient_id = i.id
                    LEFT JOIN units_of_measure uom ON ri.uom_id = uom.id
                    WHERE ri.recipe_id = """ + str(recipe_id) + """ ORDER BY ri.sort_order"""
    cursor.execute(select_query)
    results = cursor.fetchall()

    return results

def lookup_directions(recipe_id):
    select_query = """SELECT step, direction
                    FROM recipes_steps  
                    WHERE recipe_id = """ + str(recipe_id) + """ ORDER BY step"""
    cursor.execute(select_query)
    results = cursor.fetchall()

    return results

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/tags/")
async def get_tags():
    select_query = """SELECT id, tag_name FROM tags ORDER BY tag_name"""
    cursor.execute(select_query)
    tags = cursor.fetchall()
    return tags

@app.get("/recipes/")
async def get_recipe(tag_id: int | None = None):
    if (tag_id != None):
       select_query = """SELECT r.id, r.rec_name as name FROM recipes r LEFT JOIN recipes_tags rt ON rt.recipe_id = r.id WHERE rt.tag_id = """ + str(tag_id) + """ ORDER BY rec_name"""
    else:
        select_query = """SELECT id, rec_name FROM recipes ORDER BY rec_name"""
    cursor.execute(select_query)
    results = cursor.fetchall()

    return results

@app.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):

    select_query = """SELECT id, rec_name as name FROM recipes WHERE id = """ + str(recipe_id)
    cursor.execute(select_query)
    results = cursor.fetchall()
    rec = results[0]
    rec['tags'] = lookup_tags(rec['id'])
    rec['ingredients'] = lookup_ingredients(rec['id'])
    rec['directions'] = lookup_directions(rec['id'])
    rec['notes'] = lookup_notes(rec['id'])
    rec['reqr_links'] = []
    rec['recd_links'] = []
    return rec
 #   return {"recipe_id": recipe_id, "recipe_name": results[0]['rec_name']}