from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Including is_verified means the token auto-invalidates once used
        return f"{user.pk}{timestamp}{user.is_verified}"

email_verification_token = EmailVerificationTokenGenerator()