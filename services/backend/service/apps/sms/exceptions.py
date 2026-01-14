class SMSExceptionInvalidPracticeNumber(Exception):
    pass


class SMSExceptionMailingIsDisabled(Exception):
    pass


class SMSRateLimitException(Exception):
    """
    Raised when Dialpad API rate limit is hit (403 or 429 status codes).
    These should not be retried immediately - need backoff period.
    """
    pass


class SMSAuthenticationException(Exception):
    """
    Raised when Dialpad API authentication fails (403 with auth error).
    These require manual intervention - invalid or expired token.
    """
    pass
