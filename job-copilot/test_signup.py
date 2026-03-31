import httpx

r = httpx.post('http://localhost:8000/api/auth/signup', json={"username": "testuser", "password": "password123", "email": "test@example.com"})
print("STATUS CODE:", r.status_code)
print("RESPONSE:", r.text)
