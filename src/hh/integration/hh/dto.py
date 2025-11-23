# /home/jj/code/HeadHunterAutoApplier/src/hh/integration/hh/dto.py
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class HHVacancyItemDTO(BaseModel):
    id: str
    name: str
    salary: Optional[dict[str, Any]] = None
    employer: dict[str, Any]
    alternate_url: str

class HHSearchResultsDTO(BaseModel):
    items: List[HHVacancyItemDTO]
    found: int
    pages: int
    page: int

class HHNegotiationPayloadDTO(BaseModel):
    vacancy_id: str
    resume_id: str
    message: str

class HHTokenDTO(BaseModel):
    """Response from HH OAuth /token endpoint"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int