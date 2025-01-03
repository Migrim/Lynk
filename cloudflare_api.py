import requests
from datetime import datetime, timedelta, timezone

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4/graphql"
ZONE_ID = "No" 
API_TOKEN = "HoHoHo"  

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_cloudflare_stats():
    end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")  
    start_date = (datetime.now(timezone.utc) - timedelta(days=60)).strftime("%Y-%m-%d")  

    query = """
    {
      viewer {
        zones(filter: { zoneTag: "%s" }) {
          httpRequests1dGroups(limit: 60, filter: { date_gt: "%s", date_lt: "%s" }) {
            dimensions {
              date
            }
            sum {
              requests
              pageViews
              threats
              bytes
              cachedRequests
              cachedBytes
            }
          }
        }
      }
    }
    """ % (ZONE_ID, start_date, end_date)

    response = requests.post(CLOUDFLARE_API_URL, headers=headers, json={"query": query})

    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            days = data['data']['viewer']['zones'][0]['httpRequests1dGroups']
            daily_stats = []

            for day in days:
                date = day['dimensions']['date']
                totals = day['sum']

                daily_stats.append({
                    "date": date,
                    "requests": totals['requests'],
                    "page_views": totals.get('pageViews', 0),
                    "bandwidth_used": round(totals.get('bytes', 0) / (1024 * 1024), 2),
                    "threats_blocked": totals.get('threats', 0),
                    "cached_requests": totals.get('cachedRequests', 0),
                    "cached_bandwidth": round(totals.get('cachedBytes', 0) / (1024 * 1024), 2)
                })

            daily_stats.sort(key=lambda x: x['date'])

            return fill_missing_dates(daily_stats)
        else:
            print(f"Failed to fetch data: {response.text}")
            return None
    else:
        print(f"Failed to fetch data: {response.status_code}, {response.text}")
        return None

def fill_missing_dates(stats):
    today = datetime.now(timezone.utc)
    last_30_days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 31)]

    stats_by_date = {stat['date']: stat for stat in stats}

    filled_stats = []
    for date in last_30_days:
        if date == (today - timedelta(days=1)).strftime("%Y-%m-%d") and date not in stats_by_date:
            continue
        if date in stats_by_date:
            filled_stats.append(stats_by_date[date])
        else:
            filled_stats.append({
                "date": date,
                "requests": 0,
                "page_views": 0,
                "bandwidth_used": 0,
                "threats_blocked": 0,
                "cached_requests": 0,
                "cached_bandwidth": 0
            })

    filled_stats.sort(key=lambda x: x['date'])
    return filled_stats

if __name__ == "__main__":
    stats = get_cloudflare_stats()
    if stats:
        print("Cloudflare Daily Stats for the last 30 days:")
        for day_stats in stats:
            print(f"Date: {day_stats['date']}, Requests: {day_stats['requests']}, Page Views: {day_stats['page_views']}, Bandwidth Used: {day_stats['bandwidth_used']} MB, Threats Blocked: {day_stats['threats_blocked']}, Cached Requests: {day_stats['cached_requests']}, Cached Bandwidth: {day_stats['cached_bandwidth']} MB")