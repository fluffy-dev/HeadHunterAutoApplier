from fastapi import FastAPI


async def lifespan(app: FastAPI):

    #Before app startup

    yield

    #After app startup