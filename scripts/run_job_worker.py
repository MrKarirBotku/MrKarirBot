import asyncio
import logging

from app.core.logging import configure_logging
from app.workers.jobs import run_forever

if __name__ == "__main__":
    configure_logging()
    logging.getLogger(__name__).info("starting_job_worker")
    asyncio.run(run_forever())
