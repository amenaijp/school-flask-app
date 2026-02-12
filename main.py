from flask import Flask, g, render_template
import sqlite3

DATABASE = "./database.db"

app = Flask(__name__)

class MainPageItem:
    def __init__(self, planeName: str, UUID: int, imgLink: str, manufacturerName: str):
        self.planeName = planeName
        self.UUID = UUID
        self.imgLink = imgLink
        self.manufacturerName = manufacturerName

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

@app.route("/")
def home():
    sql = "SELECT PRODUCTS.NAME,PRODUCTS.UUID,PRODUCTS.PHOTOLINK,MANUFACTURER.NAME FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID"
    results = query_db(sql)
    return str(results)

@app.route("/main_page")
def main_page():
    sql = "SELECT PRODUCTS.NAME,PRODUCTS.UUID,PRODUCTS.PHOTOLINK,MANUFACTURER.NAME FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID"
    results = query_db(sql)
    return render_template("main_page.html", results=results)

@app.route("/plane/<int:uuid>")
def plane(uuid):
    sql = f"SELECT PRODUCTS.*,MANUFACTURER.NAME FROM PRODUCTS JOIN MANUFACTURER ON PRODUCTS.MANUFACTURERUUID=MANUFACTURER.UUID WHERE PRODUCTS.UUID={uuid}"
    result = query_db(sql, (), True)
    return str(result)



if __name__ == "__main__":
    app.run(debug=True)