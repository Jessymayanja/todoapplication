import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .email_utils import send_email

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED QUERY HELPER
# ─────────────────────────────────────────────────────────────────────────────

def get_todos_due_within(hours=0, minutes=0, window_minutes=60,
                          reminder_flag="reminder_sent"):
    """
    Return incomplete, un-reminded todos whose deadline falls inside a
    time window centred on  now + hours + minutes.

    Example — 24-hour window (±60 min):
        window_start = now + 23h
        window_end   = now + 25h

    Example — 5-minute window (±1 min):
        window_start = now + 4min
        window_end   = now + 6min

    The window_start is clamped to now so overdue todos are never matched.
    """
    from .models import Todo

    now         = timezone.now()
    target      = now + timedelta(hours=hours, minutes=minutes)
    half_win    = timedelta(minutes=window_minutes / 2)
    window_start = max(target - half_win, now)   # never go before now
    window_end   = target + half_win

    return (
        Todo.objects.filter(
            deadline__gte=window_start,
            deadline__lte=window_end,
            completion=False,
            **{reminder_flag: False},
        )
        .select_related("user")
    )


# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 — 24-hour reminder
# Celery Beat runs this every 30 minutes.
# It catches every todo whose deadline is between now+23h and now+25h
# and whose 24-hour reminder has not yet been sent.
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_24h_reminders(self):
    todos = get_todos_due_within(
        hours=24,
        minutes=0,
        window_minutes=120,       # ±60 min → catches deadlines in 23h–25h range
        reminder_flag="reminder_sent",
    )

    sent = 0
    failed = 0

    for todo in todos:
        hours_left = (todo.deadline - timezone.now()).total_seconds() / 3600
        logger.info(
            "Sending 24h reminder for todo %s ('%s') to %s",
            todo.id, todo.description, todo.user.email,
        )
        success = send_email(
            to_email=todo.user.email,
            subject=f"⏰ Reminder: '{todo.description}' is due in ~24 hours",
            html_content=f"""
                <div style="font-family:sans-serif;max-width:520px;margin:auto;
                            padding:24px;border:1px solid #e5e7eb;border-radius:8px">
                  <h2 style="color:#0f766e;margin-top:0">⏰ 24-Hour Deadline Reminder</h2>
                  <p>Hi <strong>{todo.user.username}</strong>,</p>
                  <p>Your todo <strong>"{todo.description}"</strong> is due in
                  approximately <strong>{hours_left:.0f} hours</strong>.</p>
                  <table style="width:100%;border-collapse:collapse;margin:16px 0">
                    <tr>
                      <td style="padding:8px;background:#f1f5f9;font-weight:600;
                                 border-radius:4px 0 0 4px;width:120px">Deadline</td>
                      <td style="padding:8px;background:#f8fafc;border-radius:0 4px 4px 0">
                        {todo.deadline.strftime("%A, %d %B %Y at %H:%M UTC")}
                      </td>
                    </tr>
                    <tr>
                      <td style="padding:8px;font-weight:600">Status</td>
                      <td style="padding:8px;color:#dc2626">Incomplete</td>
                    </tr>
                  </table>
                  <p>Log in to your Todo App and mark it complete before the deadline.</p>
                  <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">
                  <p style="color:#94a3b8;font-size:12px;margin:0">
                    Dojo Hub Todo App — automated 24-hour reminder
                  </p>
                </div>
            """,
        )
        if success:
            todo.reminder_sent = True
            todo.save(update_fields=["reminder_sent"])
            sent += 1
            logger.info("24h reminder sent for todo %s", todo.id)
        else:
            failed += 1
            logger.error("24h reminder FAILED for todo %s to %s", todo.id, todo.user.email)

    result = f"24h reminders: {sent} sent, {failed} failed."
    logger.info(result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 — 5-minute reminder
# Celery Beat runs this every 1 minute.
# It catches every todo whose deadline is between now+4min and now+6min
# and whose 5-minute reminder has not yet been sent.
# ─────────────────────────────────────────────────────────────────────────────

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def check_5min_reminders(self):
    todos = get_todos_due_within(
        hours=0,
        minutes=5,
        window_minutes=2,         # ±1 min → catches deadlines in 4min–6min range
        reminder_flag="final_reminder_sent",
    )

    sent = 0
    failed = 0

    for todo in todos:
        logger.info(
            "Sending 5-min reminder for todo %s ('%s') to %s",
            todo.id, todo.description, todo.user.email,
        )
        success = send_email(
            to_email=todo.user.email,
            subject=f" URGENT: '{todo.description}' is due in 5 minutes!",
            html_content=f"""
                <div style="font-family:sans-serif;max-width:520px;margin:auto;
                            padding:24px;border:2px solid #dc2626;border-radius:8px">
                  <h2 style="color:#dc2626;margin-top:0"> Final Reminder — 5 Minutes Left!</h2>
                  <p>Hi <strong>{todo.user.username}</strong>,</p>
                  <p>Your todo <strong>"{todo.description}"</strong> is due at
                  <strong>{todo.deadline.strftime("%H:%M UTC")}</strong> —
                  that is in about <strong>5 minutes</strong>.</p>
                  <p style="color:#dc2626;font-weight:bold;font-size:16px">
                    This is your final reminder. Take action now!
                  </p>
                  <hr style="border:none;border-top:1px solid #fecaca;margin:20px 0">
                  <p style="color:#94a3b8;font-size:12px;margin:0">
                    Dojo Hub Todo App — automated 5-minute reminder
                  </p>
                </div>
            """,
        )
        if success:
            todo.final_reminder_sent = True
            todo.save(update_fields=["final_reminder_sent"])
            sent += 1
            logger.info("5-min reminder sent for todo %s", todo.id)
        else:
            failed += 1
            logger.error("5-min reminder FAILED for todo %s to %s", todo.id, todo.user.email)

    result = f"5-min reminders: {sent} sent, {failed} failed."
    logger.info(result)
    return result