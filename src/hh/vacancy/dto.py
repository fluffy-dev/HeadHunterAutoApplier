from typing import Optional, Literal
from pydantic import BaseModel, Field

class SearchSettingsDTO(BaseModel):
    resume_id: str
    search_text: str
    area_id: str = "113"
    salary: Optional[int] = None
    currency: str = "RUR"
    period: int = 30
    schedule: Optional[str] = None
    employment: Optional[str] = None
    order_by: str = "publication_time"
    cover_letter: Optional[str] = None

class SearchSettingsUpdateDTO(SearchSettingsDTO):
    pass

class ApplicationLogDTO(BaseModel):
    vacancy_id: str
    status: str
    created_at: str