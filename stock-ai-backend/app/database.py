import json
import os
from datetime import datetime
from typing import Optional, List, Dict
import hashlib
import uuid

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SCHEDULERS_FILE = os.path.join(DATA_DIR, "schedulers.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    if not os.path.exists(SCHEDULERS_FILE):
        with open(SCHEDULERS_FILE, "w") as f:
            json.dump({}, f)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> Dict:
    ensure_data_dir()
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: Dict):
    ensure_data_dir()
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2, default=str)


def create_user(email: str, name: str, password: str) -> Optional[Dict]:
    users = load_users()
    if email in users:
        return None
    
    user_id = str(uuid.uuid4())
    users[email] = {
        "id": user_id,
        "email": email,
        "name": name,
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    save_users(users)
    return {
        "id": user_id,
        "email": email,
        "name": name,
        "created_at": users[email]["created_at"]
    }


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    users = load_users()
    if email not in users:
        return None
    
    user = users[email]
    if user["password_hash"] != hash_password(password):
        return None
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "created_at": user["created_at"]
    }


def get_user_by_id(user_id: str) -> Optional[Dict]:
    users = load_users()
    for email, user in users.items():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "created_at": user["created_at"]
            }
    return None


def load_schedulers() -> Dict:
    ensure_data_dir()
    with open(SCHEDULERS_FILE, "r") as f:
        return json.load(f)


def save_schedulers(schedulers: Dict):
    ensure_data_dir()
    with open(SCHEDULERS_FILE, "w") as f:
        json.dump(schedulers, f, indent=2, default=str)


def create_scheduler(user_id: str, prompt: str, trigger_time: str, symbols: List[str], is_active: bool = True) -> Dict:
    schedulers = load_schedulers()
    scheduler_id = str(uuid.uuid4())
    
    schedulers[scheduler_id] = {
        "id": scheduler_id,
        "user_id": user_id,
        "prompt": prompt,
        "trigger_time": trigger_time,
        "symbols": symbols,
        "is_active": is_active,
        "created_at": datetime.now().isoformat()
    }
    save_schedulers(schedulers)
    return schedulers[scheduler_id]


def get_user_schedulers(user_id: str) -> List[Dict]:
    schedulers = load_schedulers()
    return [s for s in schedulers.values() if s["user_id"] == user_id]


def get_scheduler_by_id(scheduler_id: str) -> Optional[Dict]:
    schedulers = load_schedulers()
    return schedulers.get(scheduler_id)


def update_scheduler(scheduler_id: str, updates: Dict) -> Optional[Dict]:
    schedulers = load_schedulers()
    if scheduler_id not in schedulers:
        return None
    
    schedulers[scheduler_id].update(updates)
    save_schedulers(schedulers)
    return schedulers[scheduler_id]


def delete_scheduler(scheduler_id: str) -> bool:
    schedulers = load_schedulers()
    if scheduler_id not in schedulers:
        return False
    
    del schedulers[scheduler_id]
    save_schedulers(schedulers)
    return True


def get_active_schedulers_by_trigger(trigger_time: str) -> List[Dict]:
    schedulers = load_schedulers()
    return [s for s in schedulers.values() if s["trigger_time"] == trigger_time and s["is_active"]]
