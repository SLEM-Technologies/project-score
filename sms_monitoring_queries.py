"""
SMS Error Monitoring Queries

Use these queries to monitor SMS sending health and diagnose 403 errors.
Run these regularly after deploying the fix to track improvements.
"""

# Query 1: Daily error rate summary
daily_error_rate = """
-- Check error rates by day and status
SELECT 
    CAST(created_at AS date) as date,
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY CAST(created_at AS date)), 2) as percentage
FROM apps_smshistory
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY CAST(created_at AS date), status
ORDER BY date DESC, status;
"""

# Query 2: Error breakdown by message
error_breakdown = """
-- Analyze error messages to identify patterns
SELECT 
    CASE 
        WHEN error_message LIKE '%403%' OR error_message LIKE '%Forbidden%' THEN '403 Forbidden'
        WHEN error_message LIKE '%429%' OR error_message LIKE '%rate%limit%' THEN 'Rate Limit'
        WHEN error_message LIKE '%AUTH%' OR error_message LIKE '%authentication%' THEN 'Authentication'
        WHEN error_message LIKE '%CONFIG%' THEN 'Configuration'
        WHEN error_message IS NULL THEN 'Success'
        ELSE 'Other Error'
    END as error_type,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM apps_smshistory
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY error_type
ORDER BY count DESC;
"""

# Query 3: Recent 403 errors with context
recent_403_errors = """
-- Find recent 403 errors with full details
SELECT 
    created_at,
    sent_at,
    status,
    error_message,
    event_context->>'practice_id' as practice_id,
    event_context->>'number_to' as phone_number,
    SUBSTRING(event_context->>'text', 1, 50) as message_preview
FROM apps_smshistory
WHERE error_message LIKE '%403%' 
   OR error_message LIKE '%Forbidden%'
ORDER BY created_at DESC
LIMIT 20;
"""

# Query 4: Send rate per minute (check if we're hitting limits)
send_rate_per_minute = """
-- Check actual send rate per minute
SELECT 
    DATE_TRUNC('minute', sent_at) as minute,
    COUNT(*) as messages_sent,
    CASE 
        WHEN COUNT(*) > 100 THEN '⚠️ Over limit'
        WHEN COUNT(*) > 80 THEN '⚡ High'
        ELSE '✓ Normal'
    END as status
FROM apps_smshistory
WHERE sent_at >= NOW() - INTERVAL '2 hours'
AND status = 'SENT'
GROUP BY DATE_TRUNC('minute', sent_at)
ORDER BY minute DESC
LIMIT 120;
"""

# Query 5: Success rate by hour
hourly_success_rate = """
-- Success rate by hour to identify patterns
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) FILTER (WHERE status = 'SENT') as successful,
    COUNT(*) FILTER (WHERE status = 'ERROR') as errors,
    COUNT(*) FILTER (WHERE status = 'PENDING') as pending,
    ROUND(COUNT(*) FILTER (WHERE status = 'SENT') * 100.0 / COUNT(*), 2) as success_rate_pct
FROM apps_smshistory
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
"""

# Query 6: Re-queued messages (rate limited)
rate_limited_messages = """
-- Find messages that were rate limited and re-queued
SELECT 
    created_at,
    updated_at,
    status,
    error_message,
    event_context->>'practice_id' as practice_id
FROM apps_smshistory
WHERE error_message LIKE '%Rate limited, retrying at%'
   OR error_message LIKE '%rate%limit%'
ORDER BY created_at DESC
LIMIT 50;
"""

# Query 7: Practice-specific error rates
practice_error_rates = """
-- Error rates by practice to identify if specific practices have issues
SELECT 
    event_context->>'practice_id' as practice_id,
    practice.name as practice_name,
    COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE status = 'ERROR') as errors,
    ROUND(COUNT(*) FILTER (WHERE status = 'ERROR') * 100.0 / COUNT(*), 2) as error_rate_pct
FROM apps_smshistory
LEFT JOIN apps_practice practice ON practice.odu_id = event_context->>'practice_id'
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY event_context->>'practice_id', practice.name
HAVING COUNT(*) > 10  -- Only practices with significant volume
ORDER BY error_rate_pct DESC, total_messages DESC
LIMIT 20;
"""

# Query 8: Response time analysis
response_time_analysis = """
-- Analyze time between creation and sending
SELECT 
    EXTRACT(EPOCH FROM (sent_at - created_at)) / 60 as minutes_to_send,
    COUNT(*) as count
FROM apps_smshistory
WHERE sent_at IS NOT NULL
AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY EXTRACT(EPOCH FROM (sent_at - created_at)) / 60
ORDER BY minutes_to_send;
"""

# Query 9: Current queue status
current_queue_status = """
-- Check current SMS event queue
SELECT 
    status,
    COUNT(*) as count,
    MIN(send_at) as earliest_scheduled,
    MAX(send_at) as latest_scheduled
FROM apps_smsevent
GROUP BY status;
"""

# Query 10: Compare before/after fix
before_after_comparison = """
-- Compare error rates before and after the fix
-- Adjust the date to your deployment date
WITH periods AS (
    SELECT 
        CASE 
            WHEN created_at < '2025-11-28' THEN 'Before Fix'
            ELSE 'After Fix'
        END as period,
        status,
        COUNT(*) as count
    FROM apps_smshistory
    WHERE created_at >= '2025-11-27'  -- Adjust to your date range
    GROUP BY period, status
)
SELECT 
    period,
    status,
    count,
    ROUND(count * 100.0 / SUM(count) OVER (PARTITION BY period), 2) as percentage
FROM periods
ORDER BY period, status;
"""

print("SMS Monitoring Queries Loaded")
print("=" * 60)
print("\nAvailable queries:")
print("1. daily_error_rate - Daily error summary")
print("2. error_breakdown - Categorize errors") 
print("3. recent_403_errors - Recent 403 details")
print("4. send_rate_per_minute - Check send rate")
print("5. hourly_success_rate - Hourly success trends")
print("6. rate_limited_messages - Find rate limited SMSs")
print("7. practice_error_rates - Errors by practice")
print("8. response_time_analysis - Time to send")
print("9. current_queue_status - Queue status")
print("10. before_after_comparison - Compare before/after fix")
print("\nUsage: Copy the query variable content and run in your SQL client")
