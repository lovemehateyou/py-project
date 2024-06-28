import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pyodbc
import threading

# SQL Server connection settings
server = 'LAPTOP-RRR8Q3CJ'
database = 'news'
username = 'lovemehateyou'
password = 'zerubabel11821996'
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def fetch_news():
    try:
        html_web = requests.get('https://www.animenewsnetwork.com/').text
        soup = BeautifulSoup(html_web, 'lxml')
        sections = soup.find('div', class_='mainfeed-section herald-boxes')
        news = sections.find_all('div', class_='herald box news t-news')

        now = datetime.now()
        current_day = now.day
        articles = []

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            for new in news:
                time = new.find('time').text.strip()
                genre = new.find('span').text.strip().lower()
                if str(current_day) in time and (genre == "live-action" or genre == "anime"):
                    title = new.find('h3').text.strip()
                    description_div = new.find('div', class_='snippet')
                    description = description_div.find('span').text.strip() if description_div else 'No description available'
                    detail_link = new.find('a').get('href')

                    # Check if the title already exists in the table
                    cursor.execute('SELECT COUNT(*) FROM aninews WHERE title = ?', (title,))
                    if cursor.fetchone()[0] == 0:
                        articles.append((title, description, detail_link, genre, time, 'unread'))

            for article in articles:
                cursor.execute('''
                    INSERT INTO aninews (title, descriptions, detail_link, genre, timeing, statues)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', article)
            conn.commit()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except pyodbc.Error as e:
        print(f"Database error: {e}")

def display_news():
    try:
        news_window = tk.Toplevel(app)
        news_window.title("Current News")

        # Create a Canvas widget to hold the news items
        canvas = tk.Canvas(news_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a Scrollbar for vertical scrolling
        scrollbar = ttk.Scrollbar(news_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Canvas to use the Scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the Canvas to hold the news items
        news_frame = ttk.Frame(canvas, padding="10")
        news_frame.pack(fill="both", expand=True)

        # Add the frame to the Canvas
        canvas.create_window((0, 0), window=news_frame, anchor="nw")

        # Bind a function to update scroll region when the canvas is resized
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_configure)

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, descriptions, detail_link, genre, timeing FROM aninews WHERE statues = ?', ('unread',))
            articles = cursor.fetchall()

        for i, article in enumerate(articles):
            title, description, detail_link, genre, time = article
            article_frame = ttk.Frame(news_frame, borderwidth=2, relief="sunken", padding=(5, 5))
            article_frame.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)
            ttk.Label(article_frame, text=f"Title: {title}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Description: {description}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Details: {detail_link}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Genre: {genre}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Date: {time}", wraplength=400).pack(anchor='w')

            # Update article status to 'read' in database
            cursor.execute('UPDATE aninews SET statues = ? WHERE title = ?', ('read', title))
            conn.commit()

    except pyodbc.Error as e:
        print(f"Database error: {e}")



import tkinter as tk
from tkinter import ttk
import pyodbc
import webbrowser

def display_all_news():
    try:
        all_news_window = tk.Toplevel(app)
        all_news_window.title("All News")

        # Create a Canvas widget to hold the news items
        canvas = tk.Canvas(all_news_window)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a Scrollbar for vertical scrolling
        scrollbar = ttk.Scrollbar(all_news_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Canvas to use the Scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the Canvas to hold the news items
        all_frame = ttk.Frame(canvas, padding="10")
        all_frame.pack(fill="both", expand=True)

        # Add the frame to the Canvas
        canvas.create_window((0, 0), window=all_frame, anchor="nw")

        # Bind a function to update scroll region when the canvas is resized
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_configure)

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, descriptions, detail_link, genre, timeing FROM aninews')
            articles = cursor.fetchall()

        def open_link(event):
            webbrowser.open_new(article[2])  # Open detail_link in a web browser when clicked

        for i, article in enumerate(articles):
            title, description, detail_link, genre, time = article
            article_frame = ttk.Frame(all_frame, borderwidth=2, relief="sunken", padding=(5, 5))
            article_frame.pack(fill="x", padx=5, pady=5, ipadx=5, ipady=5)
            title_label = ttk.Label(article_frame, text=f"Title: {title}", wraplength=400, cursor="hand2")
            title_label.pack(anchor='w')
            title_label.bind("<Button-1>", open_link)  # Bind left mouse button click to open_link function
            ttk.Label(article_frame, text=f"Description: {description}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Details: {detail_link}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Genre: {genre}", wraplength=400).pack(anchor='w')
            ttk.Label(article_frame, text=f"Date: {time}", wraplength=400).pack(anchor='w')

    except pyodbc.Error as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Error: {e}")


# GUI setup
app = tk.Tk()
app.title("Anime News Network Scraper")

frame = ttk.Frame(app, padding="10")
frame.grid(row=0, column=0, sticky="nsew")

for i in range(3):
    frame.grid_columnconfigure(i, weight=1)
    frame.grid_rowconfigure(i, weight=1)

ttk.Button(app, text="Current News", command=display_news).grid(row=1, column=0, pady=10)
ttk.Button(app, text="All News", command=display_all_news).grid(row=2, column=0, pady=10)

# Execute fetch_news once on application start
fetch_news()

# Start the GUI main loop
app.mainloop()
