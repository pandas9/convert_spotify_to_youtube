from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.parse
import sys
import re

def is_valid_spotify_url(url):
    """Validate if the URL is a Spotify playlist URL."""
    pattern = r'^https://open\.spotify\.com/playlist/[a-zA-Z0-9]{22}$'
    return bool(re.match(pattern, url))

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python convert.py <spotify_playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    
    # Validate URL
    if not is_valid_spotify_url(playlist_url):
        print("Error: Invalid Spotify playlist URL")
        print("URL should be in format: https://open.spotify.com/playlist/PLAYLIST_ID")
        sys.exit(1)

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()

    try:
        # Navigate to the Spotify playlist
        driver.get(playlist_url)

        # Wait until at least one track element is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]'))
        )

        # Scroll to load all tracks
        while True:
            # Get the current list of track elements
            tracks = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]')
            current_count = len(tracks)

            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load

            # Check if new tracks loaded
            tracks = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]')
            new_count = len(tracks)

            # If no new tracks loaded, exit the loop
            if new_count == current_count:
                break

        # Extract track names from the elements
        track_names = [track.text for track in tracks]

        # Search each track on YouTube and collect URLs
        youtube_urls = []
        for track in track_names:
            print(f"Searching for: {track}")
            
            # URL-encode the track name
            encoded_track = urllib.parse.quote(track)
            
            # Construct the YouTube search URL
            search_url = f"https://www.youtube.com/results?search_query={encoded_track}"
            driver.get(search_url)

            # Wait for search results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "video-title"))
            )

            # Get the first video link
            video_links = driver.find_elements(By.ID, "video-title")
            if video_links:
                youtube_url = video_links[0].get_attribute('href')
                youtube_urls.append((track, youtube_url))
            else:
                print(f"No video found for: {track}")

        # Print the results
        print("\nTrack Names and YouTube URLs:")
        for track, url in youtube_urls:
            print(f"{track}: {url}")

    finally:
        # Ensure the browser closes even if an error occurs
        driver.quit()

if __name__ == "__main__":
    main()