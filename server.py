from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_KEY = 'f00c38e0279b7bc85480c3fe775d518c'  # Replace with your OpenWeatherMap API key

@app.route('/weather', methods=['GET'])
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({'error': 'Missing coordinates'}), 400

    try:
        # Current weather
        current_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        current_response = requests.get(current_url)
        current_data = current_response.json()

        # 5-day forecast
        forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        return jsonify({
            'current': current_data,
            'forecast': forecast_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)