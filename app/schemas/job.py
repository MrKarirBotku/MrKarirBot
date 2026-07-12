from pydantic import BaseModel, HttpUrl


class JobRead(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary_min: int | None = None
    salary_max: int | None = None
    source_url: HttpUrl | None = None

    model_config = {"from_attributes": True}
