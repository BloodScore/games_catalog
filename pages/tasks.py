from celery import shared_task
from celery.beat import ScheduleEntry
from django.core import management


@shared_task
def celery_store_games(offset):
    management.call_command('store_games', offset*ScheduleEntry.total_run_count)
    ScheduleEntry.total_run_count += 1
    return f'success {offset * (ScheduleEntry.total_run_count - 1)}'
