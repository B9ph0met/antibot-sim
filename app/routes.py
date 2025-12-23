from flask import Blueprint, render_template, request, session
from app.anti_bot import BotDetector, log_event
from app.crypto import generate_keypair, get_public_key_pem, decrypt_data
import os
import requests
import secrets

main = Blueprint('main', __name__)

private_key = generate_keypair()

@main.route('/')
def index():
    public_key_pem = get_public_key_pem(private_key)
    token = secrets.token_hex(32)
    session['csrf_token'] = token
    return render_template('index.html', csrf_token=token, public_key=public_key_pem)

@main.route('/login', methods=['POST'])
def login():
    encrypted_username = request.form.get('encrypted_username')
    encrypted_password = request.form.get('encrypted_password')

    username = decrypt_data(private_key, encrypted_username)
    password = decrypt_data(private_key, encrypted_password)

    ip_address = request.remote_addr

    detector = BotDetector(ip_address)

    detector.check_ip()
    detector.headless_score(headless_score=int(request.form.get('headless_score', 0)))

    if detector.is_bot():
        log_event(detector.get_summary())
        return "Access Denied: Bot Detected", 403
    else:
        log_event(detector.get_summary())
        return f"Welcome {username}!", 200