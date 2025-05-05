import os
import requests
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

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
            "Heavy coat or down jacket",
            "Thermal underwear",
            "Sweater or fleece",
            "Warm hat",
            "Gloves",
            "Scarf",
            "Thick socks",
            "Boots"
        ])
    elif cool:
        recommendations.extend([
            "Light jacket or coat",
            "Sweater or light fleece",
            "Long-sleeve shirt",
            "Jeans or pants",
            "Light scarf (optional)",
            "Closed shoes"
        ])
    elif mild:
        recommendations.extend([
            "Light sweater or cardigan",
            "Long or short-sleeve shirt",
            "Pants or jeans",
            "Sneakers or casual shoes"
        ])
    elif warm:
        recommendations.extend([
            "T-shirt or short-sleeve shirt",
            "Light pants or shorts",
            "Dress or skirt",
            "Sandals or sneakers",
            "Light hat for sun protection"
        ])
    elif hot:
        recommendations.extend([
            "Lightweight t-shirt or tank top",
            "Shorts or light skirt",
            "Sandals",
            "Sunglasses",
            "Sun hat",
            "Consider light, breathable fabrics like cotton or linen"
        ])
    
    # Weather condition adjustments
    if rainy:
        recommendations.extend([
            "Raincoat or waterproof jacket",
            "Umbrella",
            "Waterproof shoes or boots"
        ])
    if snowy:
        recommendations.extend([
            "Waterproof boots with good traction",
            "Waterproof jacket and pants",
            "Insulated gloves"
        ])
    if windy:
        recommendations.append("Windbreaker or jacket that blocks wind")
    if sunny:
        recommendations.extend([
            "Sunglasses",
            "Sunscreen",
            "Hat for sun protection"
        ])
    
    return "Recommended clothing:\n- " + "\n- ".join(recommendations)


def parse_weather_for_clothing(weather_info: str) -> dict:
    """Parse weather information to extract temperature and description."""
    try:
        # Extract temperature
        temp_part = weather_info.split("Temperature:")[1].split("°C")[0].strip()
        temperature = float(temp_part)
        
        # Extract weather description
        description_part = weather_info.split("Current weather in")[1].split(":")[1].split(".")[0].strip()
        
        return {
            "temperature": temperature,
            "description": description_part
        }
    except (IndexError, ValueError) as e:
        return {
            "temperature": 20,  # Default value if parsing fails
            "description": "clear sky"  # Default value if parsing fails
        }


def main():
    # Check if API keys are provided
    if not WEATHERAPI_KEY or not GOOGLE_API_KEY:
        print("Please set the WEATHERAPI_KEY and GOOGLE_API_KEY environment variables.")
        return
    
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
    
    print("Hava Durumuna Göre Kıyafet Öneri Ajanı")
    print("--------------------------------------")
    print("Bu ajan, mevcut hava koşullarına göre ne giyileceğine karar vermenize yardımcı olur.")
    
    while True:
        location = input("\nBir konum girin (çıkmak için 'q'): ").strip()
        if location.lower() == 'q':
            break
        
        try:
            # Get weather using agent with Turkish instruction
            response = agent.invoke(
                f"Lütfen {location} için güncel hava durumunu al ve giyilecek uygun kıyafetleri öner. Tüm cevaplarını Türkçe olarak ver. İngilizce yazma, sadece Türkçe kullan."
            )
            print("\nYanıt:", response["output"])
        except Exception as e:
            print(f"Bir hata oluştu: {str(e)}")


if __name__ == "__main__":
    main() 