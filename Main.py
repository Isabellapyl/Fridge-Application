# Import necessary things for the program to be able to run
import tkinter as tk  # Import tkinter for GUI creation
from tkinter import messagebox, ttk  # Import messagebox and ttk widgets from tkinter for alerts and combobox
from PIL import Image, ImageTk  # Import Image and ImageTk from the PIL library for handling images
import requests  # Import requests to make API requests
import matplotlib.pyplot as plt  # Import pyplot from matplotlib to create graphs (for the weather grpah)
import random  # Import random for random shuffling and selections

# Constants to store API keys for weather and news services
WEATHER_API_KEY = 'WEATHER.API.KEY'  # API key for weather service
NEWS_API_KEY = 'NEWS.API.KEY'  # API key for news service

# Initialize the main Tkinter application
root = tk.Tk()  # Create the main window using Tk()
root.title("Fridge Application")  # Set the title for the window
root.geometry("1200x900")  # Set the window dimensions
root.resizable(False, False)  # Disable resizing for both width and height to make the application more realistic for a fridge

#style the window
bg_color = "#f0f0f0"  # Set the background color
btn_color = "#4CAF50"  # Set button color
btn_hover = "#45a049"  # Set button hover color
frame_border_color = "#bdbdbd"  # Set border color for frames
entry_color = "#ffffff"  # Set color for entry widgets
font_main = ("Helvetica", 14)  # Define the font for the main elements

root.configure(bg=bg_color)  # Set background color for the root window

# Define hover effect for buttons
def on_enter(e):
    e.widget['background'] = btn_hover  # Change button color when mouse "enters"

def on_leave(e):
    e.widget['background'] = btn_color  # return button to normal color when mouse leaves

# Set a global variable to keep track of whether we're using Celsius or Fahrenheit.
is_celsius = True  #A true/false variable to check if the temperature is in Celsius.

# Function to get geolocation data (latitude, longitude, city)
def get_geolocation():
    try:
        response = requests.get('http://ip-api.com/json')  # Make an API request to get geolocation data
        data = response.json()  # Convert the response to JSON format.
        if data.get('status') == 'success':  # IF the request was successful
            return data['lat'], data['lon'], data['city']  # Return latitude, longitude, and city name
    except requests.RequestException:  # Handle any request exceptions
        return None, None, None  # If the request fails, return None values
    return None, None, None  # Return None if data fetch fails

# Fetch geolocation and store the values
lat, lon, city = get_geolocation()  # Store latitude, longitude, and city name

# Function to get current weather for a specific city
def get_current_weather(api_key, city):
    if not city:  # If no city is provided, return None
        return None, None
    try:
        # Make an API request to OpenWeatherMap to get weather data
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:  # If request was successful
            data = response.json()  # Parse JSON response
            return data['main']['temp'], data['weather'][0]['description']  # Return temperature and description
    except requests.RequestException:  # Handle request exceptions
        return None, None
    return None, None  # Return None values if data fetch fails

# Function to toggle temperature unit between Celsius and Fahrenheit
def toggle_temperature_unit():
    global is_celsius, current_temp, current_desc  # Use global variables
    is_celsius = not is_celsius  # Toggle between Celsius and Fahrenheit

    # Convert temperature and update the button text accordingly
    if current_temp is not None:
        if is_celsius:
            temp = current_temp  # If Celsius, use the current temperature
            unit = "°C"  # Set unit as Celsius
            toggle_btn.config(text="Switch to °F")  # Update button text
        else:
            temp = (current_temp * 9 / 5) + 32  # Convert Celsius to Fahrenheit
            unit = "°F"  # Set unit as Fahrenheit
            toggle_btn.config(text="Switch to °C")  # Update button text

        # Update weather information displayed in the frame
        weather_info = f"Current weather for {city}: {temp:.1f}{unit}, {current_desc}"
        for widget in weather_frame.winfo_children():  # Loop through widgets in the weather frame
            if isinstance(widget, tk.Label):  # Only destroy labels (old info)
                widget.destroy()
        # Create new labels to display updated weather info
        tk.Label(weather_frame, text=weather_info, font=('Helvetica', 17, 'bold'), bg="#e6f7ff", wraplength=250,
                 justify="left").pack(pady=10)
        emoji = weather_emojis.get(current_desc, "")  # Get emoji for current weather description
        tk.Label(weather_frame, text=emoji, font=('Helvetica', 20), bg="#e6f7ff").pack(pady=10)  # Display emoji

# Function to display current weather information in the GUI
def display_weather(city, temp, description):
    if city and temp is not None and description:  # Check if weather data is available
        weather_info = f"Current weather for {city}: {temp}°C, {description}"
    else:
        weather_info = "Weather data unavailable"  # Default message if data is unavailable

    # Create labels to display weather information in the weather frame
    tk.Label(weather_frame, text=weather_info, font=('Helvetica', 17, 'bold'), bg="#e6f7ff", wraplength=250,
             justify="left").pack(pady=10)
    emoji = weather_emojis.get(description, "")  # Get corresponding emoji for the description
    tk.Label(weather_frame, text=emoji, font=('Helvetica', 20), bg="#e6f7ff").pack(pady=10)  # Display the emoji

# Dictionary that maps weather descriptions to corresponding emojis
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

# Function to get predicted weather data for a given location
def get_predicted_weather(api_key, lat, lon):
    try:
        # Make an API request to OpenWeatherMap for the 5-day forecast
        url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        response = requests.get(url)
        if response.status_code == 200:  # If request was successful
            data = response.json()  # Parse JSON response
            return [entry['main']['temp'] for entry in data['list'][:5]]  # Return the temperature forecast for the next 5 entries
    except requests.RequestException:  # Handle request exceptions
        return [14, 15, 13, 12, 11]  # Return a default list if request fails
    return [14, 15, 13, 12, 11]  # Return default values if something goes wrong

# Function to plot and display the predicted weather for the next 5 days
def display_predicted_weather():
    if lat and lon:  # Ensure latitude and longitude are available
        predicted_temps = get_predicted_weather(WEATHER_API_KEY, lat, lon)  # Get predicted temperatures
        days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5']  # Define labels for days
        plt.figure(figsize=(5, 3))  # Create figure for the plot
        plt.plot(days, predicted_temps, marker='o', linestyle='-', label='Predicted Temps', color="blue")  # Plot temperatures
        plt.title(f'5-Day Weather Forecast for {city}')  # Set title for the plot
        plt.xlabel('Days')  # Set label for x-axis
        plt.ylabel('Temperature (°C)')  # Set label for y-axis
        plt.legend()  # Show legend for the plot
        plt.tight_layout()  # Use tight layout for proper formatting
        plt.savefig("weather_forecast.png")  # Save the plot as an image
        forecast_img = Image.open("weather_forecast.png").resize((400, 250))  # Open and resize image
        forecast_img = ImageTk.PhotoImage(forecast_img)  # Convert image for tkinter use
        tk.Label(forecast_frame, image=forecast_img, bg="#e6f7ff").pack(pady=10)  # Create label to display image
        forecast_frame.image = forecast_img  # Store reference to avoid garbage collection

# Create the weather section UI elements
weather_frame = tk.Frame(root, width=400, height=350, bg="#e6f7ff", highlightbackground=frame_border_color,
                         highlightthickness=1)  # Create a frame to display current weather information
weather_frame.grid(row=0, column=0, sticky="nsew")  # Set grid position for the frame
weather_frame.grid_propagate(False)  # Prevent frame from resizing

# Add toggle button to switch between Celsius and Fahrenheit
toggle_btn = tk.Button(weather_frame, text="Switch to °F", command=toggle_temperature_unit, font=('Helvetica', 12),
                       bg=btn_color, fg="white", relief="raised")  # Create button for toggling temperature unit
toggle_btn.pack(pady=10)  # Add padding and pack into weather frame
toggle_btn.bind("<Enter>", on_enter)  # Bind hover effect to button (enter)
toggle_btn.bind("<Leave>", on_leave)  # Bind hover effect to button (leave)

# Forecast section for weather predictions
forecast_frame = tk.Frame(root, width=400, height=350, bg="#e6f7ff", highlightbackground=frame_border_color,
                          highlightthickness=1)  # Create a frame for weather forecast
forecast_frame.grid(row=0, column=1, sticky="nsew")  # Set grid position for the frame
forecast_frame.grid_propagate(False)  # Prevent frame from resizing

# Get the current weather data and display it
current_temp, current_desc = get_current_weather(WEATHER_API_KEY, city)  # Get current weather temperature and description
display_weather(city, current_temp, current_desc)  # Display the fetched weather data
display_predicted_weather()  # Display predicted weather data for 5 days

# Puzzle Corner Section (Bottom Left)
puzzle_frame = tk.Frame(root, bg="#d6d6d6", highlightbackground=frame_border_color, highlightthickness=1)  # Create frame for puzzle corner
puzzle_frame.grid(row=1, column=0, sticky="nsew")  # Set grid position for the puzzle frame
puzzle_frame.grid_propagate(False)  # Prevent the frame from resizing
tk.Label(puzzle_frame, text="Puzzle Corner", font=('Helvetica', 16), bg="#d6d6d6").pack(pady=5)  # Add label for Puzzle Corner title

# Sudoku Functions
difficulty = 'Medium'  # Set default difficulty level for Sudoku

# Function to create a new Sudoku board
def create_sudoku_board():
    base, side = 3, 9  # Base block size and side size of the Sudoku board
    pattern = lambda r, c: (base * (r % base) + r // base + c) % side  # Pattern to determine the Sudoku arrangement
    shuffle = lambda s: random.sample(s, len(s))  # Function to shuffle elements
    r_base, cols = range(base), shuffle(range(side))  # Generate random row base and columns
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]  # Create rows by shuffling
    nums = shuffle(range(1, side + 1))  # Shuffle numbers to be used in the Sudoku board
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]  # Generate the Sudoku board using the pattern

    # Set the number of cells to clear based on the difficulty level
    if difficulty == 'Easy':
        num_to_clear = side * side * 1 // 4  # Easy level clears fewer cells
    elif difficulty == 'Medium':
        num_to_clear = side * side * 3 // 4  # Medium level clears more cells
    elif difficulty == 'Hard':
        num_to_clear = side * side * 7 // 8  # Hard level clears the most cells
    else:
        num_to_clear = side * side * 3 // 4  # Default is medium

    for p in random.sample(range(side * side), num_to_clear):  # Randomly clear cells in the board
        board[p // side][p % side] = 0  # Set cells to zero (empty)
    return board

# Function to solve the Sudoku board using backtracking
def solve_sudoku(board):
    if not (empty := find_empty(board)):  # Find an empty cell
        return True  # If no empty cell, the board is solved
    row, col = empty
    for num in range(1, 10):  # Try numbers from 1 to 9
        if is_valid_move(board, row, col, num):  # Check if the move is valid
            board[row][col] = num  # Place the number on the board
            if solve_sudoku(board):  # Recursively try to solve the board
                return True
            board[row][col] = 0  # Backtrack if solution is not found
    return False

# Function to find an empty cell in the Sudoku board
def find_empty(board):
    return next(((i, j) for i in range(9) for j in range(9) if board[i][j] == 0), None)  # Return the first empty cell found

# Function to check if placing a number is a valid move
def is_valid_move(board, row, col, num):
    return (all(num != board[row][i] for i in range(9)) and  # Check if the number is not in the row
            all(num != board[i][col] for i in range(9)) and  # Check if the number is not in the column
            all(num != board[row // 3 * 3 + i][col // 3 * 3 + j] for i in range(3) for j in range(3)))  # Check if the number is not in the 3x3 block

# Initialize Sudoku boards
initial_board = create_sudoku_board()  # Create a new board
solution_board = [row[:] for row in initial_board]  # Create a copy of the initial board for solution
solve_sudoku(solution_board)  # Solve the board to get the solution
user_answers = {}  # Dictionary to store user answers

# Function to validate the input for Sudoku entries
def validate_input(new_value):
    if new_value == "" or (new_value.isdigit() and 1 <= int(new_value) <= 9):  # Allow empty input or digits between 1 and 9
        return True
    return False

# Register the validation function for input entries
validate_cmd = root.register(validate_input)  # Register the input validation function

# Create the Sudoku grid with validation for each entry
entries = []  # List to hold all entry widgets
grid_frame = tk.Frame(puzzle_frame, bg='lightgray')  # Create a frame for the Sudoku grid
grid_frame.pack(pady=5)  # Pack with some padding

for i in range(9):  # Loop through rows
    row_entries = []  # List to hold entry widgets for each row
    for j in range(9):  # Loop through columns
        entry = tk.Entry(
            grid_frame, width=2, font=('Helvetica', 18), justify='center',
            validate="key", validatecommand=(validate_cmd, "%P")  # Add validation
        )
        entry.grid(row=i, column=j, padx=2, pady=2)  # Set grid position with padding
        entry.bind("<KeyRelease>", lambda e, x=i, y=j: store_user_answer(x, y))  # Bind key release to store answers
        row_entries.append(entry)  # Add entry to the row entries list
    entries.append(row_entries)  # Add the row entries list to the entries list

# Function to populate the Sudoku grid
def populate_grid():
    for i in range(9):  # Loop through rows
        for j in range(9):  # Loop through columns
            entries[i][j].config(state='normal')  # Enable the entry widget
            entries[i][j].delete(0, tk.END)  # Clear any previous value
            if initial_board[i][j] != 0:  # If the cell is part of the puzzle
                entries[i][j].insert(0, str(initial_board[i][j]))  # Insert the number
                entries[i][j].config(state='disabled')  # Disable the entry to prevent editing
            elif (i, j) in user_answers:  # If the user has previously entered an answer
                entries[i][j].insert(0, user_answers[(i, j)])  # Insert the answer

# Function to store user's answers
def store_user_answer(i, j):
    value = entries[i][j].get()  # Get the value entered by the user
    if value.isdigit() and 1 <= int(value) <= 9:  # If value is valid
        user_answers[(i, j)] = value  # Store the value
    elif not value:  # If value is empty
        user_answers.pop((i, j), None)  # Remove the answer from the dictionary

populate_grid()  # Populate the Sudoku grid with the initial board

# Function to verify the user's answers
def verify_answers():
    for i in range(9):  # Loop through rows
        for j in range(9):  # Loop through columns
            user_input = entries[i][j].get()  # Get the user's input
            if not user_input.isdigit() or int(user_input) != solution_board[i][j]:  # If the input is incorrect
                messagebox.showerror("Incorrect", "Your solution is incorrect. Please try again.")  # Show error message
                return
    messagebox.showinfo("Correct", "Congratulations! Your solution is correct.")  # Show success message if all answers are correct

# Add a button to verify the user's Sudoku answers
tk.Button(puzzle_frame, text="Verify Answer", command=verify_answers, font=('Helvetica', 12)).pack(pady=5)  # Create a verify button

# Function to generate a new Sudoku game
def new_game():
    global initial_board, solution_board, user_answers  # Use global variables
    initial_board = create_sudoku_board()  # Generate a new board
    solution_board = [row[:] for row in initial_board]  # Solve the board for answers
    solve_sudoku(solution_board)

    user_answers.clear()  # Clear user answers
    populate_grid()  # Populate the grid with new puzzle
    root.after(600000, new_game)  # Schedule the next game to start after 10 minutes

# Function to set the difficulty level for Sudoku
def set_difficulty(event):
    global difficulty  # Use global difficulty
    difficulty = difficulty_var.get()  # Set difficulty from the dropdown
    new_game()  # Start a new game with the new difficulty

# Dropdown menu to select Sudoku difficulty level
difficulty_var = tk.StringVar(value='Medium')  # Set the default difficulty
difficulty_menu = ttk.Combobox(puzzle_frame, textvariable=difficulty_var, values=['Easy', 'Medium', 'Hard'], state="readonly")  # Create dropdown
difficulty_menu.bind("<<ComboboxSelected>>", set_difficulty)  # Bind event to set difficulty
difficulty_menu.pack(pady=5)  # Pack with some padding

new_game()  # Start the first automatic new game

# News Section (Bottom Right)
news_frame = tk.Frame(root, width=400, height=350, bg=bg_color, highlightbackground=frame_border_color, highlightthickness=1)  # Create frame for news
news_frame.grid(row=1, column=1, sticky="nsew")  # Set grid position for the news frame
news_frame.grid_propagate(False)  # Prevent the frame from resizing

news_boxes = [("Technology News", "lightyellow"), ("Sports News", "lightgreen"), ("Health News", "lightpink")]  # Define news categories and colors
headlines = []  # List to store headline labels

for i, (title, color) in enumerate(news_boxes):  # Loop through news categories
    frame = tk.Frame(news_frame, width=580, height=60, bg=color, highlightbackground=frame_border_color, highlightthickness=1)  # Create frame for each category
    frame.grid(row=i, column=0, sticky="nsew")  # Set grid position
    frame.grid_propagate(False)  # Prevent frame from resizing
    tk.Label(frame, text=title, font=('Helvetica', 16, 'bold'), bg=color).pack(pady=5)  # Create label for news title
    headline_label = tk.Label(frame, text="Loading news...", font=('Helvetica', 14), wraplength=654, justify='left', bg=color)  # Create label for headlines
    headline_label.pack(pady=5)  # Pack the label
    headlines.append(headline_label)  # Append to headlines list

headline1, headline2, headline3 = headlines  # Assign labels for each category

# Function to fetch news for a given category
def fetch_news(category):
    try:
        url = f'https://newsapi.org/v2/top-headlines?category={category}&apiKey={NEWS_API_KEY}'  # Create API URL
        response = requests.get(url)  # Make request to news API
        if response.status_code == 200:  # Check for successful response
            news_data = response.json()  # Parse JSON response
            return news_data['articles'][:1]  # Return the top article
    except requests.RequestException:  # Handle exceptions
        return []  # Return empty list if request fails
    return []  # Default return value

# Function to display news headlines
def display_news():
    for category, label in zip(['technology', 'sports', 'health'], [headline1, headline2, headline3]):  # Loop through categories
        articles = fetch_news(category)  # Fetch news articles
        label.config(text=articles[0]['title'] if articles else f"No {category} news available.")  # Update label text with article title

display_news()  # Fetch and display news

# Configure uniform row and column sizes for layout
root.grid_rowconfigure(0, weight=1)  # Configure first row
root.grid_rowconfigure(1, weight=1)  # Configure second row
root.grid_columnconfigure(0, weight=1)  # Configure first column
root.grid_columnconfigure(1, weight=1)  # Configure second column

root.mainloop()  # Start the Tkinter main event loop
