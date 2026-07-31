from app.sources.arbeitnow import ArbeitnowJobSource
from app.sources.base import JobSource
from app.sources.remotive import RemotiveJobSource


def get_job_sources() -> list[JobSource]:
    return [RemotiveJobSource(), ArbeitnowJobSource()]
