from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from hh.config.database.engine import db_helper

ISession: type[AsyncSession] = Annotated[AsyncSession, Depends(db_helper.get_session)]
