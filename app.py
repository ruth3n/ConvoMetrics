import streamlit as st
import json
from datetime import datetime
import calendar

st.set_page_config(
    page_title="Метрики переписки"
)

def date_to_day(date):
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    return calendar.day_name[date_object.weekday()]

st.title('Анализируй свои чаты: Инсайты Telegram у тебя под рукой!')

# Загрузка JSON-файла с чатом
data = st.file_uploader('Загрузите файл чата', type='json')

text = '''Шаги для получения файла чата:
    1 - Откройте Telegram на ПК
    2 - Перейдите в нужный чат
    3 - Нажмите на три точки в верхнем правом углу
    4 - Выберите "Экспорт чата" и сохраните в формате JSON
'''

st.write(text)

if data is not None:
    data = json.load(data)

    participants = {}  # Подсчёт сообщений по пользователям
    words_dict = {}  # Подсчёт слов по пользователям
    totalmsgs = len(data['messages'])  # Общее количество сообщений

    min_word_length = 3  # Минимальная длина слова для анализа

    char_count_dict = {}  # Количество символов по пользователям
    word_count_dict = {}  # Количество слов по пользователям
    person_word_Dict = {}  # Подсчёт слов по пользователям
    mostUsedWords = {}  # Часто используемые слова
    date_dict = {}  # Подсчёт сообщений по датам
    time_dict = {}  # Подсчёт сообщений по часам
    day_dict = {}  # Подсчёт сообщений по дням недели

    for i in data['messages']:
        if i['type'] == 'message':
            user = i['from']
            if user not in participants:
                mostUsedWords[user] = {}
                participants[user] = 0
                char_count_dict[user] = 0
                word_count_dict[user] = 0
                person_word_Dict[user] = {}
                day_dict[user] = {day: 0 for day in calendar.day_name}
                time_dict[user] = {}
                date_dict[user] = {}

            date_str = i['date'][0:10]
            hour_str = i['date'][11:13]
            participants[user] += 1
            date_dict[user][date_str] = date_dict[user].get(date_str, 0) + 1
            time_dict[user][hour_str] = time_dict[user].get(hour_str, 0) + 1
            day_dict[user][date_to_day(date_str)] += 1

            if isinstance(i['text'], str):
                words = i['text'].lower().split()
                char_count_dict[user] += len(i['text'].replace(" ", ""))
                word_count_dict[user] += len(words)
                for word in words:
                    if len(word) > min_word_length:
                        words_dict[word] = words_dict.get(word, 0) + 1
                        person_word_Dict[user][word] = person_word_Dict[user].get(word, 0) + 1

    words_dict = dict(sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:11])
    mostdays = max(len(date_dict[user]) for user in date_dict)
    for user in participants:
        person_word_Dict[user] = dict(sorted(person_word_Dict[user].items(), key=lambda x: x[1], reverse=True))
    for word in words_dict:
        for user in mostUsedWords:
            mostUsedWords[user][word] = person_word_Dict[user].get(word, 0)

    st.header(f'''Общие метрики
        Всего сообщений - {totalmsgs}
    Всего слов - {sum(word_count_dict.values())}
    Всего символов - {sum(char_count_dict.values())}
    Всего дней с перепиской - {mostdays}
    Всего участников - {len(participants)}''')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader('Количество сообщений')
        st.bar_chart(participants)
    with col2:
        st.subheader('Количество слов')
        st.bar_chart(word_count_dict)
    with col3:
        st.subheader('Количество символов')
        st.bar_chart(char_count_dict)

    st.header('Средние значения')
    st.subheader(f'''Средние значения на сообщение
        Слов - {str(sum(word_count_dict.values())/totalmsgs)[:4]}
    Символов - {str(sum(char_count_dict.values())/totalmsgs)[:5]}''')

    avg_words_per_msg = {user: word_count_dict[user]/participants[user] for user in word_count_dict}
    avg_chars_per_msg = {user: char_count_dict[user]/participants[user] for user in char_count_dict}

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Слов на сообщение')
        st.bar_chart(avg_words_per_msg)
    with col2:
        st.subheader('Символов на сообщение')
        st.bar_chart(avg_chars_per_msg)

    st.subheader(f'''Средние показатели в день
        Сообщений - {str(totalmsgs/mostdays).split('.')[0]}
    Слов - {str(sum(word_count_dict.values())/mostdays).split('.')[0]}
    Символов - {str(sum(char_count_dict.values())/mostdays).split('.')[0]}''')

    col1, col2, col3 = st.columns(3)
    avg_msgs_per_day = {user: participants[user]/mostdays for user in participants}
    avg_words_per_day = {user: word_count_dict[user]/mostdays for user in word_count_dict}
    avg_chars_per_day = {user: char_count_dict[user]/mostdays for user in char_count_dict}
    with col1:
        st.subheader('Сообщений в день')
        st.bar_chart(avg_msgs_per_day)
    with col2:
        st.subheader('Слов в день')
        st.bar_chart(avg_words_per_day)
    with col3:
        st.subheader('Символов в день')
        st.bar_chart(avg_chars_per_day)

    st.header('Самые часто используемые слова')
    st.bar_chart(mostUsedWords)

    st.header('Статистика по датам')
    st.bar_chart(date_dict)

    st.header('Статистика по дням недели')
    st.bar_chart(day_dict)

    st.header('Статистика по часам')
    st.bar_chart(time_dict)

st.write('Сделано с ❤️ от Meet')
st.write('Перевод на русский с ❤️ от ruth3n')
st.write('Оцените проект, если вам понравилось! 🌟')
