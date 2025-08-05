from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('OPENWEATHER_API_KEY', '7470b53506f3abb65fa29031a66c5806')  # Fallback to provided key if env var not set

@app.route('/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    # Validate latitude and longitude
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({'error': 'Latitude must be between -90 and 90, longitude between -180 and 180'}), 400
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid or missing coordinates'}), 400

    try:
        # Current weather
        current_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        current_response = requests.get(current_url, timeout=5)
        current_response.raise_for_status()
        current_data = current_response.json()

        # 5-day forecast (3-hour intervals)
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        forecast_response = requests.get(forecast_url, timeout=5)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # Filter forecast to one entry per day (e.g., noon)
        daily_forecast = []
        seen_dates = set()
        for entry in forecast_data.get('list', []):
            date = entry['dt_txt'].split(' ')[0]
            if date not in seen_dates and '12:00:00' in entry['dt_txt']:
                daily_forecast.append(entry)
                seen_dates.add(date)
                if len(daily_forecast) >= 5:  # Limit to 5 days
                    break

        return jsonify({
            'current': current_data,
            'forecast': {'daily': daily_forecast}
        })
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'API request failed: {str(http_err)}'}), 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({'error': f'Network error: {str(req_err)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
