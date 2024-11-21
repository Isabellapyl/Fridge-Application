import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import matplotlib.pyplot as plt
import random

# Constants
WEATHER_API_KEY = 'f17d0ee637c6ba466d1e9442d3722279'
NEWS_API_KEY = '9fedd9f8c5934c9dbf650bb3f4e95766'

# Initialize the main Tkinter application
root = tk.Tk()
root.title("Fridge Application")
root.geometry("1200x900")  # Adjusted width to fit both frames nicely
root.resizable(False, False)

# Global styling
bg_color = "#f0f0f0"
btn_color = "#4CAF50"
btn_hover = "#45a049"
frame_border_color = "#bdbdbd"
entry_color = "#ffffff"
font_main = ("Helvetica", 14)

root.configure(bg=bg_color)

# Apply hover effect to buttons
def on_enter(e):
    e.widget['background'] = btn_hover

def on_leave(e):
    e.widget['background'] = btn_color

# Get geolocation data
def get_geolocation():
    try:
        response = requests.get('http://ip-api.com/json')
        data = response.json()
        if data.get('status') == 'success':
            return data['lat'], data['lon'], data['city']
    except requests.RequestException:
        return None, None, None
    return None, None, None

# Fetch geolocation and weather
lat, lon, city = get_geolocation()

# Get the current weather
def get_current_weather(api_key, city):
    if not city:
        return None, None
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['main']['temp'], data['weather'][0]['description']
    except requests.RequestException:
        return None, None
    return None, None

# Display weather data
def display_weather(city, temp, description):
    if city and temp is not None and description:
        weather_info = f"Current weather for {city}: {temp}°C, {description}"
    else:
        weather_info = "Weather data unavailable"

    tk.Label(weather_frame, text=weather_info, font=('Helvetica', 17, 'bold'), bg="#e6f7ff", wraplength=250,
             justify="left").pack(pady=10)
    emoji = weather_emojis.get(description, "")
    tk.Label(weather_frame, text=emoji, font=('Helvetica', 20), bg="#e6f7ff").pack(pady=10)

# Weather emoji dictionary
weather_emojis = {
    'clear sky': "☀️",
    'few clouds': "⛅",
    'scattered clouds': "☁   ☀  ☁",
    'broken clouds': "☁ ☁ ☀ ☁ ☁",
    'overcast clouds': "☁ ☁ ☁ ☁ ☁\n☁ ☁ ☁ ☁ ☁",
    'light rain': "☁🌧️\n   💧",
    'moderate rain': "☁🌧️🌧️\n  💧💧💧",
    'heavy intensity rain': "☁🌧️🌧️🌧️\n 💧💧💧💧💧",
    'freezing rain': "☁🌧️❄️\n  💧❄️💧",
    'mist': "🌫️🌫️🌫️",
    'smoke': "💨💨💨",
    'haze': "🌫️🌫️🌫️",
    'fog': "🌁🌁🌁",
    'tornado': "🌪️🌪️🌪️",
}

# Fetch predicted weather
def get_predicted_weather(api_key, lat, lon):
    try:
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return [entry['main']['temp'] for entry in data['list'][:5]]
    except requests.RequestException:
        return [14, 15, 13, 12, 11]
    return [14, 15, 13, 12, 11]

# Plot and display predicted weather
def display_predicted_weather():
    if lat and lon:
        predicted_temps = get_predicted_weather(WEATHER_API_KEY, lat, lon)
        days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5']
        plt.figure(figsize=(5, 3))
        plt.plot(days, predicted_temps, marker='o', linestyle='-', label='Predicted Temps', color="blue")
        plt.title(f'5-Day Weather Forecast for {city}')
        plt.xlabel('Days')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.tight_layout()
        plt.savefig("weather_forecast.png")
        forecast_img = Image.open("weather_forecast.png").resize((400, 250))
        forecast_img = ImageTk.PhotoImage(forecast_img)
        tk.Label(forecast_frame, image=forecast_img, bg="#e6f7ff").pack(pady=10)
        forecast_frame.image = forecast_img  # Keep a reference to avoid garbage collection

# Weather Section
weather_frame = tk.Frame(root, width=400, height=350, bg="#e6f7ff", highlightbackground=frame_border_color, highlightthickness=1)
weather_frame.grid(row=0, column=0, padx=10, pady=10)
weather_frame.grid_propagate(False)

# Forecast Section to the right of current weather
forecast_frame = tk.Frame(root, width=300, height=250, bg="#e6f7ff", highlightbackground=frame_border_color, highlightthickness=1)
forecast_frame.grid(row=0, column=1, padx=10, pady=10)
forecast_frame.grid_propagate(False)

current_temp, current_desc = get_current_weather(WEATHER_API_KEY, city)
display_weather(city, current_temp, current_desc)
display_predicted_weather()

# News Section moved directly under the forecast graph
news_frame = tk.Frame(root, width=600, height=200, bg=bg_color, highlightbackground=frame_border_color, highlightthickness=1)
news_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

news_boxes = [
    ("Technology News", "lightyellow"),
    ("Sports News", "lightgreen"),
    ("Health News", "lightpink"),
]
headlines = []

for i, (title, color) in enumerate(news_boxes):
    frame = tk.Frame(news_frame, width=580, height=60, bg=color, highlightbackground=frame_border_color, highlightthickness=1)
    frame.grid(row=i, column=0, padx=10, pady=5)
    frame.grid_propagate(False)
    tk.Label(frame, text=title, font=('Helvetica', 16, 'bold'), bg=color).pack(pady=5)
    headline_label = tk.Label(frame, text="Loading news...", font=('Helvetica', 14), wraplength=560, justify='left', bg=color)
    headline_label.pack(pady=5)
    headlines.append(headline_label)

headline1, headline2, headline3 = headlines

def fetch_news(category):
    try:
        url = f'https://newsapi.org/v2/top-headlines?category={category}&apiKey={NEWS_API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            news_data = response.json()
            return news_data['articles'][:1]
    except requests.RequestException:
        return []
    return []

def display_news():
    for category, label in zip(['technology', 'sports', 'health'], [headline1, headline2, headline3]):
        articles = fetch_news(category)
        label.config(text=articles[0]['title'] if articles else f"No {category} news available.")

display_news()

# Puzzle Corner
puzzle_frame = tk.Frame(root, width=300, height=400, bg="#d6d6d6", highlightbackground=frame_border_color, highlightthickness=1)
puzzle_frame.grid(row=2, column=0, padx=10, pady=10)
puzzle_frame.grid_propagate(False)
tk.Label(puzzle_frame, text="Puzzle Corner", font=('Helvetica', 16), bg="#d6d6d6").pack(pady=5)

# Sudoku Functions (Refactored for readability and conciseness)
def create_sudoku_board():
    base, side = 3, 9
    pattern = lambda r, c: (base * (r % base) + r // base + c) % side
    shuffle = lambda s: random.sample(s, len(s))
    r_base, cols = range(base), shuffle(range(side))
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    for p in random.sample(range(side * side), side * side * 3 // 4):
        board[p // side][p % side] = 0
    return board

def solve_sudoku(board):
    if not (empty := find_empty(board)):
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid_move(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False

def find_empty(board):
    return next(((i, j) for i in range(9) for j in range(9) if board[i][j] == 0), None)

def is_valid_move(board, row, col, num):
    return all(num != board[row][i] for i in range(9)) and \
        all(num != board[i][col] for i in range(9)) and \
        all(num != board[row // 3 * 3 + i][col // 3 * 3 + j] for i in range(3) for j in range(3))

initial_board = create_sudoku_board()
solution_board = [row[:] for row in initial_board]
solve_sudoku(solution_board)
user_answers = {}

# Populate Sudoku grid
entries = []
grid_frame = tk.Frame(puzzle_frame, bg='lightgray')
grid_frame.pack(pady=5)

for i in range(9):
    row_entries = []
    for j in range(9):
        entry = tk.Entry(grid_frame, width=2, font=('Helvetica', 18), justify='center')
        entry.grid(row=i, column=j, padx=2, pady=2)
        entry.bind("<KeyRelease>", lambda e, x=i, y=j: store_user_answer(x, y))
        row_entries.append(entry)
    entries.append(row_entries)

def populate_grid():
    for i in range(9):
        for j in range(9):
            entries[i][j].config(state='normal')
            entries[i][j].delete(0, tk.END)
            if initial_board[i][j] != 0:
                entries[i][j].insert(0, str(initial_board[i][j]))
                entries[i][j].config(state='disabled')
            elif (i, j) in user_answers:
                entries[i][j].insert(0, user_answers[(i, j)])

def store_user_answer(i, j):
    value = entries[i][j].get()
    if value.isdigit() and 1 <= int(value) <= 9:
        user_answers[(i, j)] = value
    elif not value:
        user_answers.pop((i, j), None)

populate_grid()

showing_solution = False

def toggle_solution():
    global showing_solution
    showing_solution = not showing_solution
    for i in range(9):
        for j in range(9):
            entries[i][j].config(state='normal')
            if showing_solution:
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, str(solution_board[i][j]))
                entries[i][j].config(state='disabled')
            else:
                populate_grid()

tk.Button(puzzle_frame, text="Toggle Solution", command=toggle_solution, font=('Helvetica', 12)).pack(pady=5)
tk.Button(puzzle_frame, text="New Game", command=lambda: new_game(), font=('Helvetica', 12)).pack(pady=5)

# Function to verify the user's answers
def verify_answers():
    for i in range(9):
        for j in range(9):
            user_input = entries[i][j].get()
            if not user_input.isdigit() or int(user_input) != solution_board[i][j]:
                messagebox.showerror("Incorrect", "Your solution is incorrect. Please try again.")
                return
    messagebox.showinfo("Correct", "Congratulations! Your solution is correct.")

# Add the Verify Answer button
tk.Button(puzzle_frame, text="Verify Answer", command=verify_answers, font=('Helvetica', 12)).pack(pady=5)

def new_game():
    global initial_board, solution_board, user_answers, showing_solution
    initial_board = create_sudoku_board()
    solution_board = [row[:] for row in initial_board]
    solve_sudoku(solution_board)
    user_answers.clear()  # Clear previous user inputs
    showing_solution = False  # Reset the solution toggle
    populate_grid()  # Populate the grid with the new puzzle

root.mainloop()
