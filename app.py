import streamlit as st
import json
import calendar
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

st.set_page_config(page_title="Анализ переписок Telegram")

def date_to_day(date):
    date_object = datetime.strptime(date, '%Y-%m-%d').date()
    return calendar.day_name[date_object.weekday()]

st.title('🔍 Анализ чатов Telegram')

st.write("### Как получить файл чата?")
st.markdown("""
1. Откройте Telegram на ПК.
2. Выберите нужный чат.
3. Нажмите на три точки в правом верхнем углу.
4. Выберите **"Экспорт чата"** и сохраните в формате JSON.
""")

data = st.file_uploader('📂 Загрузите JSON-файл чата', type='json')

if data is not None:
    data = json.load(data)
    participants = {}
    words_dict = {}
    total_msgs = len(data['messages'])
    char_count_dict = {}
    word_count_dict = {}
    person_word_dict = {}
    most_used_words = {}
    date_dict = {}
    time_dict = {}
    day_dict = {}

    min_word_length = st.slider("Минимальная длина слова для анализа:", 2, 6, 3)

    for msg in data['messages']:
        if msg['type'] == 'message':
            sender = msg['from']
            if sender not in participants:
                participants[sender] = 0
                char_count_dict[sender] = 0
                word_count_dict[sender] = 0
                person_word_dict[sender] = {}
                most_used_words[sender] = {}
                day_dict[sender] = {day: 0 for day in calendar.day_name}
                time_dict[sender] = {str(i): 0 for i in range(24)}
                date_dict[sender] = {}
            
            date = msg['date'][:10]
            hour = msg['date'][11:13]
            day = date_to_day(date)
            
            participants[sender] += 1
            date_dict[sender][date] = date_dict[sender].get(date, 0) + 1
            time_dict[sender][hour] += 1
            day_dict[sender][day] += 1
            
            if isinstance(msg['text'], str):
                words = msg['text'].lower().split()
                char_count_dict[sender] += len(msg['text'].replace(" ", ""))
                word_count_dict[sender] += len(words)
                
                for word in words:
                    if len(word) >= min_word_length:
                        words_dict[word] = words_dict.get(word, 0) + 1
                        person_word_dict[sender][word] = person_word_dict[sender].get(word, 0) + 1
    
    words_dict = dict(sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:10])
    for sender in person_word_dict:
        most_used_words[sender] = dict(sorted(person_word_dict[sender].items(), key=lambda x: x[1], reverse=True)[:5])
    
    st.header('📊 Общая статистика')
    st.write(f"Всего сообщений: {total_msgs}")
    st.write(f"Всего слов: {sum(word_count_dict.values())}")
    st.write(f"Всего символов: {sum(char_count_dict.values())}")
    
    st.subheader('🔢 Количество сообщений по участникам')
    st.bar_chart(participants)

    st.subheader('📅 Активность по дням недели')
    day_counts = {day: sum(day_dict[user].get(day, 0) for user in day_dict) for day in calendar.day_name}
    st.bar_chart(day_counts)

    st.subheader('⏰ Активность по часам')
    hour_counts = {str(hour): sum(time_dict[user].get(str(hour), 0) for user in time_dict) for hour in range(24)}
    st.bar_chart(hour_counts)

    st.subheader('📝 Топ-10 самых популярных слов')
    st.bar_chart(words_dict)
    
    st.subheader('☁️ Облако слов')
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(words_dict)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    
    st.subheader('📌 Самые частые слова у каждого участника')
    for user, words in most_used_words.items():
        st.write(f"**{user}**")
        st.bar_chart(words)
    
    st.write('🔍 Разработано с ❤️ для анализа Telegram-чатов!')
