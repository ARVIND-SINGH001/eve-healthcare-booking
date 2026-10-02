from pydantic import BaseModel, ConfigDict, Field


class CentreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    location: str = Field(min_length=1, max_length=255)


class CentreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    location: str


class CentreTestCreate(BaseModel):
    test_name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    price: float = Field(ge=0)


class CentreTestResponse(BaseModel):
    offering_id: int
    centre_id: int
    centre_name: str
    test_id: int
    test_name: str
    description: str | None
    price: float
