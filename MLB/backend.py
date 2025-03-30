import requests
import sys
from flask import Flask, jsonify, render_template
from flask_cors import CORS  # 引入 CORS
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # 啟用 CORS，允許所有來源訪問（可進一步限制）

def fetch_mlb_standings():
    # 從 MLB 官方 API 獲取 2024 賽季的戰績數據
    url = "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2024"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    
    standings = {}
    for record in data.get("records", []):
        for team_record in record["teamRecords"]:
            team_name = team_record["team"]["name"]
            standings[team_name] = {
                "W": team_record["wins"],  # 勝場
                "L": team_record["losses"],  # 敗場
                "PCT": float(team_record["winningPercentage"]),  # 勝率
                "Home": f"{team_record['records']['splitRecords'][0]['wins']}-{team_record['records']['splitRecords'][0]['losses']}",  # 主場戰績
                "Away": f"{team_record['records']['splitRecords'][1]['wins']}-{team_record['records']['splitRecords'][1]['losses']}",  # 客場戰績
                "DIFF": team_record["runDifferential"],  # 得分差
                "STRK": team_record["streak"]["streakCode"]  # 連勝/連敗
            }
    return standings

@app.route('/standings', methods=['GET'])
def get_standings():
    standings = fetch_mlb_standings()
    if standings:
        return jsonify(standings)
    return jsonify({'error': '無法獲取數據'}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
