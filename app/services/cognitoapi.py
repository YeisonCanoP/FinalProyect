import asyncio
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import os
import sys
sys.path.append('c:/Users/yeiso/OneDrive/Escritorio/Proyecto/final_proyect')
from app.modules.vtgier.consulta import Vtiger
from app.routers.routerApi import RouterApiCognito


congitoRouter = RouterApiCognito()
app = FastAPI(
    title="Vizora API",
    description="API for Vizora application, providing authentication and data management.",
    version="1.0.0",
)
app.add_middleware(SessionMiddleware, secret_key=os.urandom(24))

app.include_router(
    congitoRouter.router,
    prefix="/cognito",
)



