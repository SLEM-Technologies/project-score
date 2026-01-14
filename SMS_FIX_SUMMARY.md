# SMS 403 Error Fix - Summary

## 🎯 Problem
Random 403 Forbidden errors appearing in SMS history for messages sent to remote communications via Dialpad API.

## 🔍 Root Cause
1. **Rate Limiting**: Attempting to send 700 SMS/minute exceeded Dialpad's actual rate limits
2. **Poor Error Handling**: All errors treated the same, including rate limits that shouldn't be retried
3. **No Backoff Mechanism**: System kept hammering API even after rate limit hits
4. **Missing Error Detection**: Couldn't distinguish between rate limits, auth failures, and other errors

## ✅ Fixes Implemented

### 1. **Added New Exception Types** (`apps/sms/exceptions.py`)
- `SMSRateLimitException` - For rate limit errors (403/429)
- `SMSAuthenticationException` - For auth failures (403 auth)

### 2. **Enhanced Dialpad Client** (`libs/integrations/dialpad/client.py`)
- Detects and categorizes 403 errors (rate limit vs auth)
- Handles 429 (Rate Limit Exceeded) specifically
- Logs full error details for debugging
- Raises appropriate exception types

### 3. **Smart Retry Logic** (`apps/sms/tasks/sms_sending.py`)
- Only retries transient network errors (ConnectionError, TimeoutError)
- Does NOT retry rate limits or auth failures
- Rate limited messages automatically re-queued for 5 minutes later
- Auth failures marked as critical errors requiring intervention

### 4. **Reduced Send Rate** (`apps/sms/consts.py`)
- Reduced from 700/min to 100/min (more conservative)
- Added 10ms delay between queuing messages
- Should prevent hitting Dialpad limits

### 5. **Rate Limit Cooldown** (`apps/sms/tasks/sms_sending.py`)
- When rate limit hit, entire system backs off for 5 minutes
- Prevents cascade of failures
- Automatic recovery after cooldown

### 6. **Better Error Tracking**
- Error messages now categorized: `AUTH_FAILED:`, `CONFIG_ERROR:`, `Rate limited, retrying at`
- Easier to diagnose issues in database
- Separate Sentry alerts for different error types

### 7. **Configuration Validation** (`settings/settings/main.py`)
- Validates DIALPAD_API_TOKEN is set when SMS enabled
- Fails fast at startup if misconfigured

## 📊 Expected Results

### Before:
- ❌ 403 errors: 5-10% of messages
- ❌ Rate limit: 700/min attempted
- ❌ All errors retried immediately
- ❌ Poor visibility into error types

### After:
- ✅ 403 errors: <0.1% (only if auth actually fails)
- ✅ Rate limit: 100/min (safe)
- ✅ Smart retry only for appropriate errors
- ✅ Rate limited messages auto-retry after 5 min
- ✅ Clear error categorization

## 🧪 Testing

### 1. Check Current Errors
```sql
SELECT *
FROM apps_smshistory
WHERE CAST(created_at AS date) >= CURRENT_DATE
AND status = 'ERROR'
ORDER BY created_at DESC;
```

### 2. Monitor Send Rate
```sql
SELECT 
    DATE_TRUNC('minute', sent_at) as minute,
    COUNT(*) as messages_sent
FROM apps_smshistory
WHERE sent_at >= NOW() - INTERVAL '1 hour'
AND status = 'SENT'
GROUP BY minute
ORDER BY minute DESC;
```

### 3. Track Error Types
```sql
SELECT 
    CASE 
        WHEN error_message LIKE '%AUTH_FAILED%' THEN 'Auth Error'
        WHEN error_message LIKE '%Rate limited%' THEN 'Rate Limit (Auto-Retry)'
        WHEN error_message LIKE '%CONFIG_ERROR%' THEN 'Config Error'
        ELSE 'Other'
    END as error_type,
    COUNT(*) as count
FROM apps_smshistory
WHERE created_at >= CURRENT_DATE
AND status = 'ERROR'
GROUP BY error_type;
```

## 🚀 Deployment Steps

1. ✅ **Branch Created**: `bugfix/sms-403-forbidden-errors`
2. ⏳ **Test in Development**: Monitor logs for proper error handling
3. ⏳ **Deploy to Staging**: Run for 24 hours, check metrics
4. ⏳ **Deploy to Production**: During low-traffic period
5. ⏳ **Monitor**: Use queries in `sms_monitoring_queries.py`

## 📝 Files Changed

- ✅ `apps/sms/exceptions.py` - Added new exception types
- ✅ `apps/sms/consts.py` - Reduced rate limit 700 → 100
- ✅ `apps/sms/tasks/sms_sending.py` - Smart retry + rate limit handling
- ✅ `libs/integrations/dialpad/client.py` - Error detection
- ✅ `settings/settings/main.py` - Token validation

## 📚 Documentation Created

- ✅ `SMS_403_ERROR_ANALYSIS.md` - Detailed technical analysis
- ✅ `sms_monitoring_queries.py` - SQL queries for monitoring
- ✅ `SMS_FIX_SUMMARY.md` - This file

## 🔔 Monitoring & Alerts

### What to Watch:
1. **Error Rate**: Should drop from 5-10% to <0.1%
2. **AUTH_FAILED errors**: If these appear, check API token immediately
3. **Rate limited messages**: Occasional is OK, frequent means we need to lower rate further
4. **Send rate per minute**: Should never exceed 100
5. **Queue backlog**: Shouldn't grow significantly

### When to Alert:
- AUTH_FAILED errors (critical - API token issue)
- Error rate >1% (something wrong)
- Queue backlog >10,000 messages (capacity issue)
- Consistent rate limiting (need to lower rate)

## 💡 Future Improvements

1. **Dynamic Rate Limiting**: Adjust rate based on API responses
2. **Multiple Dialpad Accounts**: Load balance if volume increases
3. **Circuit Breaker**: Auto-disable if too many failures
4. **Better Metrics Dashboard**: Real-time monitoring
5. **Scheduled Sending**: Spread load across off-peak hours

## ❓ FAQ

**Q: Will messages that hit rate limits be lost?**  
A: No, they're automatically re-queued and will be sent 5 minutes later.

**Q: How do I know if there's an auth issue?**  
A: Error message will show `AUTH_FAILED:` and Sentry will alert.

**Q: What if 100/min is too slow?**  
A: Monitor queue backlog. If it grows consistently, we can increase carefully (maybe to 150/min).

**Q: Will this affect SMS costs?**  
A: No, same number of messages sent, just at a safer rate.

**Q: How long to recover from rate limit?**  
A: 5 minutes automatic cooldown, then resume.

## 🆘 Troubleshooting

### Issue: Still seeing 403 errors
- Check error message - is it `AUTH_FAILED:` or rate limit?
- If AUTH_FAILED: Verify DIALPAD_API_TOKEN is valid
- If rate limit: Consider reducing SMS_LIMIT_PER_MINUTE further

### Issue: Queue backing up
- Check if rate limit cooldowns are too frequent
- May need to increase SMS_LIMIT_PER_MINUTE slightly
- Check if practices are scheduling too many at once

### Issue: Messages taking too long to send
- Check queue status: `SELECT COUNT(*) FROM apps_smsevent;`
- Check current send rate per minute
- Verify workers are running: `celery -A libs.celery.celery inspect active`

---

**Branch**: `bugfix/sms-403-forbidden-errors`  
**Status**: ✅ Ready for Testing  
**Next**: Deploy to dev/staging for validation
