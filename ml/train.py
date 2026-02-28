import torch
import numpy as np
import json
import torch.nn as nn
import os


EXPECTED_CHROME_ORDER = [
    'Host', 'Connection', 'sec-ch-ua', 'sec-ch-ua-mobile',
    'sec-ch-ua-platform', 'Upgrade-Insecure-Requests',
    'User-Agent', 'Accept', 'Accept-Encoding', 'Accept-Language'
]

def extract_features(headers_dict, header_order):
    features = {
        'has_user_agent':       float('User-Agent' in headers_dict),
        'has_accept':           float('Accept' in headers_dict),
        'has_accept_language':  float('Accept-Language' in headers_dict),
        'has_accept_encoding':  float('Accept-Encoding' in headers_dict),
        'has_connection':       float('Connection' in headers_dict),
        'has_sec_ch_ua':        float('sec-ch-ua' in headers_dict),
        'header_count':         float(len(headers_dict)),
        'header_order_score':   float(check_header_order(header_order)),
    }
    return features

def check_header_order(header_order):
    if not header_order:
        return 0.0
    present = [h for h in EXPECTED_CHROME_ORDER if h in header_order]
    if len(present) < 2:
        return 0.0
    correct_pairs = 0
    total_pairs = 0
    for i in range(len(present)):
        for j in range(i + 1, len(present)):
            total_pairs += 1
            idx_i = header_order.index(present[i])
            idx_j = header_order.index(present[j])
            if idx_i < idx_j:
                correct_pairs += 1
    return correct_pairs / total_pairs if total_pairs > 0 else 0.0

def load_training_data(path='data.jsonl'):
    features_list = []
    labels = []
    
    feature_keys = [
        'has_user_agent', 'has_accept', 'has_accept_language',
        'has_accept_encoding', 'has_connection', 'has_sec_ch_ua',
        'header_count', 'header_order_score'
    ]
    
    with open(path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            row = [entry[k] for k in feature_keys]
            features_list.append(row)
            labels.append(0.0 if entry['label'] == 'human' else 1.0)
    
    X = torch.tensor(features_list, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32)
    
    return X, y, feature_keys

class BotDetectorNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(8, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)
    
def predict(headers_dict, header_order):
    model = BotDetectorNet()
    model_path = os.path.join(os.path.dirname(__file__), 'model.pth')
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    features = extract_features(headers_dict, header_order)
    feature_values = [features[k] for k in [
        'has_user_agent', 'has_accept', 'has_accept_language',
        'has_accept_encoding', 'has_connection', 'has_sec_ch_ua',
        'header_count', 'header_order_score'
    ]]
    
    x = torch.tensor([feature_values], dtype=torch.float32)
    with torch.no_grad():
        prob = model(x).item()
    
    return {'bot_probability': round(prob, 4), 'is_bot': prob > 0.5}

if __name__ == '__main__':
    X, y, feature_keys = load_training_data()
    print(f"Loaded {len(X)} samples ({int((y==0).sum())} human, {int((y==1).sum())} bot)")
    
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    model = BotDetectorNet()
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)}")
    print(f"{'Epoch':>6} | {'Loss':>8} | {'Accuracy':>8}")
    print("-" * 30)
    
    for epoch in range(100):
        model.train()
        predictions = model(X_train).squeeze()
        loss = criterion(predictions, y_train)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                test_preds = model(X_test).squeeze()
                test_acc = ((test_preds > 0.5) == y_test).float().mean()
            print(f"{epoch+1:>6} | {loss.item():>8.4f} | {test_acc.item():>7.1%}")
    
    print("\nDone training!")
    torch.save(model.state_dict(), 'model.pth')
    print("Model saved to model.pth")
    
    print("\n--- Testing saved model ---")
    result = predict(
        {'User-Agent': 'python-requests/2.31.0', 'Accept': '*/*'},
        ['User-Agent', 'Accept']
    )
    print(f"Bot request:   {result}")
    
    result = predict(
        {
            'Host': 'localhost', 'Connection': 'keep-alive',
            'sec-ch-ua': '"Chrome"', 'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html', 'Accept-Encoding': 'gzip',
            'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"', 'Upgrade-Insecure-Requests': '1',
        },
        ['Host', 'Connection', 'sec-ch-ua', 'sec-ch-ua-mobile',
         'sec-ch-ua-platform', 'Upgrade-Insecure-Requests',
         'User-Agent', 'Accept', 'Accept-Encoding', 'Accept-Language']
    )
    print(f"Human request: {result}")