# antibot-sim

Multi-layered bot detection system for login forms. Detects automated traffic before credential validation using behavioral analysis, fingerprinting, and IP reputation.

## Detection Layers

**IP Reputation**: Queries IPQS API for fraud scores on incoming IPs. High-risk IPs get points added to the bot score.

**Geolocking**: Blocks or flags requests from specified countries based on IP geolocation data.

**Headless Detection**: Client-side checks for automation signatures:
- `navigator.webdriver` flag
- Plugin count (headless browsers typically have 0)
- Missing language settings

**Engine-Level Checks**: Harder to spoof than simple property checks:
- `Function.prototype.toString` verification (detects modified native functions)
- Puppeteer injection detection (`__puppeteer_evaluation_script__`)
- Chrome runtime presence (real Chrome vs headless)

**Browser Fingerprinting**: Generates device hash from:
- User agent, platform, screen dimensions
- Color depth, timezone offset
- Canvas fingerprint (hashed)

**Credential Encryption**: RSA encryption of username/password client-side. Server holds private key, public key embedded in page. Credentials never sent in plaintext.

## Scoring

Each check contributes points to a total score. Requests hitting 60+ points are blocked before password validation.

```
IP fraud score:     0-100 points (from API)
Geo block:          100 points (if blocked country)
Headless signals:   varies (webdriver=100, no plugins=30, etc)
```

## Setup

```bash
# Install dependencies
pip install flask cryptography requests python-dotenv

# Add your IPQS API key
echo "IPQS_API_KEY=your_key_here" > .env

# Run
python run.py
```

Visit `localhost:5001`, login with anything.

## Structure

```
├── app/
│   ├── __init__.py
│   ├── routes.py          # Flask routes
│   ├── anti_bot.py        # BotDetector class, scoring logic
│   ├── crypto.py          # RSA key generation, encrypt/decrypt
│   └── templates/
│       └── index.html
├── static/js/
│   └── sentinel.js        # Client-side detection + encryption
├── .env                   # API keys (not committed)
├── log.txt                # Request logs
└── run.py
```

## Logs

Each request logs: timestamp, IP, country, signals breakdown, total score, block decision.

```
2025-12-22 17:47:03 - IP: 127.0.0.1, Signals: {'ip': 0, 'geo': 0, 'headless': 0}, Total: 0 Blocked: False
```

## Notes

- Keys regenerate on server restart (dev only, would persist in production)
- Localhost IPs are whitelisted
- Threshold and blocked countries are configurable in `anti_bot.py`