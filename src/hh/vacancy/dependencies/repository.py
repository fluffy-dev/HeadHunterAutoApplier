from typing import Annotated
from fastapi import Depends
from hh.vacancy.repository.vacancy import VacancyRepository

IVacancyRepository: type[VacancyRepository] = Annotated[VacancyRepository, Depends()]