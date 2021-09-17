from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def goodbye_{{ cookiecutter.service_name.lower().replace('-', '_') }}():
    return {"message": "Goodbye, {{cookiecutter.service_name}}"}
