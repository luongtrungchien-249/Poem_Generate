"""Periodic scheduler configuration (Celery beat / ARQ cron schedules)."""

BEAT_SCHEDULE = {
    "nightly-evaluations": {
        "task": "entrypoints.worker.tasks.eval_nightly.run_nightly_eval",
        "schedule": "0 2 * * *", # At 02:00 AM every day
        "options": {"queue": "evals"},
    },
    "periodic-memory-compression": {
        "task": "entrypoints.worker.tasks.summarize_memory.run_summarize_memory_task",
        "schedule": "0 */4 * * *", # Every 4 hours
        "options": {"queue": "maintenance"},
    },
}
