import httpx

API_URL = "http://localhost:8000/api"

def create_and_test():
    with httpx.Client(base_url=API_URL) as client:
        # Create user A
        r1 = client.post("/auth/signup", json={"username": "alice", "password": "pwd", "email": "a@ex.com"})
        print("Alice signup:", r1.status_code)
        
        # Login user A
        r2 = client.post("/auth/login", json={"username": "alice", "password": "pwd"})
        print("Alice login:", r2.status_code)
        token_a = r2.json()["access_token"]
        
        # Add preference for user A
        r3 = client.put("/preferences", json={
            "preferred_locations": ["New York"],
            "preferred_keywords": [],
            "remote_only": False,
            "dark_mode": True,
            "seniority_level": "Senior"
        }, headers={"Authorization": f"Bearer {token_a}"})
        print("Alice prefs save:", r3.status_code)
        
        # Create user B
        r4 = client.post("/auth/signup", json={"username": "bob", "password": "pwd", "email": "b@ex.com"})
        print("Bob signup:", r4.status_code)
        
        # Login user B
        r5 = client.post("/auth/login", json={"username": "bob", "password": "pwd"})
        print("Bob login:", r5.status_code)
        token_b = r5.json()["access_token"]
        
        # Check preference for user B
        r6 = client.get("/preferences", headers={"Authorization": f"Bearer {token_b}"})
        print("Bob prefs fetch:", r6.status_code)
        prefs_b = r6.json()
        print("Bob prefs:", prefs_b)
        
        if prefs_b.get("preferred_locations") == ["New York"] or prefs_b.get("dark_mode") == True:
            print("FAILURE: Data isolation broken!")
        else:
            print("SUCCESS: Data isolation verified!")

create_and_test()
