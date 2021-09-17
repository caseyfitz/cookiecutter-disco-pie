from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def hello_{{ cookiecutter.service_name.lower().replace('-', '_') }}():
    return {"message": "Hello, {{cookiecutter.service_name}}"}
