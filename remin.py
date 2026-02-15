# panel_timer.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from telegram import Bot

class PanelTimer:
    def __init__(self, bot_token: str, admin_id: int, panel_days: int = 3):
        self.bot = Bot(token=bot_token)
        self.admin_id = admin_id

        # Panel duration
        self.panel_duration = timedelta(days=panel_days)

        # Panel activation time (default now)
        self.activation_time = datetime.now()

        # Scheduler
        self.scheduler = BackgroundScheduler()
        # Check every hour
        self.scheduler.add_job(self.check_panel, "interval", hours=1)
        self.scheduler.start()

        # Track first reminder sent
        self.first_reminder_sent = False

    def renew_panel(self):
        """Call this when you manually renew the panel"""
        self.activation_time = datetime.now()
        self.first_reminder_sent = False
        self.bot.send_message(self.admin_id, "✅ Panel has been manually renewed.")

    def check_panel(self):
        now = datetime.now()
        elapsed = now - self.activation_time
        remaining = self.panel_duration - elapsed

        # Panel expired
        if remaining.total_seconds() <= 0:
            self.bot.send_message(
                self.admin_id,
                "❌ Your panel has expired! Please renew manually to continue."
            )
            return

        # First reminder: 9 hours before expiry (2d15h after activation)
        first_reminder_time = self.panel_duration - timedelta(hours=9)
        if elapsed >= first_reminder_time and not self.first_reminder_sent:
            self.bot.send_message(
                self.admin_id,
                f"⚠️ Panel will expire in {str(remaining).split('.')[0]}. Please renew manually."
            )
            self.first_reminder_sent = True
