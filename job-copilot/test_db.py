from database_dir.database import SessionLocal, User, UserPreferences
from services import auth_service
try:
    db = SessionLocal()
    pwd = auth_service.get_password_hash("password123")
    u = User(username="test_direct", hashed_password=pwd, email="test_direct@ex.com")
    db.add(u)
    db.commit()
    db.refresh(u)
    p = UserPreferences(owner_id=u.id)
    db.add(p)
    db.commit()
    print("Success. User ID:", u.id)
except Exception as e:
    import traceback
    traceback.print_exc()
