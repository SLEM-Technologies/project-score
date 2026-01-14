import logging
from cached_property import cached_property

from dialpad import DialpadClient
from dialpad.resources import SMSResource
from requests.exceptions import HTTPError

from apps.sms.exceptions import SMSRateLimitException, SMSAuthenticationException

logger = logging.getLogger(__name__)


class CustomSMSResource(SMSResource):
    def send_sms_by_phone_number(self, from_number, to_numbers, text, **kwargs):
        try:
            response = self.request(
                method='POST',
                data=dict(text=text, from_number=from_number, to_numbers=to_numbers, **kwargs)
            )
            return response
        except HTTPError as e:
            # Log the full error for debugging
            logger.error(f"Dialpad API error: Status {e.response.status_code}, Response: {e.response.text}")
            
            if e.response.status_code == 403:
                # Check if it's rate limit or authentication issue
                error_msg = str(e.response.text).lower()
                if 'rate' in error_msg or 'limit' in error_msg or 'quota' in error_msg:
                    raise SMSRateLimitException(f"Dialpad rate limit hit (403): {e.response.text}")
                else:
                    raise SMSAuthenticationException(f"Dialpad authentication failed (403): {e.response.text}")
            elif e.response.status_code == 429:
                raise SMSRateLimitException(f"Dialpad rate limit (429): {e.response.text}")
            # Re-raise other HTTP errors
            raise


class CustomDialpadClient(DialpadClient):
    @cached_property
    def sms(self):
        return CustomSMSResource(self)
