# Інструкція для підключення бекенду

## Що вже готово

### 1. API Service (`lib/api.ts`)
- Базовий fetch з авторизацією
- Обробка помилок
- JWT токени
- Методи для рейтингів (CRUD)
- Методи для користувачів (CRUD)
- Методи для watchlist (CRUD)
- Методи для авторизації (login/register/logout)

### 2. Custom Hooks
- `useRatings` - з перемикачем моки/API
- `useProfile` - для роботи з профілем
- `useWatchlist` - для роботи з watchlist

### 3. TypeScript типи
- Всі інтерфейси готові
- User, Rating, WatchlistItem, Book, Movie

## Як підключити бекенд

### Крок 1: Додати environment змінні
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_API=true
```

### Крок 2: Налаштувати токени авторизації
```typescript
// lib/api.ts - перевірити назву токена
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token'); // або 'jwt_token'
};
```

##  Очікувані API endpoints

### Авторизація
```
POST /api/auth/login
POST /api/auth/register  
POST /api/auth/logout
POST /api/auth/refresh
```

### Користувачі
```
GET  /api/users/{userId}/profile
PUT  /api/users/{userId}/profile
GET  /api/users (для адміна)
```

### Рейтинги
```
GET    /api/users/{userId}/ratings?type=book|movie
POST   /api/ratings
PUT    /api/ratings/{ratingId}
DELETE /api/ratings/{ratingId}
```

### Watchlist
```
GET    /api/users/{userId}/watchlist
POST   /api/users/{userId}/watchlist
PUT    /api/users/{userId}/watchlist/{itemId}
DELETE /api/users/{userId}/watchlist/{itemId}
```

## Переваги архітектури

1. **Плавний перехід** - моки → API без змін в компонентах
2. **Fallback** - при помилках API показує моки/localStorage
3. **Loading states** - готові індикатори завантаження
4. **Error handling** - обробка помилок на всіх рівнях
5. **TypeScript** - типізація забезпечує безпеку

## Тестування

Після підключення бекенду протестувати:
- Редагування профілю
- Видалення з watchlist
- Перемикання табів рейтингів
- Пагінація
- Авторизація


**Компоненти не змінюються взагалі!** Вся логіка абстрагована в хуках.
