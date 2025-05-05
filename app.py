import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import requests
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

app = Flask(__name__)

# Load environment variables
load_dotenv()

# API keys
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={location}&aqi=no"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error getting weather for {location}: {response.text}"
    
    data = response.json()
    weather_description = data["current"]["condition"]["text"]
    temperature = data["current"]["temp_c"]
    feels_like = data["current"]["feelslike_c"]
    humidity = data["current"]["humidity"]
    wind_speed = data["current"]["wind_kph"]
    
    return f"Current weather in {location}: {weather_description}. Temperature: {temperature}°C (feels like {feels_like}°C). Humidity: {humidity}%. Wind speed: {wind_speed} km/h."


@tool
def recommend_clothing(weather_description: str, temperature: float) -> str:
    """Recommend clothing based on weather description and temperature."""
    # Define temperature ranges
    cold = temperature < 10
    cool = 10 <= temperature < 18
    mild = 18 <= temperature < 24
    warm = 24 <= temperature < 30
    hot = temperature >= 30
    
    # Check weather conditions
    rainy = any(x in weather_description.lower() for x in ["rain", "drizzle", "shower"])
    snowy = any(x in weather_description.lower() for x in ["snow", "sleet", "hail"])
    windy = "wind" in weather_description.lower()
    sunny = any(x in weather_description.lower() for x in ["sun", "clear", "sunny"])
    
    # Base recommendations
    recommendations = []
    
    # Temperature-based recommendations
    if cold:
        recommendations.extend([
            "Kalın mont veya şişme mont",
            "Termal içlik",
            "Kazak veya polar",
            "Bere",
            "Eldiven",
            "Atkı",
            "Kalın çoraplar",
            "Bot"
        ])
    elif cool:
        recommendations.extend([
            "Hafif mont veya ceket",
            "Kazak veya hafif polar",
            "Uzun kollu gömlek",
            "Kot pantolon veya kumaş pantolon",
            "Hafif atkı (isteğe bağlı)",
            "Kapalı ayakkabı"
        ])
    elif mild:
        recommendations.extend([
            "Hafif hırka veya kazak",
            "Uzun veya kısa kollu gömlek",
            "Pantolon veya kot",
            "Spor ayakkabı veya günlük ayakkabı"
        ])
    elif warm:
        recommendations.extend([
            "Tişört veya kısa kollu gömlek",
            "Hafif pantolon veya şort",
            "Elbise veya etek",
            "Sandalet veya spor ayakkabı",
            "Güneş koruması için hafif şapka"
        ])
    elif hot:
        recommendations.extend([
            "Hafif tişört veya atlet",
            "Şort veya hafif etek",
            "Sandalet",
            "Güneş gözlüğü",
            "Güneş şapkası",
            "Pamuk veya keten gibi nefes alabilen kumaşları tercih edin"
        ])
    
    # Weather condition adjustments
    if rainy:
        recommendations.extend([
            "Yağmurluk veya su geçirmez ceket",
            "Şemsiye",
            "Su geçirmez ayakkabı veya botlar"
        ])
    if snowy:
        recommendations.extend([
            "İyi tutunma sağlayan su geçirmez botlar",
            "Su geçirmez mont ve pantolon",
            "Yalıtımlı eldivenler"
        ])
    if windy:
        recommendations.append("Rüzgar geçirmez ceket")
    if sunny:
        recommendations.extend([
            "Güneş gözlüğü",
            "Güneş kremi",
            "Güneş koruyucu şapka"
        ])
    
    return "Önerilen kıyafetler:\n- " + "\n- ".join(recommendations)


def get_agent():
    # Check if API keys are provided
    if not WEATHERAPI_KEY or not GOOGLE_API_KEY:
        raise Exception("Please set the WEATHERAPI_KEY and GOOGLE_API_KEY environment variables.")
    
    # Initialize LLM with Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Define tools
    tools = [get_weather, recommend_clothing]
    
    # Initialize agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    return agent


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_recommendation', methods=['POST'])
def get_recommendation():
    try:
        data = request.get_json()
        location = data.get('location', '')
        
        if not location:
            return jsonify({"error": "Lütfen bir konum girin."}), 400
        
        agent = get_agent()
        
        # Get weather using agent with Turkish instruction
        response = agent.invoke(
            f"Lütfen {location} için güncel hava durumunu al ve giyilecek uygun kıyafetleri öner. Tüm cevaplarını Türkçe olarak ver. İngilizce yazma, sadece Türkçe kullan."
        )
        
        # Check if response is valid
        if not response or "output" not in response or not response["output"]:
            return jsonify({"error": "Hava durumu alınamadı. Lütfen tekrar deneyin."}), 500
        
        # Add some safeguard for better UI parsing
        output = response["output"]
        if not output.lower().startswith(location.lower()):
            output = f"{location}'da " + output
            
        return jsonify({"response": output})
    except Exception as e:
        return jsonify({"error": f"Bir hata oluştu: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True) 