import requests
from bs4 import BeautifulSoup
import re
import os  # Import the os module for file operations
from datetime import datetime

# Define Sens Critique URL
SENS_CRITIQUE_URL = 'URL_OF_SENSCRITIQUE_LIST'   ### example : https://www.senscritique.com/liste/arte_tv_series_disponibles/3082138

# Remove existing tv_shows.txt file if it exists
if os.path.exists('tv_shows.txt'):
    os.remove('tv_shows.txt')

# Recreate tv_shows.txt as an empty file
with open('tv_shows.txt', 'w'):
    pass

# Function to extract TV show titles from Sens Critique
def extract_tv_show_titles(sens_critique_url):
    tv_show_titles = []
    page_number = 1

    while True:
        try:
            # Construct the URL for the current page
            url = f"{sens_critique_url}?page={page_number}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find TV show titles on the current page
            titles = soup.find_all('a', class_='sc-e6f263fc-0 sc-a0949da7-1 cTitej eGjRhz sc-4495ecbb-3 hCRsTs')
            if not titles:
                break  # No more pages to scrape

            for title in titles:
                # Remove the year from the title (assuming it is in parentheses at the end)
                title_text = re.sub(r'\(\d{4}\)$', '', title.text.strip())
                tv_show_titles.append(title_text)

            page_number += 1
        except Exception as e:
            print(f"Error occurred while scraping page {page_number}: {e}")
            break

    # Write the extracted TV show titles to the file
    with open('tv_shows.txt', 'w') as file:
        for title in tv_show_titles:
            file.write(title + '\n')

    return tv_show_titles

# Function to read TV show titles from a file
def read_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w'):
            pass
    with open(file_name, 'r') as file:
        return file.readlines()

# Function to extract the list name and description from Sens Critique
def extract_list_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        list_name = soup.title.text.strip()

        # Extract the description
        description_element = soup.find('div', class_='sc-9aba2448-0 elZUSK')
        description_text = description_element.text.strip() if description_element else ''

        return list_name, description_text, url  # Include the source URL
    except Exception as e:
        print(f"Failed to extract the name and description of the list from Sens Critique.")
        print(f"Error: {e}")
        return None, None, None

# Function to find Trakt list ID
def find_trakt_list_id(list_name, headers):
    # Find the Trakt list ID if it exists
    base_url = "https://api.trakt.tv"
    lists_url = f"{base_url}/users/me/lists"
    response_lists = requests.get(lists_url, headers=headers)
    if response_lists.status_code == 200:
        lists_data = response_lists.json()
        for trakt_list in lists_data:
            if trakt_list['name'] == list_name:
                return trakt_list['ids']['trakt']
    return None

# Function to create Trakt list from file
def create_trakt_list_from_file(list_file, sens_critique_url):
    base_url = "https://api.trakt.tv"
    headers = {
        "Content-Type": "application/json",
        "trakt-api-key": "YOUR_TRAKT_API",
        "trakt-api-version": "2",
        "Authorization": f"Bearer YOUR_TRAKT_TOKEN",
    }

    # Remove existing tv_shows.txt file if it exists
    if os.path.exists(list_file):
        os.remove(list_file)

    # Recreate tv_shows.txt as an empty file
    with open(list_file, 'w'):
        pass

    # Read TV show titles from Sens Critique or from the file if already extracted
    tv_show_titles = read_file(list_file)
    if not tv_show_titles:
        tv_show_titles = extract_tv_show_titles(sens_critique_url)

    # Extract the list name, description, and source URL from Sens Critique
    list_name, description, source_url = extract_list_info(sens_critique_url)
    if not list_name:
        print("Failed to extract the name of the list from Sens Critique.")
        return

    # Add source URL and last update time to the Trakt list description
    description += f"\n\nSource URL: {source_url}\n\nThis list was last updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n(using senscritique2trakt script - https://github.com/PierreDurrr/SensCritique2Trakt)"

    # Check if the Trakt list already exists
    existing_list_id = find_trakt_list_id(list_name, headers)
    if existing_list_id:
        print(f"Trakt list '{list_name}' already exists with ID {existing_list_id}. Updating the list.")
        list_id = existing_list_id

        # Update the Trakt list with the source URL and last update time in the description
        update_list_url = f"{base_url}/users/me/lists/{list_id}"
        update_payload = {"description": description}
        response_update = requests.put(update_list_url, headers=headers, json=update_payload)

        if response_update.status_code != 200:
            print(f"Failed to update Trakt list '{list_name}'.")
            print(response_update.text)
            return
    else:
        # Create a new Trakt list with the source URL and last update time in the description
        create_list_url = f"{base_url}/users/me/lists"
        list_payload = {"name": list_name, "description": description, "privacy": "public"}
        response_create = requests.post(create_list_url, headers=headers, json=list_payload)

        if response_create.status_code != 201:
            print(f"Failed to create Trakt list '{list_name}'.")
            print(response_create.text)
            return

        list_id = response_create.json()["ids"]["trakt"]
        print(f"Created Trakt list '{list_name}' with ID {list_id}")

    # Add TV shows to the Trakt list
    add_items_url = f"{base_url}/users/me/lists/{list_id}/items"
    items_payload = {"shows": [{"title": show.strip()} for show in tv_show_titles]}
    response_add_items = requests.post(add_items_url, headers=headers, json=items_payload)

    if response_add_items.status_code == 201:
        print(f"TV shows added to the Trakt list '{list_name}' successfully.")
    else:
        print(f"Failed to add TV shows to the Trakt list '{list_name}'.")
        print(response_add_items.text)

# Example usage
create_trakt_list_from_file('tv_shows.txt', SENS_CRITIQUE_URL)
