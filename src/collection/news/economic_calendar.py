import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from utils import save_to_json

def fetch_page_source(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch the page... CODE: {response.status_code}")


def parse_content(html, current_month, current_year):
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"Page Title: {soup.title.string.strip()}")

    calendar_rows = soup.find_all('tr', class_='calendar__row')
    print(f"Found {len(calendar_rows)} calendar rows")

    data = []
    current_date = None
    current_time = None
    last_date = None
    last_time = None

    for row in calendar_rows:
        try:
            date_td = row.find('td', class_='calendar__cell calendar__date')
            if date_td:
                current_date = date_td.get_text(strip=True).split()[-1] 
            # Extract time
            time_td = row.find('td', class_='calendar__cell calendar__time')
            if time_td:
                current_time = time_td.get_text(strip=True)
                if current_time == "All Day":
                    current_time = "00:00AM"

            if not current_date:
                current_date = last_date
            if not current_time:
                current_time = last_time


            date_time_str = f"{current_month} {current_date} {current_time}"
            try:
                date_time_obj = datetime.strptime(date_time_str, '%b %d %I:%M%p')
            except ValueError:
                date_time_obj = datetime.strptime(date_time_str, '%b %d %I:%M %p')
            formatted_date_time = date_time_obj.replace(year=current_year).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


            last_date = current_date
            last_time = current_time

            currency_td = row.find('td', class_='calendar__cell calendar__currency')
            currency_text = currency_td.get_text(strip=True) if currency_td else 'N/A'

            impact_td = row.find('td', class_='calendar__cell calendar__impact')
            impact_text = 'N/A'
            if impact_td:
                impact_span = impact_td.find('span', class_='icon')
                if impact_span:
                    impact_class = impact_span.get('class', [])
                    if 'icon--ff-impact-red' in impact_class:
                        impact_text = 'high'
                    elif 'icon--ff-impact-ora' in impact_class:
                        impact_text = 'medium'
                    elif 'icon--ff-impact-yel' in impact_class:
                        impact_text = 'low'

            # Apply filters for impact and currency
            if impact_text in ['high', 'medium'] and currency_text in ['EUR', 'USD']:
                event_detail = row.find('td', class_='calendar__cell calendar__event')
                event_text = event_detail.get_text(strip=True) if event_detail else 'N/A'

                actual = row.find('td', class_='calendar__cell calendar__actual')
                actual_text = actual.get_text(strip=True) if actual else 'N/A'

                forecast = row.find('td', class_='calendar__cell calendar__forecast')
                forecast_text = forecast.get_text(strip=True) if forecast else 'N/A'

                previous = row.find('td', class_='calendar__cell calendar__previous')
                previous_text = previous.get_text(strip=True) if previous else 'N/A'
                
                data.append({
                    "time": formatted_date_time,
                    "currency": currency_text,
                    "impact": impact_text,
                    "event": event_text,
                    "actual": actual_text,
                    "forecast": forecast_text,
                    "previous": previous_text
                })

        except Exception as e:
            print(f"Error processing the data... {e}")

    return data

def generate_month_list(start_date, end_date):
    start = datetime.strptime(start_date, "%b%Y")
    end = datetime.strptime(end_date, "%b%Y")
    months = []
    while start <= end:
        months.append(start.strftime("%b-%Y").split('-'))
        start = datetime(start.year + (start.month // 12), ((start.month % 12) + 1), 1)
    return months

# Function to fetch and save economic calendar data for multiple months
def fetch_and_save_calendar_data(start_date, end_date, output_filename):
    months = generate_month_list(start_date, end_date)
    all_data = []
    for month, year in months:
        url = f"https://www.forexfactory.com/calendar?month={month.lower()}.{year}"
        print(f"Fetching data from URL: {url}")
        page_source = fetch_page_source(url)
        data = parse_content(page_source, month, int(year))
        all_data.extend(data)

    if all_data:
        save_path = os.path.join(os.path.dirname(__file__), output_filename)
        save_to_json(all_data, save_path)
        print(f"Economic calendar data has been saved to {save_path}")
    else:
        print("No data to save")

def main(start_date, end_date):
    start_month = start_date.split(' ')[0]
    end_month = end_date.split(' ')[0]
    output_filename = f'economic_calendar_data_{start_month}_{end_month}.json'
    fetch_and_save_calendar_data(start_date, end_date, output_filename)

if __name__ == "__main__":
    start_date = "Jan2024"
    end_date = "May2024"
    main(start_date, end_date)
