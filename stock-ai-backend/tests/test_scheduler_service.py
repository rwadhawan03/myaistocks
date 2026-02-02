"""
Unit tests for scheduler_service.py - Scheduled alerts service.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestSchedulerService:
    """Tests for SchedulerService class."""
    
    def test_init(self):
        """Test SchedulerService initialization."""
        from app.scheduler_service import SchedulerService
        service = SchedulerService()
        
        assert service.scheduler is None
        assert service.morning_hour == 8
        assert service.morning_minute == 30
        assert service.evening_hour == 17
        assert service.evening_minute == 0
    
    def test_start(self):
        """Test starting the scheduler."""
        with patch('app.scheduler_service.AsyncIOScheduler') as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            service.start()
            
            assert service.scheduler is not None
            mock_scheduler.add_job.assert_called()
            mock_scheduler.start.assert_called_once()
    
    def test_stop(self):
        """Test stopping the scheduler."""
        from app.scheduler_service import SchedulerService
        service = SchedulerService()
        service.scheduler = MagicMock()
        
        service.stop()
        
        service.scheduler.shutdown.assert_called_once()
        assert service.scheduler is None
    
    def test_stop_when_not_running(self):
        """Test stopping scheduler when not running."""
        from app.scheduler_service import SchedulerService
        service = SchedulerService()
        
        # Should not raise an error
        service.stop()
        
        assert service.scheduler is None
    
    def test_get_next_run_times(self):
        """Test getting next scheduled run times."""
        from app.scheduler_service import SchedulerService
        service = SchedulerService()
        
        result = service.get_next_run_times()
        
        assert "morning" in result
        assert "evening" in result
        
        # Verify times are in ISO format
        morning_time = datetime.fromisoformat(result["morning"])
        evening_time = datetime.fromisoformat(result["evening"])
        
        assert morning_time.hour == 8
        assert morning_time.minute == 30
        assert evening_time.hour == 17
        assert evening_time.minute == 0


class TestProcessAlerts:
    """Tests for alert processing functionality."""
    
    @pytest.mark.asyncio
    async def test_process_alerts_with_symbols(self):
        """Test processing alerts with specific symbols."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "user-123",
            "prompt": "Analyze tech stocks",
            "symbols": ["AAPL", "MSFT"],
            "trigger_time": "morning",
            "is_active": True
        }
        
        mock_user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('app.scheduler_service.get_active_schedulers_by_trigger', return_value=[mock_scheduler_data]), \
             patch('app.scheduler_service.get_user_by_id', return_value=mock_user_data), \
             patch('app.scheduler_service.ai_analyst') as mock_ai, \
             patch('app.scheduler_service.email_service') as mock_email:
            
            mock_ai.generate_stock_recommendation = AsyncMock(return_value={"analysis": "Buy AAPL"})
            mock_email.send_market_alert = AsyncMock(return_value=True)
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            await service._process_alerts("morning")
            
            # Should have called generate_stock_recommendation for each symbol
            assert mock_ai.generate_stock_recommendation.call_count == 2
            mock_email.send_market_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_alerts_without_symbols(self):
        """Test processing alerts without specific symbols (general market)."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "user-123",
            "prompt": "General market update",
            "symbols": [],
            "trigger_time": "evening",
            "is_active": True
        }
        
        mock_user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('app.scheduler_service.get_active_schedulers_by_trigger', return_value=[mock_scheduler_data]), \
             patch('app.scheduler_service.get_user_by_id', return_value=mock_user_data), \
             patch('app.scheduler_service.ai_analyst') as mock_ai, \
             patch('app.scheduler_service.email_service') as mock_email:
            
            mock_ai.generate_market_summary = AsyncMock(return_value={"summary": "Market closed up"})
            mock_email.send_market_alert = AsyncMock(return_value=True)
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            await service._process_alerts("evening")
            
            mock_ai.generate_market_summary.assert_called_once()
            mock_email.send_market_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_alerts_user_not_found(self):
        """Test processing alerts when user is not found."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "nonexistent-user",
            "prompt": "Test",
            "symbols": ["AAPL"],
            "trigger_time": "morning",
            "is_active": True
        }
        
        with patch('app.scheduler_service.get_active_schedulers_by_trigger', return_value=[mock_scheduler_data]), \
             patch('app.scheduler_service.get_user_by_id', return_value=None), \
             patch('app.scheduler_service.email_service') as mock_email:
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            await service._process_alerts("morning")
            
            # Should not send email if user not found
            mock_email.send_market_alert.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_alerts_error_handling(self):
        """Test error handling during alert processing."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "user-123",
            "prompt": "Test",
            "symbols": ["AAPL"],
            "trigger_time": "morning",
            "is_active": True
        }
        
        mock_user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('app.scheduler_service.get_active_schedulers_by_trigger', return_value=[mock_scheduler_data]), \
             patch('app.scheduler_service.get_user_by_id', return_value=mock_user_data), \
             patch('app.scheduler_service.ai_analyst') as mock_ai:
            
            mock_ai.generate_stock_recommendation = AsyncMock(side_effect=Exception("AI Error"))
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            # Should not raise exception
            await service._process_alerts("morning")


class TestRunManualAlert:
    """Tests for manual alert triggering."""
    
    @pytest.mark.asyncio
    async def test_run_manual_alert_success(self):
        """Test successful manual alert trigger."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "user-123",
            "prompt": "Analyze AAPL",
            "symbols": ["AAPL"],
            "trigger_time": "morning",
            "is_active": True
        }
        
        mock_user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('app.scheduler_service.get_scheduler_by_id', return_value=mock_scheduler_data), \
             patch('app.scheduler_service.get_user_by_id', return_value=mock_user_data), \
             patch('app.scheduler_service.ai_analyst') as mock_ai, \
             patch('app.scheduler_service.email_service') as mock_email:
            
            mock_ai.generate_stock_recommendation = AsyncMock(return_value={"analysis": "Buy AAPL"})
            mock_email.send_market_alert = AsyncMock(return_value=True)
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            result = await service.run_manual_alert("scheduler-123")
            
            assert result["success"] is True
            assert result["email_sent"] is True
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_run_manual_alert_scheduler_not_found(self):
        """Test manual alert with non-existent scheduler."""
        with patch('app.scheduler_service.get_scheduler_by_id', return_value=None):
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            result = await service.run_manual_alert("nonexistent-id")
            
            assert "error" in result
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_run_manual_alert_user_not_found(self):
        """Test manual alert when user is not found."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "nonexistent-user",
            "prompt": "Test",
            "symbols": ["AAPL"],
            "trigger_time": "morning"
        }
        
        with patch('app.scheduler_service.get_scheduler_by_id', return_value=mock_scheduler_data), \
             patch('app.scheduler_service.get_user_by_id', return_value=None):
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            result = await service.run_manual_alert("scheduler-123")
            
            assert "error" in result
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_run_manual_alert_error(self):
        """Test manual alert error handling."""
        mock_scheduler_data = {
            "id": "scheduler-123",
            "user_id": "user-123",
            "prompt": "Test",
            "symbols": ["AAPL"],
            "trigger_time": "morning"
        }
        
        mock_user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with patch('app.scheduler_service.get_scheduler_by_id', return_value=mock_scheduler_data), \
             patch('app.scheduler_service.get_user_by_id', return_value=mock_user_data), \
             patch('app.scheduler_service.ai_analyst') as mock_ai:
            
            mock_ai.generate_stock_recommendation = AsyncMock(side_effect=Exception("AI Error"))
            
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            result = await service.run_manual_alert("scheduler-123")
            
            assert "error" in result


class TestMorningEveningAlerts:
    """Tests for morning and evening alert triggers."""
    
    @pytest.mark.asyncio
    async def test_run_morning_alerts(self):
        """Test morning alerts execution."""
        with patch.object(
            __import__('app.scheduler_service', fromlist=['SchedulerService']).SchedulerService,
            '_process_alerts',
            new_callable=AsyncMock
        ) as mock_process:
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            await service._run_morning_alerts()
            
            mock_process.assert_called_once_with("morning")
    
    @pytest.mark.asyncio
    async def test_run_evening_alerts(self):
        """Test evening alerts execution."""
        with patch.object(
            __import__('app.scheduler_service', fromlist=['SchedulerService']).SchedulerService,
            '_process_alerts',
            new_callable=AsyncMock
        ) as mock_process:
            from app.scheduler_service import SchedulerService
            service = SchedulerService()
            
            await service._run_evening_alerts()
            
            mock_process.assert_called_once_with("evening")
