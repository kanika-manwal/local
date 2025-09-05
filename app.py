from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "Page": "Home Page - use /request endpoint",
        "Usage Example": "/request?commodity=Potato&state=Karnataka&market=Bangalore",
        "Time Stamp": datetime.datetime.now().isoformat()
    })

@app.route("/request")
def get_prices():
    commodity = request.args.get("commodity")
    state = request.args.get("state")
    market = request.args.get("market")

    if not commodity or not state or not market:
        return jsonify({"error": "Please provide commodity, state, and market parameters"}), 400

    # Build Agmarknet URL
    url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

    payload = {
        "Tx_Commodity": commodity,
        "Tx_State": state,
        "Tx_Market": market,
        "Tx_Date": datetime.date.today().strftime("%d-%b-%Y"),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, params=payload, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 500

    # Parse HTML response
    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all("tr")

    prices = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 7:
            prices.append({
                "state": state,
                "market": market,
                "commodity": commodity,
                "variety": cols[1].text.strip(),
                "arrival_date": cols[2].text.strip(),
                "min_price": cols[4].text.strip(),
                "max_price": cols[5].text.strip(),
                "modal_price": cols[6].text.strip()
            })

    if not prices:
        return jsonify({"message": "No data found for given inputs"}), 404

    return jsonify(prices)

if __name__ == "__main__":
    app.run(debug=True)
