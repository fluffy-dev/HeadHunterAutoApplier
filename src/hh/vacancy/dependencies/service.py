from typing import Annotated
from fastapi import Depends
from hh.vacancy.service import VacancyService
from hh.vacancy.dependencies.repository import IVacancyRepository

def get_vacancy_service(repo: IVacancyRepository) -> VacancyService:
    return VacancyService(repo)

IVacancyService: type[VacancyService] = Annotated[VacancyService, Depends(get_vacancy_service)]