import argparse
import sys
from typing import List
from tabulate import tabulate
from src.main import get_recommender, precompute_and_cache
from src.utils import setup_logging, logger
from src.config import ALPHA

def display_results(results: List[dict], title: str):
    """
    Виводить результати у вигляді гарної таблиці.
    """
    if not results:
        print(f"\n--- {title} ---")
        print("Результатів не знайдено.")
        return

    # Додавання рангу
    for i, res in enumerate(results):
        res['rank'] = i + 1

    # Вибір колонок для виводу
    headers = ["Rank", "ID", "Title", "Type", "Score", "Genres", "Year"]
    table_data = []
    for res in results:
        table_data.append([
            res.get('rank'),
            res.get('item_id'),
            res.get('title'),
            res.get('item_type'),
            f"{res.get('score', 0.0):.4f}",
            res.get('genres'),
            res.get('release_year')
        ])

    print(f"\n--- {title} ---")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

def parse_args(args):
    """
    Парсинг аргументів командного рядка.
    """
    parser = argparse.ArgumentParser(
        description="Гібридна рекомендаційна система (Content-based + Item-Item CF).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Глобальні аргументи
    parser.add_argument('--debug', action='store_true', help='Увімкнути режим налагодження (DEBUG logging).')
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Доступні команди')

    # --- recommend ---
    parser_recommend = subparsers.add_parser('recommend', help='Генерує рекомендації для користувача або аноніма.')
    
    # Група для користувача
    user_group = parser_recommend.add_argument_group('Рекомендації для користувача')
    user_group.add_argument('--user-id', type=int, help='ID користувача для рекомендацій.')
    
    # Група для аноніма
    anon_group = parser_recommend.add_argument_group('Рекомендації для аноніма')
    anon_group.add_argument('--anon', action='store_true', help='Режим анонімних рекомендацій.')
    anon_group.add_argument('--liked', type=str, help='Список ID об\'єктів, які сподобалися (через кому), наприклад: 10,12,5.')
    
    parser_recommend.add_argument('--top', type=int, default=10, help='Кількість рекомендацій для повернення (за замовчуванням: 10).')
    parser_recommend.add_argument('--alpha', type=float, default=ALPHA, help=f'Вага для Content-based частини (за замовчуванням: {ALPHA}).')

    # --- similar ---
    parser_similar = subparsers.add_parser('similar', help='Знаходить схожі об\'єкти.')
    parser_similar.add_argument('--item-id', type=int, required=True, help='ID об\'єкта, для якого шукаємо схожі.')
    parser_similar.add_argument('--top', type=int, default=3, help='Кількість схожих об\'єктів для повернення (за замовчуванням: 3).')
    parser_similar.add_argument('--method', type=str, default='hybrid', choices=['hybrid', 'content', 'cf'], help='Метод подібності: hybrid, content або cf (за замовчуванням: hybrid).')

    # --- precompute ---
    parser_precompute = subparsers.add_parser('precompute', help='Примусове (пере)обчислення та кешування матриць/векторів.')
    parser_precompute.add_argument('--force', action='store_true', help='Примусово перерахувати всі дані, ігноруючи кеш.')

    # --- info ---
    parser_info = subparsers.add_parser('info', help='Показати зведену інформацію про об\'єкт.')
    parser_info.add_argument('--item-id', type=int, required=True, help='ID об\'єкта для відображення інформації.')

    return parser.parse_args(args)

def main_cli(args=None):
    """
    Головна функція CLI.
    """
    if args is None:
        args = sys.argv[1:]
        
    try:
        parsed_args = parse_args(args)
    except SystemExit:
        # Якщо argparse викликав SystemExit (наприклад, --help або помилка), просто виходимо
        return

    # Налаштування логування
    setup_logging(parsed_args.debug)
    
    try:
        if parsed_args.command == 'precompute':
            precompute_and_cache(force=parsed_args.force)
            logger.info("Попереднє обчислення завершено.")
            return

        # Для команд, що вимагають рекомендатора, отримуємо його
        recommender = get_recommender()

        if parsed_args.command == 'recommend':
            if parsed_args.user_id is not None and not parsed_args.anon:
                results = recommender.recommend_for_user(parsed_args.user_id, parsed_args.top)
                display_results(results, f"Рекомендації для користувача {parsed_args.user_id}")
            elif parsed_args.anon and parsed_args.liked:
                try:
                    liked_ids = [int(x.strip()) for x in parsed_args.liked.split(',')]
                    results = recommender.recommend_for_anon(liked_ids, parsed_args.top)
                    display_results(results, f"Рекомендації для аноніма (на основі {len(liked_ids)} об'єктів)")
                except ValueError:
                    logger.error("Невірний формат --liked. Використовуйте список чисел через кому, наприклад: 10,12,5")
            else:
                logger.error("Для команди 'recommend' потрібно вказати або --user-id, або --anon та --liked.")

        elif parsed_args.command == 'similar':
            results = recommender.get_similar_items(parsed_args.item_id, parsed_args.top, parsed_args.method)
            display_results(results, f"Схожі об'єкти для Item ID {parsed_args.item_id} (метод: {parsed_args.method})")

        elif parsed_args.command == 'info':
            info = recommender.get_item_info(parsed_args.item_id)
            if info:
                print(f"\n--- Інформація про об'єкт {parsed_args.item_id} ---")
                print(f"Назва: {info['title']}")
                print(f"Тип: {info['item_type']}")
                print(f"Жанри: {info['genres']}")
                print(f"Рік: {info['release_year']}")
                print(f"Автор/Режисер: {info['author_director']}")
                print(f"Середній рейтинг: {info['avg_rating']}")
                print(f"Опис: {info['description'][:100]}...")
            else:
                logger.error(f"Об'єкт з ID {parsed_args.item_id} не знайдено.")

    except Exception as e:
        logger.error(f"Критична помилка виконання: {e}", exc_info=parsed_args.debug)
        sys.exit(1)

if __name__ == '__main__':
    main_cli()
