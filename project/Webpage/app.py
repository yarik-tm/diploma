from typing import Counter
from flask import Flask, render_template, redirect, url_for, request, jsonify
from joblib import dump, load
from pickle import dump as dump_p, load as load_p
from flask_cors import CORS, cross_origin
import json
from pprint import pprint
import datetime
import pandas as pd

# For SQL Connect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, insert



Base = automap_base()

engine = create_engine('postgresql://postgres:rootroot@[::1]:5432/userdb')

Base.prepare(engine, reflect=True)
#Base.prepare(engine, autoload_with=engine)


app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_ORIGINS'] = '*'
app.config['DEBUG'] = True

@app.get('/')
def index():
   return render_template("index.html")

@app.get('/about')
def about_page():
   return render_template("about.html")

@app.get('/create')
def create_page():
   return render_template("create.html")

@app.get('/add_data')
def add_data_page():
   return render_template("add_data.html")

@app.get('/map')
def map_page():
   return render_template("map.html")

@app.route('/imaginary_country/<econ_gdp>/<life_exp>/<freedom>/<govt_trust>/<generosity>')
def get_pred_happiness(econ_gdp, life_exp, freedom, govt_trust, generosity):
      
   
   # inverse scale happiness score with happiness scaler, store in variable
   # check if happiness is unhappy, happy, etc
   # return unscaled happiness score and qualitative result


   # Setting happiness levels
   unhappy = 2.523 #"Unhappy"
   low_happy = 3.85275 #"Low Happiness"
   mod_happy = 5.182499999999999 #"Moderately Happy"
   happy = 6.51225 #"Happy"
   ext_happy = 7.842 #"Extremely Happy"

   # LinRegress coeffs determined from Jupyter notebook
   coef_gdp = 1.211244050635855 
   coef_life = 1.707979044319649 
   coef_freedom = 1.9806188129473845 
   coef_corrupt = 1.9806188129473845 
   coef_generosity = 0.6536659939512272 
   intercept = 2.33466608

   # determine predicted happiness
   prediction = (float(econ_gdp)/40.0)*coef_gdp + (float(life_exp)/40.0)*coef_life + (float(freedom)/40.0)*coef_freedom + (float(govt_trust)/40.0)*coef_corrupt + (float(generosity)/40.0)*coef_generosity + intercept
   
   # Detemine happiness level
   if prediction > happy:
      hap_level = "Extremely Happy"
   elif prediction > mod_happy:
      hap_level = "Happy"
   elif prediction > low_happy:
      hap_level = "Moderately Happy"
   elif prediction > unhappy:
      hap_level = "Low Happiness"
   else:
      hap_level = "Unhappy"


   # determine nearest country by happiness score
   with open('static/data/country_happiness_score.json') as f:
      data = json.load(f)
   nearest = "USA"
   start = 10
   for i in data:
      print(i["country"])

      delta = prediction - float(i["happiness_score"])

      if abs(delta) < start:
         start = abs(delta)
         nearest = i["country"]
   


   response = {"prediction": round(prediction, 2), "level": hap_level, "nearest": nearest}


   return jsonify(response)


@app.route('/FTM/<cntry>/<howhapp>/<frdm>/<govt_trust>/<generosity>')
def store_FTM(cntry, howhapp, frdm, govt_trust, generosity):

   print(cntry, howhapp, frdm, govt_trust, generosity)
   try:
      
      conn = engine.connect()
      
      year = datetime.date.today().year

    
      # no column specification needed if all columns are inserted
      stmt = f"INSERT INTO feed_the_machine VALUES ('{cntry}', {frdm}, {govt_trust}, {generosity}, {year}, {howhapp});"

      conn.execute(stmt)

      message = 'Your information has been recorded'
   except:
      message = 'An error occured'
   

   # store countries only for dropdown
   with open('static\data\country_happiness_score.json') as f:
      data = json.load(f)

   countries = []
   for key in data:
      #store unique countries only
      if key not in countries:
         countries.append(key)


   response = {"message": message, "countries": countries}

   return jsonify(response)

@app.route('/postmethod', methods = ['POST', 'GET'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    print(jsdata)
    return jsdata

def time_plot(country):
        time_df = pd.read_sql(f"SELECT country, happiness_score, year FROM public.happiness_data", con=engine)
        x_data = time_df[time_df["country"] == country]["year"]
        print(x_data)
        y_data = y_data = time_df[time_df["country"] == country]["happiness_score"]
        time_dict = {
            "country": country,
            "x_data": x_data,
            "y_data": y_data
        }
        return(time_dict)

@app.route("/line_plot/<country>")
def Line_plot(country):
    data = time_plot(country)
    response ={
        "country": country,
        "x_data": list(data["x_data"]),
        "y_data": list(data["y_data"])
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)