# /home/jj/code/HeadHunterAutoApplier/src/hh/vacancy/router.py
from typing import List
from fastapi import APIRouter, HTTPException
from hh.security.dependencies import ICurrentUser
from hh.vacancy.dto import SearchSettingsDTO, SearchSettingsUpdateDTO
from hh.vacancy.dependencies.service import IVacancyService
from hh.integration.hh.dependencies.service import IHHService

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])

@router.get("/settings", response_model=SearchSettingsDTO)
async def get_settings(user: ICurrentUser, service: IVacancyService):
    settings = await service.get_settings(user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@router.put("/settings", response_model=SearchSettingsDTO)
async def update_settings(
    dto: SearchSettingsUpdateDTO,
    user: ICurrentUser,
    service: IVacancyService
):
    return await service.upsert_settings(user.id, dto)

@router.get("/resumes")
async def get_my_resumes(
    user: ICurrentUser,
    service: IVacancyService,
    hh_service: IHHService
):
    """Get resumes from HH to populate dropdowns on frontend."""
    try:
        return await service.get_resumes(user.id, hh_service)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bot/start")
async def start_bot(user: ICurrentUser, service: IVacancyService):
    return await service.set_bot_state(user.id, is_active=True)

@router.post("/bot/stop")
async def stop_bot(user: ICurrentUser, service: IVacancyService):
    return await service.set_bot_state(user.id, is_active=False)