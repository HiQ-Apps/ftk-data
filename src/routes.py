from flask import Flask, jsonify, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

data_dir = "data/raw/pair_data/"
pairs = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'EURJPY', 'EURGBP', 'GBPJPY', 'CHFJPY', 'EURCHF', 'GBPCHF']

def load_data():
    data = {}
    for pair in pairs:
        filename = os.path.join(data_dir, f"max_daily/{pair}.csv")
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
        data[pair] = df['Close']
    return data

def calculate_dynamic_strength(data, time_points):
    currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF']
    results = []
    for time_point in time_points:
        strength = {currency: 0 for currency in currencies}
        count = {currency: 0 for currency in currencies}
        valid_data = True
        for pair, df in data.items():
            try:
                price = df.loc[time_point]
                base_currency, quote_currency = pair[:3], pair[3:]
                if 'JPY' in pair:
                    price /= 100  # Scale JPY to be comparable with other currencies
                if base_currency in currencies and quote_currency in currencies:
                    strength[base_currency] += price
                    strength[quote_currency] += 1 / price
                    count[base_currency] += 1
                    count[quote_currency] += 1
            except KeyError:
                valid_data = False
                break
            except IndexError:
                valid_data = False
                break

        if valid_data:
            for currency in strength:
                if count[currency] > 0:
                    strength[currency] /= count[currency]
            results.append(strength)
        else:
            results.append({currency: 0 for currency in currencies})
    
    return pd.DataFrame(results, index=time_points)

@app.route("/api/strengths", methods=["GET"])
def get_strengths():
    data = load_data()
    time_points = list(data.values())[0].index
    strengths_df = calculate_dynamic_strength(data, time_points)
    return jsonify(strengths_df.to_dict(orient="index"))

@app.route("/api/strengths/<string:currency>", methods=["GET"])
def get_strength(currency):
    data = load_data()
    time_points = list(data.values())[0].index
    strengths_df = calculate_dynamic_strength(data, time_points)
    if currency.upper() in strengths_df.columns:
        return jsonify(strengths_df[currency.upper()].to_dict())
    else:
        return jsonify({"error": "Currency not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)