from pydantic import UUID4, BaseModel


class Movie(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class MovieResponse(BaseModel):
    id: UUID4
    title: str
    description: str

    class Config:
        orm_mode = True
