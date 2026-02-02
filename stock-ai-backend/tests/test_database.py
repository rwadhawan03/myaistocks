"""
Unit tests for database.py - User and Scheduler CRUD operations.
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch


class TestUserOperations:
    """Tests for user-related database operations."""
    
    def test_create_user_success(self, temp_data_dir):
        """Test successful user creation."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_user, load_users
            
            result = create_user("test@example.com", "Test User", "password123")
            
            assert result is not None
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"
            assert "id" in result
            assert "created_at" in result
            
            # Verify user was saved
            users = load_users()
            assert "test@example.com" in users
    
    def test_create_user_duplicate_email(self, temp_data_dir):
        """Test that duplicate email registration fails."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_user
            
            # Create first user
            create_user("test@example.com", "Test User", "password123")
            
            # Try to create duplicate
            result = create_user("test@example.com", "Another User", "password456")
            
            assert result is None
    
    def test_authenticate_user_success(self, temp_data_dir):
        """Test successful user authentication."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_user, authenticate_user
            
            create_user("test@example.com", "Test User", "password123")
            
            result = authenticate_user("test@example.com", "password123")
            
            assert result is not None
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"
    
    def test_authenticate_user_wrong_password(self, temp_data_dir):
        """Test authentication with wrong password."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_user, authenticate_user
            
            create_user("test@example.com", "Test User", "password123")
            
            result = authenticate_user("test@example.com", "wrongpassword")
            
            assert result is None
    
    def test_authenticate_user_nonexistent(self, temp_data_dir):
        """Test authentication with non-existent user."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import authenticate_user
            
            result = authenticate_user("nonexistent@example.com", "password123")
            
            assert result is None
    
    def test_get_user_by_id(self, temp_data_dir):
        """Test retrieving user by ID."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_user, get_user_by_id
            
            created = create_user("test@example.com", "Test User", "password123")
            user_id = created["id"]
            
            result = get_user_by_id(user_id)
            
            assert result is not None
            assert result["id"] == user_id
            assert result["email"] == "test@example.com"
    
    def test_get_user_by_id_nonexistent(self, temp_data_dir):
        """Test retrieving non-existent user by ID."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import get_user_by_id
            
            result = get_user_by_id("nonexistent-id")
            
            assert result is None


class TestSchedulerOperations:
    """Tests for scheduler-related database operations."""
    
    def test_create_scheduler(self, temp_data_dir):
        """Test successful scheduler creation."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler
            
            result = create_scheduler(
                user_id="user-123",
                prompt="Analyze AAPL",
                trigger_time="morning",
                symbols=["AAPL", "MSFT"],
                is_active=True
            )
            
            assert result is not None
            assert result["user_id"] == "user-123"
            assert result["prompt"] == "Analyze AAPL"
            assert result["trigger_time"] == "morning"
            assert result["symbols"] == ["AAPL", "MSFT"]
            assert result["is_active"] is True
            assert "id" in result
            assert "created_at" in result
    
    def test_get_user_schedulers(self, temp_data_dir):
        """Test retrieving schedulers for a user."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler, get_user_schedulers
            
            # Create schedulers for different users
            create_scheduler("user-123", "Prompt 1", "morning", ["AAPL"])
            create_scheduler("user-123", "Prompt 2", "evening", ["MSFT"])
            create_scheduler("user-456", "Prompt 3", "morning", ["GOOGL"])
            
            result = get_user_schedulers("user-123")
            
            assert len(result) == 2
            assert all(s["user_id"] == "user-123" for s in result)
    
    def test_get_scheduler_by_id(self, temp_data_dir):
        """Test retrieving scheduler by ID."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler, get_scheduler_by_id
            
            created = create_scheduler("user-123", "Test prompt", "morning", ["AAPL"])
            scheduler_id = created["id"]
            
            result = get_scheduler_by_id(scheduler_id)
            
            assert result is not None
            assert result["id"] == scheduler_id
    
    def test_update_scheduler(self, temp_data_dir):
        """Test updating a scheduler."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler, update_scheduler, get_scheduler_by_id
            
            created = create_scheduler("user-123", "Original prompt", "morning", ["AAPL"])
            scheduler_id = created["id"]
            
            result = update_scheduler(scheduler_id, {"prompt": "Updated prompt", "is_active": False})
            
            assert result is not None
            assert result["prompt"] == "Updated prompt"
            assert result["is_active"] is False
            
            # Verify persistence
            fetched = get_scheduler_by_id(scheduler_id)
            assert fetched["prompt"] == "Updated prompt"
    
    def test_delete_scheduler(self, temp_data_dir):
        """Test deleting a scheduler."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler, delete_scheduler, get_scheduler_by_id
            
            created = create_scheduler("user-123", "Test prompt", "morning", ["AAPL"])
            scheduler_id = created["id"]
            
            result = delete_scheduler(scheduler_id)
            
            assert result is True
            assert get_scheduler_by_id(scheduler_id) is None
    
    def test_delete_scheduler_nonexistent(self, temp_data_dir):
        """Test deleting non-existent scheduler."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import delete_scheduler
            
            result = delete_scheduler("nonexistent-id")
            
            assert result is False
    
    def test_get_active_schedulers_by_trigger(self, temp_data_dir):
        """Test retrieving active schedulers by trigger time."""
        with patch('app.database.DATA_DIR', str(temp_data_dir)), \
             patch('app.database.USERS_FILE', str(temp_data_dir / "users.json")), \
             patch('app.database.SCHEDULERS_FILE', str(temp_data_dir / "schedulers.json")):
            
            from app.database import create_scheduler, get_active_schedulers_by_trigger
            
            create_scheduler("user-1", "Morning 1", "morning", ["AAPL"], is_active=True)
            create_scheduler("user-2", "Morning 2", "morning", ["MSFT"], is_active=True)
            create_scheduler("user-3", "Morning 3", "morning", ["GOOGL"], is_active=False)
            create_scheduler("user-4", "Evening 1", "evening", ["TSLA"], is_active=True)
            
            morning_schedulers = get_active_schedulers_by_trigger("morning")
            
            assert len(morning_schedulers) == 2
            assert all(s["trigger_time"] == "morning" for s in morning_schedulers)
            assert all(s["is_active"] is True for s in morning_schedulers)


class TestPasswordHashing:
    """Tests for password hashing functionality."""
    
    def test_hash_password_consistency(self):
        """Test that same password produces same hash."""
        from app.database import hash_password
        
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 == hash2
    
    def test_hash_password_different_passwords(self):
        """Test that different passwords produce different hashes."""
        from app.database import hash_password
        
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        
        assert hash1 != hash2
