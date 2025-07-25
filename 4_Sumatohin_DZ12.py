import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import F
from collections import defaultdict

bot = Bot(token="7599159158:AAFBKNHna16td-Kcfnkmaxbpc_GdrkA9LqM")
dp = Dispatcher()

# Данные для квиза (вопросы и варианты ответов)
quiz_data = [
    {
        'question': '1. Что такое Python?',
        'options': [
            'Язык программирования высокого уровня',
            'База данных',
            'Графический редактор',
            'Операционная система'
        ],
        'correct_option': 0
    },
    {
        'question': '2. Работу с какими типами данных поддерживает Python?',
        'options': [
            'Целые числа, строки, списки, словари',
            'Только числа и строки',
            'Только числовые типы',
            'Только текстовые данные'
        ],
        'correct_option': 0
    },
    {
        'question': '3. Что такое PEP 8?',
        'options': [
            'Руководство по стилю кода Python',
            'Версия Python 8',
            'Модуль для работы с датами',
            'Протокол передачи данных'
        ],
        'correct_option': 0
    },
    {
        'question': '4. Как в Python работает умножение строк?',
        'options': [
            'Повторяет строку указанное количество раз',
            'Конкатенирует строки',
            'Преобразует строку в число и умножает',
            'Умножение строк не поддерживается'
        ],
        'correct_option': 0
    },
    {
        'question': '5. Как в Python работает умножение списков?',
        'options': [
            'Повторяет элементы списка указанное количество раз',
            'Перемножает элементы списка между собой',
            'Создает матрицу из списков',
            'Умножение списков не поддерживается'
        ],
        'correct_option': 0
    },
    {
        'question': '6. В чем разница между списками и кортежами?',
        'options': [
            'Списки изменяемы, кортежи нет',
            'Кортежи изменяемы, списки нет',
            'Кортежи могут содержать только числа',
            'Разницы нет, это одно и то же'
        ],
        'correct_option': 0
    },
    {
        'question': '7. Как развернуть список в Python?',
        'options': [
            'Использовать срез [::-1]',
            'Метод reverse()',
            'Функция reversed()',
            'Все варианты верны'
        ],
        'correct_option': 3
    },
    {
        'question': '8. Как работает функция range?',
        'options': [
            'Генерирует последовательность чисел',
            'Возвращает случайное число в заданном диапазоне',
            'Находит диапазон значений в списке',
            'Создает диапазон дат'
        ],
        'correct_option': 0
    },
    {
        'question': '9. Что можно использовать в качестве ключа словаря?',
        'options': [
            'Неизменяемые типы данных',
            'Любые типы данных',
            'Только строки',
            'Только числа'
        ],
        'correct_option': 0
    },
    {
        'question': '10. Как выполняется код на Python?',
        'options': [
            'Интерпретируется построчно',
            'Компилируется в машинный код',
            'Преобразуется в байт-код Java',
            'Все варианты верны'
        ],
        'correct_option': 0
    },
    {
        'question': '11. Где поиск выполняется быстрей: в списках или словарях?',
        'options': [
            'В словарях (O(1) в среднем)',
            'В списках (O(1))',
            'Скорость одинаковая',
            'Зависит от размера данных'
        ],
        'correct_option': 0
    }
]

# Хранилища данных
user_quiz_index = {}  # Текущий вопрос для пользователя
user_answers = {}     # Ответы пользователя
user_stats = defaultdict(dict)  # Статистика пользователей
user_shuffled_options = {}  # Перемешанные варианты ответов

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Моя статистика"))
    await message.answer(
        "Добро пожаловать в Python квиз!\n"
        "Проверьте свои знания языка Python.\n"
        "Нажмите 'Начать игру' или введите /quiz",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Хэндлер на кнопку "Моя статистика" и команду /stats
@dp.message(F.text == "Моя статистика")
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    stats = user_stats.get(user_id, {})
    
    if not stats:
        await message.answer("Вы еще не играли в квиз. Начните игру!")
    else:
        await message.answer(
            f"📊 Ваша статистика:\n"
            f"Последний результат: {stats.get('last_score', 0)}/{len(quiz_data)}\n"
            f"Всего игр: {stats.get('total_played', 0)}"
        )

# Хэндлер на кнопку "Начать игру" и команду /quiz
@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    await new_quiz(message)

# Обработчик ответов
@dp.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    current_index = await get_quiz_index(user_id)
    
    question_data = quiz_data[current_index]
    shuffled_options = user_shuffled_options[user_id][current_index]
    selected_option = int(callback.data.split("_")[1])
    
    original_correct_option = question_data['options'][question_data['correct_option']]
    correct_option_index = shuffled_options.index(original_correct_option)
    is_correct = selected_option == correct_option_index
    
    user_answers[user_id] = user_answers.get(user_id, [])
    user_answers[user_id].append({
        'question': question_data['question'],
        'selected': shuffled_options[selected_option],
        'correct': original_correct_option,
        'is_correct': is_correct
    })
    
    if is_correct:
        response_message = f"✅ Ваш ответ: {shuffled_options[selected_option]}\nПравильно!"
    else:
        response_message = f"❌ Ваш ответ: {shuffled_options[selected_option]}\n✅ Правильный ответ: {original_correct_option}"
    
    await callback.message.answer(response_message)
    
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass
    
    current_index += 1
    if current_index < len(quiz_data):
        await update_quiz_index(user_id, current_index)
        await get_question(callback.message, user_id)
    else:
        correct_answers = sum(1 for ans in user_answers[user_id] if ans['is_correct'])
        total_questions = len(quiz_data)
        
        user_stats[user_id]['last_score'] = correct_answers
        user_stats[user_id]['total_played'] = user_stats[user_id].get('total_played', 0) + 1
        
        # Формирование сообщения с результатами
        result_message = (
            f"🎉 Квиз завершен!\n"
            f"Ваш результат: {correct_answers}/{total_questions}\n\n"
            f"📝 Детализация ответов:\n"
        )
        
        # Добавляем детализацию по каждому вопросу без дублирования номеров
        for i, answer in enumerate(user_answers[user_id], 1):
            # Убираем номер из вопроса, так как мы добавляем его сами
            question_text = answer['question'].split('. ', 1)[1] if '. ' in answer['question'] else answer['question']
            
            if answer['is_correct']:
                result_message += (
                    f"{i}. {question_text}\n"
                    f"   ✅ Ваш ответ: {answer['selected']}\n"
                    f"   (Правильно)\n\n"
                )
            else:
                result_message += (
                    f"{i}. {question_text}\n"
                    f"   ❌ Ваш ответ: {answer['selected']}\n"
                    f"   ✅ Правильный ответ: {answer['correct']}\n\n"
                )
        
        await callback.message.answer(result_message)
        await update_quiz_index(user_id, 0)
        del user_shuffled_options[user_id]

# Функция генерации кнопок
def generate_options_keyboard(options):
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{index}"
        ))
    builder.adjust(1)
    return builder.as_markup()

# Функция для получения вопроса
async def get_question(message, user_id):
    current_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_index]
    
    # Перемешиваем варианты ответов для этого вопроса
    shuffled_options = question_data['options'].copy()
    random.shuffle(shuffled_options)
    
    # Сохраняем перемешанные варианты
    if user_id not in user_shuffled_options:
        user_shuffled_options[user_id] = {}
    user_shuffled_options[user_id][current_index] = shuffled_options
    
    kb = generate_options_keyboard(shuffled_options)
    await message.answer(question_data['question'], reply_markup=kb)

# Функция для запуска квиза
async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    user_answers[user_id] = []  # Очищаем предыдущие ответы
    await message.answer("Давайте начнём квиз! Отвечайте на вопросы по порядку:")
    await get_question(message, user_id)

async def update_quiz_index(user_id, index):
    user_quiz_index[user_id] = index

async def get_quiz_index(user_id):
    return user_quiz_index.get(user_id, 0)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())