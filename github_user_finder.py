from tkinter import *
import json
import requests
from datetime import datetime

window = Tk()
window.title("GitHub User Finder")
window.geometry("1200x800")
window.configure(bg="#f0f0f0")

favorites = []
search_results = []

def search_users():
    global search_results
    username = search_entry.get().strip()
    
    if not username:
        res.config(text="Введите имя пользователя для поиска!", fg="red")
        return
    
    try:
        # GitHub API запрос
        url = f"https://api.github.com/search/users?q={username}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            search_results = data.get('items', [])
            
            # Очищаем список результатов
            results_lb.delete(0, END)
            
            if search_results:
                for user in search_results:
                    user_info = f"{user['login']} | Score: {user['score']:.1f} | {user['html_url']}"
                    results_lb.insert(END, user_info)
                res.config(text=f"Найдено {len(search_results)} пользователей", fg="green")
            else:
                res.config(text="Пользователи не найдены", fg="red")
        else:
            res.config(text=f"Ошибка API: {response.status_code}", fg="red")
            
    except requests.exceptions.RequestException as e:
        res.config(text=f"Ошибка соединения: {str(e)}", fg="red")
    except Exception as e:
        res.config(text=f"Ошибка: {str(e)}", fg="red")

def add_to_favorites():
    selection = results_lb.curselection()
    
    if not selection:
        res.config(text="Выберите пользователя из результатов поиска!", fg="red")
        return
    
    selected_user = search_results[selection[0]]
    username = selected_user['login']
    
    # Проверяем, есть ли уже в избранном
    if any(user['login'] == username for user in favorites):
        res.config(text=f"Пользователь {username} уже в избранном!", fg="orange")
        return
    
    # Добавляем в избранное
    favorites.append(selected_user)
    update_favorites_list()
    save_favorites_to_json()
    res.config(text=f"Пользователь {username} добавлен в избранное!", fg="green")

def remove_from_favorites():
    selection = favorites_lb.curselection()
    
    if not selection:
        res.config(text="Выберите пользователя из избранного для удаления!", fg="red")
        return
    
    removed_user = favorites.pop(selection[0])
    update_favorites_list()
    save_favorites_to_json()
    res.config(text=f"Пользователь {removed_user['login']} удален из избранного!", fg="green")

def get_user_details():
    selection = results_lb.curselection()
    
    if not selection:
        res.config(text="Выберите пользователя для просмотра деталей!", fg="red")
        return
    
    selected_user = search_results[selection[0]]
    
    try:
        # Получаем детальную информацию о пользователе
        url = f"https://api.github.com/users/{selected_user['login']}"
        response = requests.get(url)
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Показываем детали в новом окне
            detail_window = Toplevel(window)
            detail_window.title(f"GitHub User: {user_data['login']}")
            detail_window.geometry("600x500")
            detail_window.configure(bg="#f0f0f0")
            
            Label(detail_window, text=f"GitHub User Details", 
                  font="Arial 20 bold", bg="#f0f0f0").pack(pady=10)
            
            details_text = f"""
            Username: {user_data.get('login', 'N/A')}
            Name: {user_data.get('name', 'N/A')}
            Bio: {user_data.get('bio', 'N/A')}
            Location: {user_data.get('location', 'N/A')}
            Email: {user_data.get('email', 'N/A')}
            Public Repos: {user_data.get('public_repos', 0)}
            Followers: {user_data.get('followers', 0)}
            Following: {user_data.get('following', 0)}
            Created: {user_data.get('created_at', 'N/A')[:10]}
            URL: {user_data.get('html_url', 'N/A')}
            """
            
            Label(detail_window, text=details_text, font="Arial 12", 
                  bg="white", relief="solid", justify=LEFT, padx=20, pady=20).pack(pady=10, padx=20, fill=BOTH, expand=True)
            
            Button(detail_window, text="Закрыть", command=detail_window.destroy,
                  font="Arial 12", bg="#f44336", fg="white", padx=20, pady=5).pack(pady=10)
            
            res.config(text=f"Показаны детали пользователя {user_data['login']}", fg="green")
        else:
            res.config(text=f"Ошибка получения данных: {response.status_code}", fg="red")
            
    except requests.exceptions.RequestException as e:
        res.config(text=f"Ошибка соединения: {str(e)}", fg="red")

def update_favorites_list():
    favorites_lb.delete(0, END)
    for user in favorites:
        user_info = f"★ {user['login']} | Score: {user['score']:.1f}"
        favorites_lb.insert(END, user_info)

def save_favorites_to_json():
    try:
        with open('favorites.json', 'w', encoding='utf-8') as f:
            json.dump(favorites, f, indent=4, ensure_ascii=False)
    except Exception as e:
        res.config(text=f"Ошибка сохранения: {str(e)}", fg="red")

def load_favorites_from_json():
    global favorites
    try:
        with open('favorites.json', 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        update_favorites_list()
    except FileNotFoundError:
        favorites = []
    except Exception as e:
        favorites = []
        res.config(text=f"Ошибка загрузки избранного: {str(e)}", fg="red")

# Заголовок
Label(text="GitHub User Finder", font="Arial 24 bold", 
      bg="#f0f0f0", fg="#333333").place(x=450, y=20)

# Поисковая строка
Label(text="Поиск пользователя GitHub", font="Arial 14", bg="#f0f0f0").place(x=50, y=100)
search_entry = Entry(font="Arial 14", width=30, bg="white", relief="solid")
search_entry.place(x=50, y=130)

Button(text="Поиск", font="Arial 14", command=search_users, 
       bg="#2196F3", fg="white", relief="raised", padx=20).place(x=430, y=125)

# Привязка Enter к поиску
search_entry.bind('<Return>', lambda event: search_users())

# Результаты поиска
Label(text="Результаты поиска", font="Arial 16 bold", bg="#f0f0f0", fg="#333333").place(x=50, y=180)
results_lb = Listbox(font="Arial 11", width=60, height=12, bg="white", 
                     relief="solid", selectbackground="#4CAF50")
results_lb.place(x=50, y=210)

# Кнопки для работы с результатами
Button(text="⭐ В избранное", font="Arial 12", command=add_to_favorites,
       bg="#FF9800", fg="white", padx=10).place(x=50, y=420)

Button(text="📋 Детали", font="Arial 12", command=get_user_details,
       bg="#9C27B0", fg="white", padx=10).place(x=200, y=420)

# Избранное
Label(text="Избранные пользователи", font="Arial 16 bold", bg="#f0f0f0", fg="#333333").place(x=50, y=470)
favorites_lb = Listbox(font="Arial 11", width=60, height=10, bg="white", 
                       relief="solid", selectbackground="#FF9800")
favorites_lb.place(x=50, y=500)

# Кнопка удаления из избранного
Button(text="🗑️ Удалить из избранного", font="Arial 12", command=remove_from_favorites,
       bg="#f44336", fg="white", padx=10).place(x=50, y=680)

# Сообщения
res = Label(font="Arial 10", fg="red", text="Готов к работе", bg="#f0f0f0")
res.place(x=50, y=730)

# Информационная панель справа
info_frame = Frame(window, bg="white", relief="solid", bd=2, width=400)
info_frame.place(x=600, y=100, height=500)

Label(info_frame, text="Как использовать:", font="Arial 14 bold", 
      bg="white", fg="#333333").place(x=10, y=10)

info_text = """
1. Введите имя пользователя GitHub
2. Нажмите "Поиск" или Enter
3. Выберите пользователя из списка
4. Нажмите "⭐ В избранное" или "📋 Детали"
5. Избранное сохраняется автоматически
6. Для удаления выберите в избранном 
   и нажмите "🗑️ Удалить"

GitHub API ограничения:
• 60 запросов/час без аутентификации
• Максимум 1000 результатов поиска
• Rate limit info в заголовках ответа
"""
Label(info_frame, text=info_text, font="Arial 11", bg="white", 
      justify=LEFT).place(x=10, y=40)

# Загрузка избранного при запуске
load_favorites_from_json()

window.mainloop()