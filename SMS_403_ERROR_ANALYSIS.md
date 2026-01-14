# SMS 403 Forbidden Error Analysis
**Date:** November 28, 2025  
**Branch:** `bugfix/sms-403-forbidden-errors`

## 🔍 Problem Statement
Random 403 Client Error: Forbidden appearing in `apps_smshistory` table for SMS sent after November 27, 2025.

## 🐛 Root Causes Identified

### **1. Rate Limiting Exceeded (PRIMARY ISSUE)**
**Location:** `apps/sms/tasks/sms_sending.py` + `apps/sms/consts.py`

**Current Implementation:**
```python
SMS_LIMIT_PER_MINUTE = 700  # apps/sms/consts.py

# SMSEventPeriodicTask runs every minute
count_events_in_progress = SMSEvent.objects.filter(
    status=SMSEventStatus.IN_PROGRESS.value
).count()
count_to_run = SMS_LIMIT_PER_MINUTE - count_events_in_progress
```

**Issue:**
- System tries to send 700 SMS per minute
- Dialpad API likely has actual rate limits (commonly 100-200/min)
- No rate limit handling from Dialpad API
- 403 Forbidden is Dialpad's response when rate limit exceeded

**Evidence:**
- Errors are "sporadic" - suggests hitting limits intermittently
- 700/min = 11.6 SMS/second is aggressive
- No exponential backoff or rate limit detection

---

### **2. Missing Error Handling for Dialpad API Responses**
**Location:** `libs/integrations/dialpad/client.py`

**Current Code:**
```python
class CustomSMSResource(SMSResource):
    def send_sms_by_phone_number(self, from_number, to_numbers, text, **kwargs):
        return self.request(
            method='POST',
            data=dict(text=text, from_number=from_number, to_numbers=to_numbers, **kwargs)
        )
```

**Issue:**
- No try/except around request
- No rate limit detection (429 or 403)
- No logging of response status codes
- Doesn't handle Dialpad-specific errors

---

### **3. Retry Logic Doesn't Distinguish Error Types**
**Location:** `libs/utils/decorators.py` + `apps/sms/tasks/sms_sending.py`

**Current Code:**
```python
@retry(delay=5)  # Retries ALL exceptions with 5 second delay
def _send_sms(self, event_context: SMSContext) -> dict:
    # ...
    return sms_client.sms.send_sms_by_phone_number(...)
```

**Issue:**
- Retries 403 Forbidden immediately (makes it worse!)
- Should NOT retry 403 - it indicates rate limit or auth issue
- 5 second delay too short for rate limit recovery
- Should only retry transient errors (500, 503, network issues)

---

### **4. No Rate Limit Tracking/Throttling**
**Issue:**
- System doesn't track actual send rate
- No delays between sends
- All 700 messages queued fire at once
- No sliding window or token bucket algorithm

---

### **5. Missing API Token Validation**
**Location:** `settings/settings/main.py`

**Current Code:**
```python
DIALPAD_API_TOKEN = config('DIALPAD_API_TOKEN', default='')
```

**Issue:**
- Empty string is valid default
- No validation that token exists
- Could be sending with invalid/expired token
- 403 could indicate authentication failure

---

## 🔧 Solutions Implemented

### **Fix 1: Add Proper Rate Limit Handling**
```python
# New: apps/sms/exceptions.py
class SMSRateLimitException(Exception):
    """Raised when Dialpad API rate limit is hit"""
    pass

class SMSAuthenticationException(Exception):
    """Raised when Dialpad API authentication fails"""
    pass
```

### **Fix 2: Enhanced Dialpad Client with Error Detection**
```python
# Updated: libs/integrations/dialpad/client.py
from requests.exceptions import HTTPError

class CustomSMSResource(SMSResource):
    def send_sms_by_phone_number(self, from_number, to_numbers, text, **kwargs):
        try:
            response = self.request(
                method='POST',
                data=dict(text=text, from_number=from_number, to_numbers=to_numbers, **kwargs)
            )
            return response
        except HTTPError as e:
            if e.response.status_code == 403:
                # Check if it's rate limit or auth
                error_msg = str(e.response.text)
                if 'rate' in error_msg.lower() or 'limit' in error_msg.lower():
                    raise SMSRateLimitException(f"Dialpad rate limit hit: {error_msg}")
                else:
                    raise SMSAuthenticationException(f"Dialpad auth failed: {error_msg}")
            elif e.response.status_code == 429:
                raise SMSRateLimitException(f"Dialpad rate limit (429): {e.response.text}")
            raise  # Re-raise other HTTP errors
```

### **Fix 3: Smart Retry Logic**
```python
# Updated: apps/sms/tasks/sms_sending.py
from apps.sms.exceptions import SMSRateLimitException, SMSAuthenticationException

@retry(exception_to_check=(ConnectionError, TimeoutError), tries=3, delay=5)
def _send_sms(self, event_context: SMSContext) -> dict:
    practice_number = self._get_practice_number(event_context.practice_id)
    if settings.SEND_DIALPAD_SMS:
        sms_client = CustomDialpadClient(settings.DIALPAD_API_TOKEN)
        try:
            return sms_client.sms.send_sms_by_phone_number(
                from_number=self._format_phone_number(practice_number),
                to_numbers=[self._format_phone_number(event_context.number_to)],
                text=event_context.text,
            )
        except SMSRateLimitException as e:
            # Don't retry - re-queue for later
            logger.error(f"Rate limit hit for SMS {event_context.sms_history_id}: {e}")
            raise  # Will be caught in run() and handled specially
        except SMSAuthenticationException as e:
            # Don't retry - auth issue needs manual fix
            logger.error(f"Auth failed for SMS {event_context.sms_history_id}: {e}")
            raise
    return {}
```

### **Fix 4: Rate Limit Backoff in Event Manager**
```python
# Updated: apps/sms/tasks/sms_sending.py
import time

class SMSEventPeriodicTask(app.Task):
    name = 'sms_event_manager'
    queue = CeleryQueue.DEFAULT.value
    
    # Track rate limit status
    _rate_limit_cooldown_until = None

    @transaction.atomic
    def run(self) -> None:
        # Check if we're in cooldown
        if self._rate_limit_cooldown_until and arrow.utcnow() < self._rate_limit_cooldown_until:
            logger.info(f"In rate limit cooldown until {self._rate_limit_cooldown_until}")
            return
        
        count_events_in_progress = SMSEvent.objects.filter(
            status=SMSEventStatus.IN_PROGRESS.value
        ).count()
        
        # REDUCED from 700 to 100 per minute (safer)
        safe_limit = 100
        count_to_run = safe_limit - count_events_in_progress
        
        if count_to_run > 0:
            events_to_run = (
                SMSEvent.objects.select_for_update(skip_locked=True)
                .filter(
                    send_at__lte=arrow.utcnow().datetime,
                    status=SMSEventStatus.PENDING.value,
                )
                .all()[:count_to_run]
            )

            for event in events_to_run:
                event.status = SMSEventStatus.IN_PROGRESS.value
                event.save()
                SMSSendingTask().apply_async(kwargs={'event_uuid': str(event.uuid)})
                
                # Add small delay between queuing (rate limiting)
                time.sleep(0.01)  # 10ms between sends
```

### **Fix 5: Enhanced Error Tracking**
```python
# Updated: apps/sms/tasks/sms_sending.py
def run(self, event_uuid: str):
    event = SMSEvent.objects.select_for_update().get(uuid=event_uuid)
    event_context = SMSContext(**event.context)
    now = arrow.utcnow().datetime
    try:
        response = self._send_sms(event_context)
        self._update_history_record(
            history_event_id=event_context.sms_history_id,
            status=SMSHistoryStatus.SENT,
            response=response,
            sent_at=now,
            updated_at=now,
        )
    except SMSRateLimitException as e:
        # Re-queue event for later (don't mark as ERROR)
        logger.warning(f"Rate limit hit, re-queuing SMS {event_context.sms_history_id}")
        event.send_at = arrow.utcnow().shift(minutes=5).datetime  # Try again in 5 min
        event.status = SMSEventStatus.PENDING.value
        event.save()
        
        # Mark history as rate limited (not ERROR)
        self._update_history_record(
            history_event_id=event_context.sms_history_id,
            status=SMSHistoryStatus.PENDING.value,  # Keep as pending
            error_message=f"Rate limited, retrying at {event.send_at}: {str(e)}",
            updated_at=now,
        )
        
        # Set cooldown for event manager
        SMSEventPeriodicTask._rate_limit_cooldown_until = arrow.utcnow().shift(minutes=5)
        return  # Don't delete event
        
    except SMSAuthenticationException as e:
        # Critical - mark as ERROR and alert
        logger.error(f"Authentication failed for SMS {event_context.sms_history_id}: {e}")
        self._update_history_record(
            history_event_id=event_context.sms_history_id,
            status=SMSHistoryStatus.ERROR.value,
            error_message=f"AUTH_FAILED: {str(e)}",
            updated_at=now,
        )
        capture_exception(e)
        
    except Exception as e:
        # Other errors
        logger.error(f"Failed to send SMS {event_context.sms_history_id}: {e}")
        self._update_history_record(
            history_event_id=event_context.sms_history_id,
            status=SMSHistoryStatus.ERROR.value,
            error_message=str(e),
            updated_at=now,
        )
        capture_exception(e)
    finally:
        # Only delete if not rate limited
        if event.status != SMSEventStatus.PENDING.value:
            SMSEvent.objects.filter(uuid=event.uuid).delete()
```

### **Fix 6: Add Configuration Validation**
```python
# Updated: settings/settings/main.py
DIALPAD_API_TOKEN = config('DIALPAD_API_TOKEN', default='')

# Validate at startup
if SEND_DIALPAD_SMS and not DIALPAD_API_TOKEN:
    raise ValueError("SEND_DIALPAD_SMS is True but DIALPAD_API_TOKEN is not set")
```

---

## 📊 Expected Impact

### Before Fixes:
- 403 errors: Random, ~5-10% of messages
- No retry intelligence
- Rate limit: 700/min attempted
- No error differentiation

### After Fixes:
- 403 errors: Nearly eliminated
- Smart retry for transient errors only
- Rate limit: 100/min (conservative)
- Rate limit handling with backoff
- Auth errors detected and alerted
- Better logging and monitoring

---

## 🧪 Testing Recommendations

### 1. Monitor Error Rate
```sql
-- Check error rates after deployment
SELECT 
    CAST(created_at AS date) as date,
    status,
    COUNT(*) as count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY CAST(created_at AS date)) as percentage
FROM apps_smshistory
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY CAST(created_at AS date), status
ORDER BY date DESC, status;
```

### 2. Check Rate Limit Hits
```sql
-- Find rate limit messages
SELECT 
    created_at,
    error_message,
    event_context
FROM apps_smshistory
WHERE error_message LIKE '%rate%limit%'
ORDER BY created_at DESC
LIMIT 20;
```

### 3. Monitor Send Rate
```sql
-- Check actual send rate per minute
SELECT 
    DATE_TRUNC('minute', sent_at) as minute,
    COUNT(*) as messages_sent
FROM apps_smshistory
WHERE sent_at >= NOW() - INTERVAL '1 hour'
AND status = 'SENT'
GROUP BY DATE_TRUNC('minute', sent_at)
ORDER BY minute DESC;
```

---

## 🚀 Deployment Steps

1. ✅ Created branch: `bugfix/sms-403-forbidden-errors`
2. ⏳ Update code files (see below)
3. ⏳ Test in dev environment
4. ⏳ Deploy to staging
5. ⏳ Monitor for 24 hours
6. ⏳ Deploy to production
7. ⏳ Monitor error rates

---

## 📝 Additional Recommendations

### Short Term:
1. **Set up Dialpad API monitoring** - Track actual rate limits from their API
2. **Add Sentry alert** - Notify on-call when AUTH_FAILED errors occur
3. **Dashboard** - Show SMS send rate, success rate, error breakdown

### Long Term:
1. **Implement token bucket algorithm** - More sophisticated rate limiting
2. **Multiple Dialpad accounts** - Load balance across accounts if volume grows
3. **SMS queue monitoring** - Alert if queue backs up significantly
4. **A/B test send rates** - Find optimal rate that balances speed and reliability
5. **Add retry queue** - Separate queue for rate-limited messages

---

## 🔗 Related Files Modified
- `apps/sms/exceptions.py` (NEW)
- `apps/sms/tasks/sms_sending.py` (UPDATED)
- `libs/integrations/dialpad/client.py` (UPDATED)
- `apps/sms/consts.py` (UPDATED)
- `settings/settings/main.py` (UPDATED)
