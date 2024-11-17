import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import threading

# Function to automate scraping
def automate():
    log_message("Starting automation...")
    s = Service("C:/Users/Abdullah/PycharmProjects/Web Scraping/chromedriver-win64/chromedriver.exe")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }
    chrome_options = Options()
    chrome_options.add_argument(f'--user-agent={headers["User-Agent"]}')
    driver = webdriver.Chrome(service=s, options=chrome_options)

    log_message("Navigating to IMDB...")
    driver.get("https://www.imdb.com/")
    time.sleep(3)
    log_message("Clicking the element...")
    element = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div[2]/div[5]/a")
    element.click()
    time.sleep(3)

    log_message("Clicking the login link...")
    element1 = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[1]/a[1]")
    element1.click()

    log_message("Entering username and password...")
    username = driver.find_element(By.XPATH,
                                   "/html/body/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/form/div/div/div/div[1]/input")
    username.send_keys("your_gmail")
    password = driver.find_element(By.XPATH,
                                   "/html/body/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/form/div/div/div/div[2]/input")
    password.send_keys("your_pass")
    username.submit()

    log_message("Performing search...")
    search = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div[2]/label[1]")
    search.click()
    time.sleep(3)
    tvdrama = driver.find_element(By.XPATH,
                                  "/html/body/div[2]/nav/div[2]/aside[1]/div/div[2]/div/div[2]/div[1]/span/label")
    tvdrama.click()
    time.sleep(3)
    driver.find_element(By.XPATH,
                        "/html/body/div[2]/nav/div[2]/aside[1]/div/div[2]/div/div[2]/div[1]/span/div/div/ul/a[2]").click()
    time.sleep(2)
    driver.find_element(By.XPATH,
                        "/html/body/div[2]/main/div/div[3]/section/div/div[2]/div/div[1]/div/div/button[1]").click()
    time.sleep(10)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(10)

    page_source = driver.page_source
    driver.quit()
    log_message("Automation completed.")
    return page_source

# Function to scrape data from the page source
def scrapedata(page):
    log_message("Starting data scraping...")
    names = []
    ratings = []
    views = []
    descriptions = []

    try:
        soup = BeautifulSoup(page, 'html.parser')
        container = soup.find('ul', class_="ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 jmWPOZ detailed-list-view ipc-metadata-list--base")
        if container:
            boxes = container.find_all('li', class_='ipc-metadata-list-summary-item')
            for box in boxes:
                name_tag = box.find('h3', class_='ipc-title__text')
                name = name_tag.text.strip() if name_tag else None
                names.append(name)

                rating_view_tag = box.find('span', class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
                rating_text = view_text = None
                if rating_view_tag:
                    rating_view_text = rating_view_tag.text.strip()
                    if rating_view_text:
                        rating_text = rating_view_text[:3]
                        view_text = rating_view_text[5:-1]
                ratings.append(rating_text)
                views.append(view_text)

                desc_tag = box.find('div', class_='ipc-html-content-inner-div')
                desc = desc_tag.text.strip() if desc_tag else None
                descriptions.append(desc)

    except Exception as e:
        log_message(f"Error: {e}")

    min_len = min(len(names), len(ratings), len(views), len(descriptions))
    names = names[:min_len]
    ratings = ratings[:min_len]
    views = views[:min_len]
    descriptions = descriptions[:min_len]

    df = pd.DataFrame({"Name": names, "Rating": ratings, "Views": views, "Description": descriptions})
    df.to_csv("IMDB_data_real.csv", index=False)
    log_message("Data scraping completed.")
    return df

# Function to run automation in a separate thread
def run_automation():
    def automation_thread():
        global page_source
        page_source = automate()
    threading.Thread(target=automation_thread).start()

# Function to run scraping in a separate thread
def run_scraping():
    def scraping_thread():
        if page_source:
            scrapedata(page=page_source)
        else:
            log_message("Please run automation first.")
    threading.Thread(target=scraping_thread).start()

# Function to log messages to the GUI
def log_message(message):
    log_area.insert(tk.END, message + "\n")
    log_area.yview(tk.END)
    log_area.update_idletasks()

# Main application window
root = tk.Tk()
root.title("IMDB Scraper")
root.geometry("600x400")

# Create frames for layout
frame_top = tk.Frame(root, padx=10, pady=10)
frame_top.pack(side=tk.TOP, fill=tk.X)
frame_bottom = tk.Frame(root, padx=10, pady=10)
frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Add buttons for automation and scraping
btn_automation = tk.Button(frame_top, text="Run Automation", command=run_automation, width=15)
btn_automation.pack(side=tk.LEFT, padx=10)
btn_scraping = tk.Button(frame_top, text="Run Scraping", command=run_scraping, width=15)
btn_scraping.pack(side=tk.LEFT, padx=10)

# Add a scrolled text area for logs
log_area = scrolledtext.ScrolledText(frame_bottom, wrap=tk.WORD, height=15)
log_area.pack(fill=tk.BOTH, expand=True)

root.mainloop()
