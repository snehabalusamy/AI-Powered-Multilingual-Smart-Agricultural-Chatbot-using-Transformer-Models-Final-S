import requests
import time

def test_chat():
    url = "http://localhost:8000/chat"
    payload = {"message": "best fertilizer for rice"}
    
    print(f"Sending request to {url} with payload: {payload}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start if running immediately after spawn
    time.sleep(2)
    test_chat()
