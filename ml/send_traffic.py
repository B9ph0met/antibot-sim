import json
import random
import numpy as np
from train import extract_features

def generate_bot_entry():
    profile = random.choice(['empty', 'minimal', 'bad_order', 'partial'])
    
    if profile == 'empty':
        headers = {}
    elif profile == 'minimal':
        headers = {
            'User-Agent': random.choice([
                'python-requests/2.31.0',
                'Go-http-client/1.1',
                'curl/7.88.1',
                'Python/3.11 aiohttp/3.9.0',
            ]),
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    elif profile == 'bad_order':
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Host': 'localhost:5001',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    elif profile == 'partial':
        possible = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'text/html',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive',
            'Host': 'localhost:5001',
        }
        keys = random.sample(list(possible.keys()), random.randint(2, 4))
        headers = {k: possible[k] for k in keys}
    
    header_order = list(headers.keys())
    features = extract_features(headers, header_order)
    features['label'] = 'bot'
    features['raw_header_order'] = header_order
    return features

def generate_human_entry():
    headers = {
        'Host': 'localhost:5001',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': random.choice(['"macOS"', '"Windows"', '"Linux"']),
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': random.choice([
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        ]),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9']),
    }
    
    header_order = list(headers.keys())
    features = extract_features(headers, header_order)
    features['label'] = 'human'
    features['raw_header_order'] = header_order
    return features

if __name__ == '__main__':
    entries = []
    for _ in range(500):
        entries.append(generate_bot_entry())
    for _ in range(500):
        entries.append(generate_human_entry())
    
    random.shuffle(entries)
    
    with open('data.jsonl', 'a') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Wrote {len(entries)} entries to data.jsonl")
    
    bot_sample = next(e for e in entries if e['label'] == 'bot')
    human_sample = next(e for e in entries if e['label'] == 'human')
    
    print(f"\nBot sample:   {json.dumps(bot_sample, indent=2)}")
    print(f"\nHuman sample: {json.dumps(human_sample, indent=2)}")