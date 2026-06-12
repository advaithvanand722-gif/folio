import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

def get_weather(city="Thiruvananthapuram"):
    """Fetch weather data from OpenWeatherMap API."""
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        return None, "Error: OWM_API_KEY environment variable is missing."
        
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        weather_main = data["weather"][0]["main"].lower()
        weather_desc = data["weather"][0]["description"].lower()
        
        # Condition detection
        is_raining = "rain" in weather_main or "drizzle" in weather_main
        is_hot = temp > 35
        
        return {
            "temp": temp,
            "desc": weather_desc,
            "is_raining": is_raining,
            "is_hot": is_hot,
            "city": city
        }, None
        
    except Exception as e:
        return None, f"Weather API error: {e}"

def send_email_alert(weather_data):
    """Send an automated alert using Gmail SMTP."""
    sender_email = os.getenv("ALERT_EMAIL")
    sender_password = os.getenv("ALERT_EMAIL_PASSWORD") 
    receiver_email = os.getenv("RECEIVER_EMAIL")
    
    if not all([sender_email, sender_password, receiver_email]):
        print("Missing email credentials. Skipping email delivery.")
        return

    subject = f"⚠️ Weather Alert: Extreme Conditions in {weather_data['city']}"
    body = f"""
Weather conditions crossed your safety thresholds on {date.today().strftime('%A, %d %B %Y')}.

Current Temperature: {weather_data['temp']}°C
Current Status: {weather_data['desc'].capitalize()}

Action Recommended: Take umbrellas or avoid peak afternoon sun exposure.
    """
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"SMTP Transmission failure: {e}")

def run():
    print("Initiating daily evaluation...")
    weather_data, error = get_weather()
    
    if error:
        print(error)
        return
        
    print(f"Metrics parsed for {weather_data['city']}: {weather_data['temp']}°C, {weather_data['desc']}")
    
    if weather_data["is_hot"] or weather_data["is_raining"]:
        print("Threshold breached! Initializing email alert dispatch...")
        send_email_alert(weather_data)
    else:
        print("Weather conditions stable. No alerts necessary.")

if __name__ == "__main__":
    run()