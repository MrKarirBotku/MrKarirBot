from app.sources.base import JobSource
from app.sources.manual import ManualJobSource


def get_job_sources() -> list[JobSource]:
    return [ManualJobSource()]
