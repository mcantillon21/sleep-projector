from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hmac
import hashlib
import base64
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for frontend access

# Store latest Whoop data in memory
latest_data = {
    'recovery': None,
    'sleep': None,
    'workout': None,
    'cycle': None
}

# WHOOP credentials from environment variables
CLIENT_ID = os.getenv('WHOOP_CLIENT_ID')
CLIENT_SECRET = os.getenv('WHOOP_CLIENT_SECRET')
ACCESS_TOKEN = os.getenv('WHOOP_ACCESS_TOKEN')
REFRESH_TOKEN = os.getenv('WHOOP_REFRESH_TOKEN')
TOKEN_URL = 'https://api.prod.whoop.com/oauth/oauth2/token'

# Validate required environment variables
def validate_env():
    missing = []
    if not CLIENT_ID:
        missing.append('WHOOP_CLIENT_ID')
    if not CLIENT_SECRET:
        missing.append('WHOOP_CLIENT_SECRET')
    if not ACCESS_TOKEN:
        missing.append('WHOOP_ACCESS_TOKEN')
    if not REFRESH_TOKEN:
        missing.append('WHOOP_REFRESH_TOKEN')
    if missing:
        print(f'⚠️  Missing environment variables: {", ".join(missing)}')
        print('   Copy .env.example to .env and fill in your WHOOP credentials')
        return False
    return True

def refresh_access_token():
    """Refresh the access token using the refresh token"""
    global ACCESS_TOKEN
    try:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': REFRESH_TOKEN,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(TOKEN_URL, data=data)
        if response.status_code == 200:
            token_data = response.json()
            ACCESS_TOKEN = token_data['access_token']
            print(f'✅ Access token refreshed successfully')
            return True
        else:
            print(f'❌ Failed to refresh token: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error refreshing token: {e}')
        return False

def make_whoop_request(url):
    """Make a request to Whoop API with automatic token refresh on 401"""
    global ACCESS_TOKEN
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)

    # If unauthorized, try refreshing token and retry
    if response.status_code == 401:
        print('⚠️  Token expired, refreshing...')
        if refresh_access_token():
            headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
            response = requests.get(url, headers=headers)

    return response

def validate_signature(timestamp, raw_body, signature):
    """Validate the webhook signature from WHOOP"""
    payload = timestamp + raw_body
    calculated = hmac.new(
        CLIENT_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).digest()
    calculated_b64 = base64.b64encode(calculated).decode('utf-8')
    return calculated_b64 == signature

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get signature headers
    timestamp = request.headers.get('X-WHOOP-Signature-Timestamp')
    signature = request.headers.get('X-WHOOP-Signature')
    raw_body = request.get_data(as_text=True)
    
    # Validate signature
    if not validate_signature(timestamp, raw_body, signature):
        print('❌ Invalid signature!')
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Get webhook data
    data = request.get_json()
    
    # Log the webhook event
    print(f'\n🔔 WEBHOOK RECEIVED: {datetime.now().isoformat()}')
    print(f'Type: {data.get("type")}')
    print(f'User ID: {data.get("user_id")}')
    print(f'ID: {data.get("id")}')
    print(f'Trace ID: {data.get("trace_id")}')
    
    # Handle sleep updates
    if data.get('type') == 'sleep.updated':
        print('💤 SLEEP UPDATED - This is the key moment!')

        # Respond quickly (best practice)
        # Then process asynchronously
        sleep_id = data.get('id')

        # Fetch and cache sleep data immediately
        try:
            sleep_data = fetch_sleep_data(sleep_id)
            if sleep_data:
                latest_data['sleep'] = sleep_data
                print_sleep_info(sleep_data)
                print('✅ Sleep data cached for frontend')
        except Exception as e:
            print(f'Error fetching sleep data: {e}')

    elif data.get('type') == 'recovery.updated':
        print('🔋 RECOVERY UPDATED')
        # Fetch latest recovery data
        try:
            url = 'https://api.prod.whoop.com/developer/v2/recovery'
            response = make_whoop_request(url)
            if response.status_code == 200:
                recovery_data = response.json()
                if recovery_data.get('records') and len(recovery_data['records']) > 0:
                    latest_data['recovery'] = recovery_data['records'][0]
                    print('✅ Recovery data cached for frontend')
        except Exception as e:
            print(f'Error fetching recovery: {e}')

    elif data.get('type') == 'workout.updated':
        print('💪 WORKOUT UPDATED')
        # Fetch latest workout data
        try:
            url = 'https://api.prod.whoop.com/developer/v2/activity/workout'
            response = make_whoop_request(url)
            if response.status_code == 200:
                workout_data = response.json()
                if workout_data.get('records') and len(workout_data['records']) > 0:
                    latest_data['workout'] = workout_data['records'][0]
                    print('✅ Workout data cached for frontend')
        except Exception as e:
            print(f'Error fetching workout: {e}')

    # Always respond quickly with 200
    return jsonify({'status': 'ok'}), 200

def fetch_sleep_data(sleep_id):
    """Fetch sleep data from WHOOP API"""
    url = f'https://api.prod.whoop.com/developer/v2/activity/sleep/{sleep_id}'
    response = make_whoop_request(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'❌ API Error: {response.status_code} - {response.text}')
        return None

def print_sleep_info(sleep_data):
    """Print useful sleep information"""
    print('\n📊 SLEEP DATA:')
    print(f"  Sleep ID: {sleep_data.get('id')}")
    print(f"  Start: {sleep_data.get('start')}")
    print(f"  End: {sleep_data.get('end')}")
    print(f"  Score State: {sleep_data.get('score_state')}")
    print(f"  Is Nap: {sleep_data.get('nap')}")
    
    score = sleep_data.get('score')
    if score:
        stage_summary = score.get('stage_summary', {})
        print('\n  Sleep Stages:')
        print(f"    Total in Bed: {stage_summary.get('total_in_bed_time_milli', 0) / 1000 / 60:.1f} min")
        print(f"    Awake: {stage_summary.get('total_awake_time_milli', 0) / 1000 / 60:.1f} min")
        print(f"    Light Sleep: {stage_summary.get('total_light_sleep_time_milli', 0) / 1000 / 60:.1f} min")
        print(f"    Deep Sleep (SWS): {stage_summary.get('total_slow_wave_sleep_time_milli', 0) / 1000 / 60:.1f} min")
        print(f"    REM Sleep: {stage_summary.get('total_rem_sleep_time_milli', 0) / 1000 / 60:.1f} min")
        print(f"    Sleep Cycles: {stage_summary.get('sleep_cycle_count')}")
        print(f"    Disturbances: {stage_summary.get('disturbance_count')}")
        
        if score.get('sleep_efficiency_percentage'):
            print(f"\n  Sleep Efficiency: {score.get('sleep_efficiency_percentage'):.1f}%")
        if score.get('respiratory_rate'):
            print(f"  Respiratory Rate: {score.get('respiratory_rate'):.1f} breaths/min")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, etc)"""
    return send_from_directory('.', path)

# API Endpoints for frontend
@app.route('/api/recovery', methods=['GET'])
def get_recovery():
    """Get latest recovery data"""
    if not latest_data['recovery']:
        # Fetch fresh data from Whoop API
        try:
            url = 'https://api.prod.whoop.com/developer/v2/recovery'
            response = make_whoop_request(url)
            if response.status_code == 200:
                data = response.json()
                # Get most recent recovery
                if data.get('records') and len(data['records']) > 0:
                    latest_data['recovery'] = data['records'][0]
        except Exception as e:
            print(f'Error fetching recovery: {e}')

    return jsonify(latest_data['recovery']) if latest_data['recovery'] else jsonify({}), 200

@app.route('/api/sleep', methods=['GET'])
def get_sleep():
    """Get latest sleep data"""
    if not latest_data['sleep']:
        # Fetch fresh data from Whoop API
        try:
            url = 'https://api.prod.whoop.com/developer/v2/activity/sleep'
            response = make_whoop_request(url)
            if response.status_code == 200:
                data = response.json()
                # Get most recent sleep
                if data.get('records') and len(data['records']) > 0:
                    latest_data['sleep'] = data['records'][0]
        except Exception as e:
            print(f'Error fetching sleep: {e}')

    return jsonify(latest_data['sleep']) if latest_data['sleep'] else jsonify({}), 200

@app.route('/api/workout', methods=['GET'])
def get_workout():
    """Get latest workout data"""
    if not latest_data['workout']:
        # Fetch fresh data from Whoop API
        try:
            url = 'https://api.prod.whoop.com/developer/v2/activity/workout'
            response = make_whoop_request(url)
            if response.status_code == 200:
                data = response.json()
                # Get most recent workout
                if data.get('records') and len(data['records']) > 0:
                    latest_data['workout'] = data['records'][0]
        except Exception as e:
            print(f'Error fetching workout: {e}')

    return jsonify(latest_data['workout']) if latest_data['workout'] else jsonify({}), 200

@app.route('/api/cycle', methods=['GET'])
def get_cycle():
    """Get latest cycle (day strain) data"""
    if not latest_data['cycle']:
        # Fetch fresh data from Whoop API
        try:
            url = 'https://api.prod.whoop.com/developer/v2/cycle'
            response = make_whoop_request(url)
            if response.status_code == 200:
                data = response.json()
                # Get most recent cycle
                if data.get('records') and len(data['records']) > 0:
                    latest_data['cycle'] = data['records'][0]
        except Exception as e:
            print(f'Error fetching cycle: {e}')

    return jsonify(latest_data['cycle']) if latest_data['cycle'] else jsonify({}), 200

@app.route('/api/refresh', methods=['POST'])
def refresh_all_data():
    """Manually refresh all Whoop data"""
    try:
        # Fetch all data types
        endpoints = {
            'recovery': 'https://api.prod.whoop.com/developer/v2/recovery',
            'sleep': 'https://api.prod.whoop.com/developer/v2/activity/sleep',
            'workout': 'https://api.prod.whoop.com/developer/v2/activity/workout',
            'cycle': 'https://api.prod.whoop.com/developer/v2/cycle'
        }

        for data_type, url in endpoints.items():
            response = make_whoop_request(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('records') and len(data['records']) > 0:
                    latest_data[data_type] = data['records'][0]

        return jsonify({'status': 'success', 'timestamp': datetime.now().isoformat()}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def fetch_initial_data():
    """Fetch initial Whoop data on startup"""
    print('\n🔄 Fetching initial Whoop data...')
    try:
        # Fetch all data types
        endpoints = {
            'recovery': 'https://api.prod.whoop.com/developer/v2/recovery',
            'sleep': 'https://api.prod.whoop.com/developer/v2/activity/sleep',
            'workout': 'https://api.prod.whoop.com/developer/v2/activity/workout',
            'cycle': 'https://api.prod.whoop.com/developer/v2/cycle'
        }

        for data_type, url in endpoints.items():
            try:
                response = make_whoop_request(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('records') and len(data['records']) > 0:
                        latest_data[data_type] = data['records'][0]
                        print(f'  ✅ {data_type.capitalize()} data loaded')
                    else:
                        print(f'  ⚠️  No {data_type} records found')
                else:
                    print(f'  ❌ Failed to fetch {data_type}: {response.status_code}')
            except Exception as e:
                print(f'  ❌ Error fetching {data_type}: {e}')

        print('✨ Initial data fetch complete!\n')
    except Exception as e:
        print(f'❌ Error during initial data fetch: {e}\n')

if __name__ == '__main__':
    print('🎧 WHOOP Webhook Server Starting...')

    # Validate environment variables
    if not validate_env():
        print('❌ Server cannot start without required credentials')
        exit(1)

    print(f'🔐 Using client ID: {CLIENT_ID[:8]}...')
    print('📡 Listening for webhooks on http://localhost:5001/webhook')

    # Fetch initial data before starting server
    fetch_initial_data()

    # Run the server
    app.run(host='0.0.0.0', port=5001, debug=True)