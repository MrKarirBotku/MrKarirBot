from app.database.models.job import Job
from app.services.jobs.sync import create_fingerprint
from app.sources.base import SourceJob
from app.sources.utils import clean_html, normalize_job_type, parse_datetime


def test_fingerprint_deduplicates_case_and_punctuation() -> None:
    first = SourceJob(
        external_id="one",
        title="Customer Support (Remote)",
        company="Example, Inc.",
        location="Indonesia",
        description="First source",
        source_name="Source A",
        source_url="https://example.com/jobs/one",
    )
    second = first.model_copy(
        update={
            "external_id": "two",
            "title": "customer support remote",
            "company": "EXAMPLE INC",
            "source_name": "Source B",
            "source_url": "https://example.org/jobs/two",
        }
    )

    assert create_fingerprint(first) == create_fingerprint(second)


def test_source_normalization_helpers() -> None:
    assert clean_html("<p>Hello&nbsp;<strong>World</strong></p>") == "Hello World"
    assert parse_datetime("2026-07-31T10:15:00Z") is not None
    assert normalize_job_type("Full-time") == "full_time"
    assert normalize_job_type("Intern") == "internship"


def test_job_model_maps_to_existing_supabase_columns() -> None:
    assert "company_name" in Job.__table__.c
    assert "source" in Job.__table__.c
    assert "employment_type" in Job.__table__.c
    assert "deduplication_key" in Job.__table__.c
    assert "channel_posted_at" in Job.__table__.c
