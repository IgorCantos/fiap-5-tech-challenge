from fastapi import APIRouter, HTTPException
from app.schemas import UserCreate, User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


users = []


@router.post("/", response_model=User)
def create_user(user: UserCreate):

    new_user = {
        "id": len(users) + 1,
        **user.model_dump()
    }

    users.append(new_user)

    return new_user



@router.get("/", response_model=list[User])
def get_users():
    return users



@router.get("/{id}", response_model=User)
def get_user(id: int):

    for user in users:
        if user["id"] == id:
            return user

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )



@router.put("/{id}", response_model=User)
def update_user(
    id: int,
    user: UserCreate
):

    for item in users:
        if item["id"] == id:

            item.update(
                user.model_dump()
            )

            return item

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )



@router.delete("/{id}")
def delete_user(id: int):

    for user in users:
        if user["id"] == id:

            users.remove(user)

            return {
                "message": "Usuário removido"
            }


    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado"
    )