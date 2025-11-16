"""
Роутер для ендпоінтів рекомендацій
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import RecommendationResponse, RecommendedItem
from backend.app.recommender.service import RecommenderService
from backend.app.auth import SECRET_KEY, ALGORITHM

router = APIRouter()

# === Dependency Injection ===

def get_recommender_service(db: Session = Depends(get_db)) -> RecommenderService:
    """
    Провайдер RecommenderService.
    
    ВАЖЛИВО: RecommenderService — це "важкий" об'єкт, який завантажує всі дані
    та будує матриці подібності при створенні. Тому ми створюємо його один раз
    при старті FastAPI додатку і використовуємо як singleton.
    
    Але для простоти у цьому прикладі створюємо новий інстанс на кожен запит.
    У production варто використовувати @lru_cache або app.state для кешування.
    """
    return RecommenderService(db=db)


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Витягує поточного користувача з JWT токену.
    
    Очікує заголовок: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизації відсутній",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Перевірка формату "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний формат токену. Очікується: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    try:
        # Декодування JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний токен: user_id відсутній",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний або прострочений токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Пошук користувача в БД
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено"
        )
    
    return user


# === Ендпоінти ===

@router.get(
    "/similar-to/{item_id}",
    response_model=RecommendationResponse,
    summary="Схоже на...",
    description="Повертає список елементів, схожих на вказаний (content-based + CF)"
)
def get_similar_items(
    item_id: int,
    top_n: int = 10,
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Ендпоінт "Схоже на..."
    
    Повертає елементи, подібні до вказаного, використовуючи гібридний підхід
    (content-based + collaborative filtering).
    
    - **item_id**: ID елемента, для якого шукаємо схожі
    - **top_n**: Кількість рекомендацій (за замовчуванням 10)
    """
    try:
        # Викликаємо метод гібридних рекомендацій
        results = recommender.get_hybrid_recommendations(item_id=item_id, top_n=top_n)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Елемент з ID {item_id} не знайдено або немає рекомендацій"
            )
        
        # Перетворюємо у Pydantic моделі
        recommendations = [RecommendedItem(**item) for item in results]
        
        return RecommendationResponse(
            recommendations=recommendations,
            total=len(recommendations)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при генерації рекомендацій: {str(e)}"
        )


@router.get(
    "/for-you",
    response_model=RecommendationResponse,
    summary="Рекомендовано для тебе",
    description="Персоналізовані рекомендації на основі історії користувача"
)
def get_personalized_recommendations(
    top_n: int = 10,
    current_user: User = Depends(get_current_user),
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Ендпоінт "Рекомендовано для тебе"
    
    Повертає персоналізовані рекомендації на основі історії оцінок користувача.
    Вимагає авторизації (JWT токен).
    
    - **top_n**: Кількість рекомендацій (за замовчуванням 10)
    
    Заголовок: Authorization: Bearer <your_jwt_token>
    """
    try:
        # Викликаємо метод персоналізованих рекомендацій
        results = recommender.get_user_recommendations(
            user_id=current_user.id,
            top_n=top_n
        )
        
        if not results:
            # Якщо немає рекомендацій, повертаємо порожній список
            return RecommendationResponse(
                recommendations=[],
                total=0
            )
        
        # Перетворюємо у Pydantic моделі
        recommendations = [RecommendedItem(**item) for item in results]
        
        return RecommendationResponse(
            recommendations=recommendations,
            total=len(recommendations)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при генерації персоналізованих рекомендацій: {str(e)}"
        )


@router.get(
    "/content-based/{item_id}",
    response_model=RecommendationResponse,
    summary="Схоже за контентом",
    description="Рекомендації на основі контенту (опис, жанри, актори)"
)
def get_content_based_similar(
    item_id: int,
    top_n: int = 10,
    recommender: RecommenderService = Depends(get_recommender_service)
):
    """
    Додатковий ендпоінт: тільки content-based рекомендації
    
    Корисно для A/B тестування або порівняння з гібридним підходом.
    """
    try:
        results = recommender.get_content_based_recommendations(item_id=item_id, top_n=top_n)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Елемент з ID {item_id} не знайдено або немає рекомендацій"
            )
        
        recommendations = [RecommendedItem(**item) for item in results]
        
        return RecommendationResponse(
            recommendations=recommendations,
            total=len(recommendations)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка при генерації рекомендацій: {str(e)}"
        )