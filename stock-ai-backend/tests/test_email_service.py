"""
Unit tests for email_service.py - Email notification service.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestEmailService:
    """Tests for EmailService class."""
    
    def test_init_with_env_vars(self):
        """Test EmailService initialization with environment variables."""
        with patch.dict('os.environ', {
            'SMTP_HOST': 'smtp.test.com',
            'SMTP_PORT': '587',
            'SMTP_USER': 'test@test.com',
            'SMTP_PASSWORD': 'testpass'
        }):
            from app.email_service import EmailService
            service = EmailService()
            
            assert service.smtp_host == 'smtp.test.com'
            assert service.smtp_port == 587
            assert service.smtp_user == 'test@test.com'
            assert service.smtp_password == 'testpass'
    
    def test_init_with_defaults(self):
        """Test EmailService initialization with default values."""
        with patch.dict('os.environ', {}, clear=True):
            from app.email_service import EmailService
            service = EmailService()
            
            assert service.smtp_host == 'smtp.gmail.com'
            assert service.smtp_port == 587
    
    @pytest.mark.asyncio
    async def test_send_email_not_configured(self):
        """Test send_email when SMTP is not configured."""
        with patch.dict('os.environ', {'SMTP_USER': '', 'SMTP_PASSWORD': ''}):
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = ''
            service.smtp_password = ''
            
            result = await service.send_email(
                to_email="recipient@test.com",
                subject="Test Subject",
                body="Test Body"
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_email(
                to_email="recipient@test.com",
                subject="Test Subject",
                body="Test Body"
            )
            
            assert result is True
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_email_with_html(self):
        """Test email sending with HTML body."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_email(
                to_email="recipient@test.com",
                subject="Test Subject",
                body="Test Body",
                html_body="<html><body>Test</body></html>"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_email_failure(self):
        """Test email sending failure."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("SMTP Error")
            
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_email(
                to_email="recipient@test.com",
                subject="Test Subject",
                body="Test Body"
            )
            
            assert result is False


class TestMarketAlertEmail:
    """Tests for market alert email functionality."""
    
    @pytest.mark.asyncio
    async def test_send_market_alert_morning(self):
        """Test sending morning market alert."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock):
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_market_alert(
                to_email="user@test.com",
                user_name="Test User",
                alert_content="Market is up today!",
                trigger_time="morning",
                symbols=["AAPL", "MSFT"]
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_market_alert_evening(self):
        """Test sending evening market alert."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock):
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_market_alert(
                to_email="user@test.com",
                user_name="Test User",
                alert_content="Market closed strong!",
                trigger_time="evening",
                symbols=None
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_market_alert_general_market(self):
        """Test sending market alert without specific symbols."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock):
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_market_alert(
                to_email="user@test.com",
                user_name="Test User",
                alert_content="General market update",
                trigger_time="morning",
                symbols=[]
            )
            
            assert result is True


class TestWelcomeEmail:
    """Tests for welcome email functionality."""
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_success(self):
        """Test successful welcome email sending."""
        with patch('app.email_service.aiosmtplib.send', new_callable=AsyncMock):
            from app.email_service import EmailService
            service = EmailService()
            service.smtp_user = 'test@test.com'
            service.smtp_password = 'testpass'
            service.from_email = 'test@test.com'
            
            result = await service.send_welcome_email(
                to_email="newuser@test.com",
                user_name="New User"
            )
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_not_configured(self):
        """Test welcome email when SMTP not configured."""
        from app.email_service import EmailService
        service = EmailService()
        service.smtp_user = ''
        service.smtp_password = ''
        
        result = await service.send_welcome_email(
            to_email="newuser@test.com",
            user_name="New User"
        )
        
        assert result is False
