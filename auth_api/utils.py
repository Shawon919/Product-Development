from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from datetime import datetime,timedelta,timezone


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    expiry_time = timedelta(days=15)

    def _make_hash_value(self, user, timestamp):
        return (user.pk) + (timestamp) + (user.is_active)
    
    def check_token(self, user, token):
        if not super().check_token(user):
            return False
        
        ts_b36 = token.split('-')[1]
        
        try:
            ts_int = self._parse_timestamp(ts_b36)
        except Exception:
            return False
        
        token_time = datetime.fromtimestamp(ts_int,tz=timezone.utc)
        if datetime.now(timezone.utc) - token_time > self.expiry_time:
            return False
        return True
    

email_verification_token = EmailVerificationTokenGenerator()
