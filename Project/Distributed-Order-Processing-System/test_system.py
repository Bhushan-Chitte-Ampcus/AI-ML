import requests

BASE_ORDER = "http://localhost:8000"
BASE_PRODUCT = "http://localhost:8001"

def test_flow():
    # successful checkout
    resp = requests.post(f"{BASE_ORDER}/checkout?user_id=3&product_id=2&quantity=10")
    print("Success:", resp.json())

    # insufficient balance
    resp = requests.post(f"{BASE_ORDER}/checkout?user_id=2&product_id=1&quantity=1")
    print("Insufficient:", resp.json())

    # out of stock
    resp = requests.post(f"{BASE_ORDER}/checkout?user_id=4&product_id=1&quantity=2")
    print("Stock:", resp.json())

test_flow()