import requests
from bs4 import BeautifulSoup
import time
import os

from dotenv import load_dotenv
import anthropic

load_dotenv()
API_KEY = os.getenv('API_KEY')
client = anthropic.Anthropic(api_key=API_KEY,)


def prompt(content: str, history = []):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        messages= history + [
            {"role": "user", "content": content}
        ]
    )
    #print(message.content)
    return message.content[0].text



def scrape_github_profile(username):
    base_url = f"https://github.com/{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    def download_and_parse(url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
            return None

    def extract_text(soup):
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Remove all images and SVGs
        for img in soup.find_all('img'):
            img.decompose()
        for svg in soup.find_all('svg'):
            svg.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text

    # Download and parse profile page
    profile_soup = download_and_parse(base_url)
    if profile_soup:
        #print(f"Successfully downloaded profile page for {username}")
        profile_text = extract_text(profile_soup)
    
    # Download and parse repositories page
    repos_url = f"{base_url}?tab=repositories"
    repos_soup = download_and_parse(repos_url)
    if repos_soup:
        #print(f"Successfully downloaded repositories page for {username}")
        repos_text = extract_text(repos_soup)

    return profile_text, repos_text



def summarize_github_profile(github_username):
    profile_text, repos_text = scrape_github_profile(github_username)

    # use claude to analyze the text and write a short summary
    _prompt = f"Write a short summary of {github_username} github profile.\n\nProfile:\n{profile_text}\n\nRepositories:\n{repos_text}\n\nDO NOT MENTION THE USER'S NAME OR USERNAME OR ANY OTHER PERSONAL INFORMATION."
    profile_summary = prompt(_prompt)

    return profile_summary
    

