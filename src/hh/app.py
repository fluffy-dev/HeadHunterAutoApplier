import logging

from fastapi import FastAPI

from hh.config.project import settings as main_settings
from hh.config.swagger import settings as swagger_settings
from hh.config.logging import settings as logging_settings, logger_config

from hh.lifespan import lifespan

from hh.middleware import init_middleware

from hh.router import router


def get_app() -> FastAPI:
    if logging_settings.logging_on:
        logging.config.dictConfig(logger_config) # noqa

    app = FastAPI(
        title=swagger_settings.title,
        # description=get_description(swagger_settings.description),
        summary=swagger_settings.summary,
        version=main_settings.version,
        terms_of_service=swagger_settings.terms_of_service,
        contact=swagger_settings.contact,
        license_info=swagger_settings.license,
        lifespan=lifespan,
        root_path=main_settings.root_path,
        debug=main_settings.debug,
        docs_url=swagger_settings.docs_url if main_settings.debug else None,
        redoc_url=swagger_settings.redoc_url if main_settings.debug else None,
        openapi_url=f"{swagger_settings.docs_url}/openapi.json" if main_settings.debug else None,
    )

    init_middleware(app)

    app.include_router(router)

    return app


app = get_app()