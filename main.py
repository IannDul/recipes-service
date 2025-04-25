from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from routers.auth_router import auth_router
from routers.recipes_router import recipes_router

app = FastAPI(title='Recipes service')

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_router = APIRouter(prefix='/api/v1')
main_router.include_router(recipes_router)
main_router.include_router(auth_router)
app.include_router(main_router)


if __name__ == '__main__':
    import uvicorn
    from config import settings

    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
