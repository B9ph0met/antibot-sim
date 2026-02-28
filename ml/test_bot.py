import requests

url = 'http://localhost:5001/login'

for i in range(15):
    r = requests.post(url, data={
        'encrypted_username': 'dGVzdA==',
        'encrypted_password': 'dGVzdA==',
        'vm_token': '0',
        'fingerprint': '',
        'headless_score': '0',
    })

    print(f"Request {i+1}: {r.status_code} - {r.text[:60]}")

