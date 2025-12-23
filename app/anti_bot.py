
import datetime
import requests
import os

IPQS_API_KEY = os.getenv('IPQS_API_KEY')
WITHHELD_IPS = ['127.0.0.1', 'localhost']
BLOCKED_COUNTRIES = ['CN', 'RU', 'KP', 'IR']

class BotDetector:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.signals = {}
        self.totalscore = 0
        self.country = None

    def check_ip(self):

        if self.ip_address in WITHHELD_IPS:
            print(f"IP {self.ip_address} is withheld from checks.")
            self.signals["ip"] = 0
            self.signals["geo"] = 0
            self.country = "LOCAL"
            return
        try:
            url = f"https://ipqualityscore.com/api/json/ip/{IPQS_API_KEY}/{self.ip_address}"
            response = requests.get(url)
            data = response.json()

            fraudscore = data.get('fraud_score')
            self.signals["ip"] = fraudscore

            self.country = data.get('country_code')
            if self.country in BLOCKED_COUNTRIES:
                self.signals["geo"] = 100
            else:
                self.signals["geo"] = 0

        except Exception as e:
            print(f"Error checking IP: {e}")
            self.signals["ip"] = 0
            self.signals["geo"] = 0
            self.country = "Unknown"
        
    def headless_score(self, headless_score):
        self.signals["headless"] = headless_score
            
    def is_bot(self, threshold=60):
        self.totalscore = sum(self.signals.values())
        if self.totalscore >= threshold:
            return True
        else:
            return False
        
    def get_summary(self):
        return {
            "ip_address": self.ip_address,
            "signals": self.signals,
            "totalscore": self.totalscore,
            "block": self.is_bot(),
            "country": self.country
        }

def log_event(summary):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ip_address = summary.get("ip_address")
    signals = summary.get("signals", {})
    total = summary.get("totalscore", 0)
    is_bot_detected = summary.get("block", False)

    try:
        log_entry = f"{timestamp} - IP: {ip_address}, Signals: {signals}, Total: {total} Blocked: {is_bot_detected}\n"
        with open("log.txt", "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging event: {e}")