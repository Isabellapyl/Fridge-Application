import tkinter as tk
from tkinter import messagebox, ttk
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


# Global variable to track temperature unit
is_celsius = True


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


# Toggle temperature unit
def toggle_temperature_unit():
    global is_celsius, current_temp, current_desc
    is_celsius = not is_celsius

    # Convert temperature and update button text
    if current_temp is not None:
        if is_celsius:
            temp = current_temp  # Convert to Celsius
            unit = "°C"
            toggle_btn.config(text="Switch to °F")  # Update button text
        else:
            temp = (current_temp * 9 / 5) + 32  # Convert to Fahrenheit
            unit = "°F"
            toggle_btn.config(text="Switch to °C")  # Update button text

        # Update the weather display
        weather_info = f"Current weather for {city}: {temp:.1f}{unit}, {current_desc}"
        for widget in weather_frame.winfo_children():
            if isinstance(widget, tk.Label):  # Clear and update only labels
                widget.destroy()
        tk.Label(weather_frame, text=weather_info, font=('Helvetica', 17, 'bold'), bg="#e6f7ff", wraplength=250,
                 justify="left").pack(pady=10)
        emoji = weather_emojis.get(current_desc, "")
        tk.Label(weather_frame, text=emoji, font=('Helvetica', 20), bg="#e6f7ff").pack(pady=10)


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
weather_frame = tk.Frame(root, width=400, height=350, bg="#e6f7ff", highlightbackground=frame_border_color,
                         highlightthickness=1)
weather_frame.grid(row=0, column=0, sticky="nsew")
weather_frame.grid_propagate(False)

# Add toggle button
toggle_btn = tk.Button(weather_frame, text="Switch to °F", command=toggle_temperature_unit, font=('Helvetica', 12),
                       bg=btn_color, fg="white", relief="raised")
toggle_btn.pack(pady=10)
toggle_btn.bind("<Enter>", on_enter)
toggle_btn.bind("<Leave>", on_leave)

# Forecast Section to the right of current weather
forecast_frame = tk.Frame(root, width=400, height=350, bg="#e6f7ff", highlightbackground=frame_border_color,
                          highlightthickness=1)
forecast_frame.grid(row=0, column=1, sticky="nsew")
forecast_frame.grid_propagate(False)

current_temp, current_desc = get_current_weather(WEATHER_API_KEY, city)
display_weather(city, current_temp, current_desc)
display_predicted_weather()


# Puzzle Corner in the bottom left
puzzle_frame = tk.Frame(root, bg="#d6d6d6", highlightbackground=frame_border_color, highlightthickness=1)
puzzle_frame.grid(row=1, column=0, sticky="nsew")
puzzle_frame.grid_propagate(False)
tk.Label(puzzle_frame, text="Puzzle Corner", font=('Helvetica', 16), bg="#d6d6d6").pack(pady=5)

# Sudoku Functions
difficulty = 'Medium'  # Default difficulty level

def create_sudoku_board():
    base, side = 3, 9
    pattern = lambda r, c: (base * (r % base) + r // base + c) % side
    shuffle = lambda s: random.sample(s, len(s))
    r_base, cols = range(base), shuffle(range(side))
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    # Set the number of cells to clear based on the difficulty
    if difficulty == 'Easy':
        num_to_clear = side * side * 1 // 4
    elif difficulty == 'Medium':
        num_to_clear = side * side * 3 // 4
    elif difficulty == 'Hard':
        num_to_clear = side * side * 7 // 8
    else:
        num_to_clear = side * side * 3 // 4

    for p in random.sample(range(side * side), num_to_clear):
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

# Initialize Sudoku Boards
initial_board = create_sudoku_board()
solution_board = [row[:] for row in initial_board]
solve_sudoku(solution_board)
user_answers = {}

# Function to validate the input
def validate_input(new_value):
    # Allow empty input (to clear entries) or digits between 1 and 9
    if new_value == "" or (new_value.isdigit() and 1 <= int(new_value) <= 9):
        return True
    return False

# Register the validation function
validate_cmd = root.register(validate_input)

# Populate Sudoku grid with validation
entries = []
grid_frame = tk.Frame(puzzle_frame, bg='lightgray')
grid_frame.pack(pady=5)

for i in range(9):
    row_entries = []
    for j in range(9):
        entry = tk.Entry(
            grid_frame, width=2, font=('Helvetica', 18), justify='center',
            validate="key", validatecommand=(validate_cmd, "%P")  # Add validation
        )
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

# Function for generating a new game
def new_game():
    global initial_board, solution_board, user_answers
    # Generate a new board and solution
    initial_board = create_sudoku_board()
    solution_board = [row[:] for row in initial_board]
    solve_sudoku(solution_board)

    # Clear previous user inputs
    user_answers.clear()

    # Populate the grid with the new puzzle
    populate_grid()

    # Schedule the next new game after 10 minutes (600,000 ms)
    root.after(600000, new_game)

# Dropdown menu for difficulty selection
def set_difficulty(event):
    global difficulty
    difficulty = difficulty_var.get()
    new_game()  # Start a new game when difficulty changes

difficulty_var = tk.StringVar(value='Medium')
difficulty_menu = ttk.Combobox(puzzle_frame, textvariable=difficulty_var, values=['Easy', 'Medium', 'Hard'], state="readonly")
difficulty_menu.bind("<<ComboboxSelected>>", set_difficulty)
difficulty_menu.pack(pady=5)

# Start the first automatic new game
new_game()

# News Section in the bottom right
news_frame = tk.Frame(root, width=400, height=350, bg=bg_color, highlightbackground=frame_border_color, highlightthickness=1)
news_frame.grid(row=1, column=1, sticky="nsew")
news_frame.grid_propagate(False)

news_boxes = [
    ("Technology News", "lightyellow"),
    ("Sports News", "lightgreen"),
    ("Health News", "lightpink"),
]
headlines = []

for i, (title, color) in enumerate(news_boxes):
    frame = tk.Frame(news_frame, width=580, height=60, bg=color, highlightbackground=frame_border_color, highlightthickness=1)
    frame.grid(row=i, column=0, sticky="nsew")
    frame.grid_propagate(False)
    tk.Label(frame, text=title, font=('Helvetica', 16, 'bold'), bg=color).pack(pady=5)
    headline_label = tk.Label(frame, text="Loading news...", font=('Helvetica', 14), wraplength=654, justify='left', bg=color)
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

# Configure uniform row and column sizes
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
