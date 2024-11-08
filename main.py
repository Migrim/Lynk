from flask import Flask, render_template, jsonify
import time
from datetime import datetime
import psutil

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

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    # Placeholder for simulated server stats
    server_stats = [
        {'page_views': 200, 'requests': 150, 'bandwidth_used': 500.5, 'threats_blocked': 3,
         'cached_requests': 100, 'cached_bandwidth': 300.25},
        {'page_views': 250, 'requests': 180, 'bandwidth_used': 550.75, 'threats_blocked': 5,
         'cached_requests': 120, 'cached_bandwidth': 350.50}
    ]

    first_day = server_stats[0]
    last_day = server_stats[-1]

    percentage_change = {
        'page_views': calculate_percentage_change(first_day['page_views'], last_day['page_views']),
        'requests': calculate_percentage_change(first_day['requests'], last_day['requests']),
        'bandwidth_used': calculate_percentage_change(first_day['bandwidth_used'], last_day['bandwidth_used']),
        'threats_blocked': calculate_percentage_change(first_day['threats_blocked'], last_day['threats_blocked']),
        'cached_requests': calculate_percentage_change(first_day['cached_requests'], last_day['cached_requests']),
        'cached_bandwidth': calculate_percentage_change(first_day['cached_bandwidth'], last_day['cached_bandwidth'])
    }

    total_stats = {
        'total_page_views': format_requests(sum(entry['page_views'] for entry in server_stats)),
        'total_requests': format_requests(sum(entry['requests'] for entry in server_stats)),
        'total_bandwidth_used': round(sum(entry['bandwidth_used'] for entry in server_stats), 2),
        'total_threats_blocked': sum(entry['threats_blocked'] for entry in server_stats),
        'total_cached_requests': format_requests(sum(entry['cached_requests'] for entry in server_stats)),
        'total_cached_bandwidth': round(sum(entry['cached_bandwidth'] for entry in server_stats), 2)
    }

    system_stats = {
        'cpu_usage': psutil.cpu_percent(),
        'ram_usage': psutil.virtual_memory().percent,
        'storage_usage': psutil.disk_usage('/').percent
    }

    return render_template('dashboard.html', cloudflare_stats=server_stats, total_stats=total_stats, percentage_change=percentage_change, system_stats=system_stats)

@app.route('/admin/system_stats', methods=['GET'])
def get_system_stats():
    cpu_usage_per_core = psutil.cpu_percent(interval=1.5, percpu=True)  # Slightly longer interval for accuracy
    cpu_usage = round(sum(cpu_usage_per_core) / len(cpu_usage_per_core), 1)  # Average and round to one decimal place

    system_stats = {
        'cpu_usage': f"{cpu_usage:.1f}",  # Format to 00.0%
        'ram_usage': round(psutil.virtual_memory().percent, 1),  # Rounded to one decimal
        'storage_usage': round(psutil.disk_usage('/').percent, 1)  # Rounded to one decimal
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
