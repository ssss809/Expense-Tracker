import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import requests

FAVORITES_FILE = "favorites.json"
API_URL = "github.com"

class GitHubUserFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("550x600")
        self.root.minsize(450, 500)
        
        self.favorites = self.load_favorites()
        self.current_user_data = None
        
        self._init_styles()
        self._create_widgets()

    def _init_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=[15, 5])
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))

    def _create_widgets(self):
        # Панель поиска
        search_frame = ttk.LabelFrame(self.root, text=" Поиск профиля GitHub ", padding=10)
        search_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.search_entry = ttk.Entry(search_frame, font=("Segoe UI", 11))
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda event: self.search_user())
        
        search_btn = ttk.Button(search_frame, text="Найти", command=self.search_user, style="Action.TButton")
        search_btn.pack(side=tk.RIGHT)

        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)

        self._build_results_tab()
        self._build_favorites_tab()

    def _build_results_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Результаты поиска")
        
        self.info_text = tk.Text(tab, font=("Consolas", 11), bg="#f8f9fa", state=tk.DISABLED, relief=tk.FLAT)
        self.info_text.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
        
        self.add_fav_btn = ttk.Button(tab, text="⭐ Добавить в избранное", state=tk.DISABLED, command=self.add_to_favorites)
        self.add_fav_btn.pack(fill=tk.X)

    def _build_favorites_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="Избранные пользователи")
        
        # Фильтрация
        filter_frame = ttk.Frame(tab)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(filter_frame, text="Фильтр: ", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        self.filter_entry = ttk.Entry(filter_frame, font=("Segoe UI", 10))
        self.filter_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.filter_entry.bind("<KeyRelease>", lambda event: self.update_favorites_listbox())

        # Список
        self.fav_listbox = tk.Listbox(tab, font=("Segoe UI", 11), selectmode=tk.SINGLE, highlightthickness=0)
        self.fav_listbox.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
        
        # Кнопка удаления
        delete_btn = ttk.Button(tab, text="❌ Удалить из избранного", command=self.delete_from_favorites)
        delete_btn.pack(fill=tk.X)
        
        self.update_favorites_listbox()

    def search_user(self):
        username = self.search_entry.get().strip()
        
        if not username:
            messagebox.showwarning("Валидация", "Поле поиска не должно быть пустым.")
            return

        try:
            response = requests.get(f"{API_URL}{username}", timeout=5)
            if response.status_code == 200:
                self.current_user_data = response.json()
                self._display_user_info()
            elif response.status_code == 404:
                self._clear_info_text("Ошибка: Пользователь не найден.")
                self.add_fav_btn.config(state=tk.DISABLED)
            else:
                self._clear_info_text(f"Ошибка API (Код: {response.status_code})")
        except requests.exceptions.RequestException:
            messagebox.showerror("Сеть", "Не удалось подключиться к GitHub API. Проверьте интернет.")

    def _display_user_info(self):
        data = self.current_user_data
        formatted_info = (
            f" Логин:       {data.get('login')}\n"
            f" Имя:         {data.get('name') or 'Не указано'}\n"
            f" ID:          {data.get('id')}\n"
            f" Компания:    {data.get('company') or 'Нет'}\n"
            f" Репозитории: {data.get('public_repos')}\n"
            f" Подписчики:  {data.get('followers')}\n"
            f" Ссылка:      {data.get('html_url')}"
        )
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", formatted_info)
        self.info_text.config(state=tk.DISABLED)
        self.add_fav_btn.config(state=tk.NORMAL)

    def _clear_info_text(self, message):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", message)
        self.info_text.config(state=tk.DISABLED)

    def add_to_favorites(self):
        if not self.current_user_data:
            return
        
        login = self.current_user_data["login"]
        if login not in self.favorites:
            self.favorites.append(login)
            self.save_favorites()
            self.update_favorites_listbox()
            messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное.")
        else:
            messagebox.showinfo("Инфо", "Пользователь уже находится в избранном.")

    def delete_from_favorites(self):
        selected_index = self.fav_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Выбор", "Выберите пользователя из списка для удаления.")
            return
        
        selected_user = self.fav_listbox.get(selected_index)
        self.favorites.remove(selected_user)
        self.save_favorites()
        self.update_favorites_listbox()

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def update_favorites_listbox(self):
        self.fav_listbox.delete(0, tk.END)
        filter_text = self.filter_entry.get().lower().strip()
        for user in self.favorites:
            if filter_text in user.lower():
                self.fav_listbox.insert(tk.END, user)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinderApp(root)
    root.mainloop()
