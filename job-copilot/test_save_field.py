from fastapi.testclient import TestClient
from api.main import app
import traceback

client = TestClient(app)

print("Testing save-field via TestClient...")
try:
    # 1. Register/Login to get a real token via TestClient
    client.post("/api/auth/register", json={"username": "test_save_user4", "password": "pw"})
    login = client.post("/api/auth/login", data={"username": "test_save_user4", "password": "pw"})
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    data = {"label_text": "First Name", "field_value": "John"}
    response = client.post("/api/save-field", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    with open("error.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Exception written to error.txt")

# Removed match-fields test

