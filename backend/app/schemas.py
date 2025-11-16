from pydantic import BaseModel

# Schema for user registration
class UserLogin(BaseModel):
    email: str
    password: str


# === Схеми для рекомендацій ===

class RecommendedItem(BaseModel):
    """Схема для одного рекомендованого елемента"""
    item_id: int
    title: str
    item_type: str
    genres: str
    release_year: int
    score: float = Field(ge=0.0, le=1.0, description="Оцінка релевантності від 0 до 1")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "item_id": 42,
                "title": "Inception",
                "item_type": "movie",
                "genres": "Sci-Fi;Thriller",
                "release_year": 2010,
                "score": 0.87
            }
        }


class RecommendationResponse(BaseModel):
    """Схема для списку рекомендацій"""
    recommendations: list[RecommendedItem]
    total: int = Field(description="Загальна кількість рекомендацій")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "item_id": 42,
                        "title": "Inception",
                        "item_type": "movie",
                        "genres": "Sci-Fi;Thriller",
                        "release_year": 2010,
                        "score": 0.87
                    }
                ],
                "total": 1
            }
        }