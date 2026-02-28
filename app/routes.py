# app/routes.py

from ml.train import extract_features, predict
from flask import Blueprint, render_template, request, session
from app.anti_bot import BotDetector, log_event
from app.crypto import generate_keypair, get_public_key_pem, decrypt_data
import os
import requests
import secrets
import json
import base64
from collections import defaultdict

main = Blueprint('main', __name__)

private_key = generate_keypair()

# Same constants as the VM
XOR_KEY = 48879313
MOD_VALUE = 1000000

# Add this function somewhere before your routes
def log_training_data(request):
    """Log request headers to ml/data.jsonl for training."""
    headers_dict = dict(request.headers)
    header_order = list(request.headers.keys())
    
    features = extract_features(headers_dict, header_order)
    features['label'] = 'human'
    features['raw_header_order'] = header_order
    
    with open('ml/data.jsonl', 'a') as f:
        f.write(json.dumps(features) + '\n')

def validate_vm_token(token, fingerprint_b64, headless_score):
    """Validate the VM token matches expected value"""
    try:
        # Decode fingerprint
        fingerprint = json.loads(base64.b64decode(fingerprint_b64))
        
        width = fingerprint.get('screenWidth', 0)
        height = fingerprint.get('screenHeight', 0)
        
        # We don't have pluginCount in fingerprint, so we need to add it
        # For now, assume 5 as default or add it to fingerprint
        pluginCount = fingerprint.get('pluginCount', 5)
        
        # Same formula as VM
        expected = headless_score * 7919 + width * 31 + height * 17 + pluginCount * 13
        expected = expected ^ XOR_KEY
        expected = expected % MOD_VALUE
        
        return int(token) == expected
    except Exception as e:
        print(f"Token validation error: {e}")
        return False

@main.route('/')
def index():
    public_key_pem = get_public_key_pem(private_key)
    token = secrets.token_hex(32)
    session['csrf_token'] = token
    return render_template('index.html', csrf_token=token, public_key=public_key_pem)

bot_request_counts = defaultdict(int)
BOT_THRESHOLD = 10  # allow first 10, then start blocking

@main.route('/login', methods=['POST'])
def login():
    headers_dict = dict(request.headers)
    header_order = list(request.headers.keys())
    ml_result = predict(headers_dict, header_order)
    print(f"[ML] {ml_result}")
    
    if ml_result['is_bot']:
        bot_request_counts[request.remote_addr] += 1
        
        if bot_request_counts[request.remote_addr] > BOT_THRESHOLD:
            return "Access Denied", 403
    
    encrypted_username = request.form.get('encrypted_username')
    encrypted_password = request.form.get('encrypted_password')
    
    if not encrypted_username or not encrypted_password:
        return "Bad Request", 400

    vm_token = request.form.get('vm_token', '0')
    fingerprint = request.form.get('fingerprint', '')
    headless_score = int(request.form.get('headless_score', 0))

    # Validate VM token first
    if False and not validate_vm_token(vm_token, fingerprint, headless_score):
        log_event({
            'ip': request.remote_addr,
            'signals': {'vm_token': 'invalid'},
            'totalscore': 0,
            'block': True
        })
        return "Access Denied: Token Validation Failed", 403

    try:
        username = decrypt_data(private_key, encrypted_username)
        password = decrypt_data(private_key, encrypted_password)
    except Exception:
        return "Bad Request", 400

    ip_address = request.remote_addr

    detector = BotDetector(ip_address)

    detector.check_ip()
    detector.headless_score(headless_score=headless_score)

    if detector.is_bot():
        log_event(detector.get_summary())
        return "Access Denied: Bot Detected", 403
    else:
        log_event(detector.get_summary())
        return f"Welcome {username}!", 200