from typing import AsyncGenerator, Annotated
from fastapi import Depends
from hh.integration.hh.service import HHIntegrationService

async def get_hh_service() -> AsyncGenerator[HHIntegrationService, None]:
    service = HHIntegrationService()
    try:
        yield service
    finally:
        await service.close()

IHHService: type[HHIntegrationService] = Annotated[HHIntegrationService, Depends(get_hh_service)]