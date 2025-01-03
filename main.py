from flask import Flask, render_template, jsonify
import time
from datetime import datetime
from cloudflare_api import get_cloudflare_stats  
import psutil
from crypto_prices import get_crypto_prices, get_historical_data

app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

def calculate_percentage_change(start_value, end_value):
    if start_value == 0:
        return 0
    return round(((end_value - start_value) / start_value) * 100, 2)

def format_requests(number):
    if number >= 1000:
        number_in_k = number / 1000
        return f"{number_in_k:.3f}k"
    else:
        return str(number)

@app.route('/crypto/<coin_id>/history')
def crypto_history(coin_id):
    historical_data = get_historical_data(coin_id)
    return jsonify(historical_data)

@app.route('/admin/crypto')
def admin_crypto():
    data = get_crypto_prices()
    return jsonify(data)

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

def calculate_percentage_change(old_value, new_value):
    if old_value == 0:
        return 0
    return round(((new_value - old_value) / old_value) * 100, 2)

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    crypto_stats = get_crypto_prices()

    previous_prices = {
        'btc_price': 50000,  
        'eth_price': 4000,   
        'sol_price': 100    
    }

    crypto_percentage_change = {
        'btc_price': calculate_percentage_change(previous_prices['btc_price'], crypto_stats.get('current_btc_price', 0)),
        'eth_price': calculate_percentage_change(previous_prices['eth_price'], crypto_stats.get('current_eth_price', 0)),
        'sol_price': calculate_percentage_change(previous_prices['sol_price'], crypto_stats.get('current_sol_price', 0))
    }

    cloudflare_stats = get_cloudflare_stats()

    if cloudflare_stats and len(cloudflare_stats) >= 2: 
        yesterday = cloudflare_stats[-2] 
        today = cloudflare_stats[-1] 

        percentage_change = {
            'page_views': calculate_percentage_change(yesterday['page_views'], today['page_views']),
            'requests': calculate_percentage_change(yesterday['requests'], today['requests']),
            'bandwidth_used': calculate_percentage_change(yesterday['bandwidth_used'], today['bandwidth_used']),
            'threats_blocked': calculate_percentage_change(yesterday['threats_blocked'], today['threats_blocked']),
            'cached_requests': calculate_percentage_change(yesterday['cached_requests'], today['cached_requests']),
            'cached_bandwidth': calculate_percentage_change(yesterday['cached_bandwidth'], today['cached_bandwidth'])
        }

        total_stats = {
            'total_page_views': format_requests(sum(entry['page_views'] for entry in cloudflare_stats)),
            'total_requests': format_requests(sum(entry['requests'] for entry in cloudflare_stats)),
            'total_bandwidth_used': round(sum(entry['bandwidth_used'] for entry in cloudflare_stats), 2),
            'total_threats_blocked': sum(entry['threats_blocked'] for entry in cloudflare_stats),
            'total_cached_requests': format_requests(sum(entry['cached_requests'] for entry in cloudflare_stats)),
            'total_cached_bandwidth': round(sum(entry['cached_bandwidth'] for entry in cloudflare_stats), 2)
        }

        system_stats = {
            'cpu_usage': psutil.cpu_percent(),
            'ram_usage': psutil.virtual_memory().percent,
            'storage_usage': psutil.disk_usage('/').percent
        }

        return render_template('dashboard.html', cloudflare_stats=cloudflare_stats, total_stats=total_stats, percentage_change=percentage_change, system_stats=system_stats, crypto_stats=crypto_stats, crypto_percentage_change=crypto_percentage_change)

    else:
        placeholder_stats = {
            'total_page_views': 0,
            'total_requests': 0,
            'total_bandwidth_used': 0.00,
            'total_threats_blocked': 0,
            'total_cached_requests': 0,
            'total_cached_bandwidth': 0.00
        }
        placeholder_change = {
            'page_views': 0,
            'requests': 0,
            'bandwidth_used': 0,
            'threats_blocked': 0,
            'cached_requests': 0,
            'cached_bandwidth': 0
        }

        system_stats = {
            'cpu_usage': 0,
            'ram_usage': 0,
            'storage_usage': 0
        }

        return render_template('dashboard.html', cloudflare_stats=[placeholder_stats], total_stats=placeholder_stats, percentage_change=placeholder_change, system_stats=system_stats, crypto_stats=crypto_stats, crypto_percentage_change=crypto_percentage_change, error="Failed to retrieve Cloudflare data or insufficient data")

@app.route('/admin/system_stats', methods=['GET'])
def get_system_stats():
    cpu_usage_per_core = psutil.cpu_percent(interval=1.5, percpu=True)  
    cpu_usage = round(sum(cpu_usage_per_core) / len(cpu_usage_per_core), 1) 

    system_stats = {
        'cpu_usage': f"{cpu_usage:.1f}",  
        'ram_usage': round(psutil.virtual_memory().percent, 1),  
        'storage_usage': round(psutil.disk_usage('/').percent, 1)  
    }
    return jsonify(system_stats)

@app.route('/admin/uptime')
def get_uptime():
    uptime_seconds = psutil.boot_time()
    current_time = time.time()
    uptime = current_time - uptime_seconds

    uptime_days = int(uptime // (24 * 3600))
    uptime %= (24 * 3600)
    uptime_hours = int(uptime // 3600)
    uptime %= 3600
    uptime_minutes = int(uptime // 60)

    return jsonify({
        'days': uptime_days,
        'hours': uptime_hours,
        'minutes': uptime_minutes
    })

@app.route('/admin/server_time')
def get_server_time():
    current_time = datetime.now().strftime('%H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')
    return jsonify({'time': current_time, 'date': current_date})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
