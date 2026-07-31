import httpx

from app.sources.base import JobSource, SourceJob
from app.sources.utils import clean_html, parse_datetime


class ArbeitnowJobSource(JobSource):
    name = "Arbeitnow"
    endpoint = "https://www.arbeitnow.com/api/job-board-api"

    async def fetch(self, query: str = "", limit: int = 100) -> list[SourceJob]:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(self.endpoint)
            response.raise_for_status()

        normalized_query = query.casefold().strip()
        jobs: list[SourceJob] = []
        for item in response.json().get("data", []):
            searchable = " ".join(
                [item.get("title", ""), item.get("company_name", ""), item.get("location", "")]
            ).casefold()
            if normalized_query and normalized_query not in searchable:
                continue
            job_types = item.get("job_types") or []
            jobs.append(
                SourceJob(
                    external_id=str(item.get("slug") or item["url"]),
                    title=item["title"].strip(),
                    company=item["company_name"].strip(),
                    location=item.get("location") or "Europe",
                    description=clean_html(item.get("description", "")),
                    job_type=", ".join(job_types) or None,
                    is_remote=bool(item.get("remote")),
                    source_name=self.name,
                    source_url=item["url"],
                    published_at=parse_datetime(item.get("created_at")),
                )
            )
            if len(jobs) >= limit:
                break
        return jobs
