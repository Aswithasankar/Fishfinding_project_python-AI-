from flask import render_template, Flask, request, jsonify, redirect
from flask_cors import CORS, cross_origin
import os
from predict import fishspecies
import requests
import google.generativeai as genai

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)
@app.route("/", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        first_name = request.form.get("username")
        last_name = request.form.get("password") 
        if first_name == 'admin' and last_name == 'admin':
            return redirect("/home")
    else:
        return render_template("login.html")

@app.route("/home", methods=['GET'])
@cross_origin()
def home():
    if request.method == "GET":
        return render_template('index.html')

@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
   if request.method == "POST":
    image_file = request.files['file']
    print(image_file)
    classifier = fishspecies() 
    result = classifier.FishspeciesPrediction(image_file)
    return result
   else:
       print('Loading Error')

API_KEY = "8ef61edcf1c576d65d836254e11ea420"  # Replace with your API key

@app.route("/weather", methods=["GET", "POST"])
def weather():
    weather_data = None
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
            else:
                weather_data = {"error": "City not found!"}
    return render_template("weather.html", weather=weather_data)

# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyAnMlXs16_Otj7LrYboVUxrtSzehYslpf8"  # Replace with your API Key
genai.configure(api_key=GEMINI_API_KEY)

def predict_fish_price(fish_type, weight, location):
    prompt = f"Predict the market price for {weight}kg of {fish_type} in {location}, India (INR). Consider recent market trends, local demand, and inflation."
    
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)

    if response and response.text:
        price = response.text.strip()  # Extract only the price (assuming model gives a numeric output)
    else:
        price = "N/A"

    return {"fish_type": fish_type, "location": location, "price": price}


@app.route("/market_price", methods=["GET", "POST"])
def market_price():
    prediction_data = None
    if request.method == "POST":
        fish_type = request.form.get("fish_type")
        weight = request.form.get("weight")
        location = request.form.get("location")

        if fish_type and weight and location:
            try:
                weight = float(weight)
                prediction_data = predict_fish_price(fish_type, weight, location)
            except ValueError:
                prediction_data = {"fish_type": fish_type, "location": location, "price": "Invalid weight value!"}

    return render_template("market_price.html", prediction_data=prediction_data)

# Function to get natural fish-rich water bodies in a city
def get_fish_water_bodies(city):
    prompt = f"List the best natural water bodies (ponds, lakes, rivers) in {city}, India, where a large number of fish are available. Only return place names without extra text."

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(prompt)

    if response and response.text:
        places = response.text.strip().split("\n")  # Convert response into a clean list
        return [place.strip() for place in places if place.strip()]
    
    return ["No data available."]

@app.route("/market", methods=["GET", "POST"])
def market():
    places = []
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            places = get_fish_water_bodies(city)

    return render_template("market.html", places=places)

@app.route("/fishing_techniques", methods=["GET", "POST"])
def fishing_techniques():
    return render_template("fishing_techniques.html")

if __name__ == "__main__":
    app.run()