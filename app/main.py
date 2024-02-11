from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from users.api.controller import router as user_router
from transcibe.controller import router as transcibe_router
from .db.models import User
from .db.database import engine
from .core.config import settings
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, description=settings.PROJECT_NAME, version="1.0.0")

# Configure CORS
origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    print("app started")


@app.on_event("shutdown")
async def shutdown():
    print("SHUTDOWN")

app.include_router(user_router, prefix='/users')
app.include_router(transcibe_router, prefix='/transcibe')


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)


# admin = Admin(app, engine)


# class UserAdmin(ModelView, model=User):
#     column_list = [User.id, User.username]
#     can_create = True
#     can_edit = True
#     can_delete = False
#     can_view_details = True
#     icon = "fa-solid fa-user"
#     column_searchable_list = [User.username]
#     column_sortable_list = [User.id]
#     column_formatters = {User.username: lambda m, a: m.username[:10]}
#     # column_default_sort = [(User.email, True), (User.username, True)]

# admin.add_view(UserAdmin)