import httpx

from app.sources.base import JobSource, SourceJob
from app.sources.utils import clean_html, normalize_job_type, parse_datetime


class RemotiveJobSource(JobSource):
    name = "Remotive"
    endpoint = "https://remotive.com/api/remote-jobs"

    async def fetch(self, query: str = "", limit: int = 100) -> list[SourceJob]:
        params = {"limit": limit}
        if query:
            params["search"] = query
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(self.endpoint, params=params)
            response.raise_for_status()

        jobs: list[SourceJob] = []
        for item in response.json().get("jobs", [])[:limit]:
            jobs.append(
                SourceJob(
                    external_id=str(item["id"]),
                    title=item["title"].strip(),
                    company=item["company_name"].strip(),
                    location=item.get("candidate_required_location") or "Remote",
                    description=clean_html(item.get("description", "")),
                    salary_text=item.get("salary") or None,
                    job_type=normalize_job_type(item.get("job_type")),
                    is_remote=True,
                    source_name=self.name,
                    source_url=item["url"],
                    published_at=parse_datetime(item.get("publication_date")),
                )
            )
        return jobs
