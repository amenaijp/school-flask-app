from flask import Flask, g, render_template
import sqlite3
from typing import List

DATABASE = "./database.db"

app = Flask(__name__)

class MainPageItem:
    def __init__(self, planeName: str, UUID: int, imgLink: str, manufacturerName: str, manufacturerUUID: int):
        self.planeName = planeName
        self.UUID = UUID
        self.imgLink = imgLink
        self.manufacturerName = manufacturerName
        self.manufacturerUUID = manufacturerUUID

    def from_tuple(args):
        return MainPageItem(*args)

class SpecificPlaneItem:
    def __init__(self, planeName: str, description: str, creationYear: str, planeUUID: int, manufacturerUUID: int, imgLink: str, manufacturerName: str):
        self.planeName = planeName
        self.description = description
        self.creationYear = creationYear
        self.planeUUID = planeUUID
        self.manufacturerUUID = manufacturerUUID
        self.imgLink = imgLink
        self.manufacturerName = manufacturerName

class SpecificManufacturer:
    def __init__(self, manufacturerName: str, description: str, foundingYear: int, _uuid: int, logoLink: str, planes: List[SpecificPlaneItem]):
        self.manufacturerName = manufacturerName
        self.description = description
        self.foundingYear = foundingYear
        self.logoLink = logoLink
        self.planes = planes

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/main_page")
def main_page():
    sql = "SELECT PRODUCTS.NAME,PRODUCTS.UUID,PRODUCTS.PHOTOLINK,MANUFACTURER.NAME,PRODUCTS.MANUFACTURERUUID FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID"
    results = query_db(sql)
    results = list(map(MainPageItem.from_tuple, results))
    return render_template("main_page.html", results=results)

@app.route("/plane/<int:uuid>")
def plane(uuid):
    sql = f"SELECT PRODUCTS.*,MANUFACTURER.NAME FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID WHERE PRODUCTS.UUID={uuid}"
    result = query_db(sql, (), True)
    result = SpecificPlaneItem(*result)
    return render_template("aircraft.html", result=result)

@app.route("/manufacturer/<int:uuid>")
def manufacturer(uuid):
    sql = f"SELECT * FROM MANUFACTURER WHERE MANUFACTURER.UUID={uuid}"
    result_manufacturer = query_db(sql, (), True)
    sql = f"SELECT PRODUCTS.NAME,PRODUCTS.UUID,PRODUCTS.PHOTOLINK,MANUFACTURER.NAME,PRODUCTS.MANUFACTURERUUID FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID WHERE PRODUCTS.MANUFACTURERUUID={uuid}"
    result_planes = list(map(MainPageItem.from_tuple, query_db(sql)))
    result = SpecificManufacturer(*result_manufacturer, result_planes)
    return render_template("manufacturer.html", result=result)



if __name__ == "__main__":
    app.run(debug=True)