from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib.parse
import sys
import re
import os

def is_valid_spotify_url(url):
    """Validate if the URL is a Spotify playlist URL."""
    pattern = r'^https://open\.spotify\.com/playlist/[a-zA-Z0-9]{22}$'
    return bool(re.match(pattern, url))

def create_safe_filename(playlist_url):
    """Create a safe filename from the Spotify playlist URL."""
    # Extract the playlist ID from the URL
    playlist_id = playlist_url.split('/')[-1]
    # Create the filename
    filename = f"extracted.{playlist_id}.txt"
    # Replace any potentially unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename

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

    safe_filename = create_safe_filename(playlist_url)

    # Initialize the Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Required for some systems
    options.add_argument('--window-size=1920,1080')  # Set window size for better rendering
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to the Spotify playlist
        driver.get(playlist_url)

        # Wait until at least one track element is present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]'))
        )
        
        print("Starting to scroll through playlist...")

        seen_tracks = set()
        tracks_info = []

        # New incremental scrolling logic with dynamic container selection
        playlist_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="playlist-tracklist"]')
        expected_count = int(playlist_container.get_attribute('aria-rowcount')) - 1

        found_last_track = False
        scrolled_through_tracks = []

        while len(tracks_info) <= expected_count:
            time.sleep(3.5)
            tracks = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="tracklist-row"]')
            last_track = tracks[-1]
            
            for container in tracks:
                try:
                    text_element = container.find_element(By.CSS_SELECTOR, '[data-encore-id="text"]')
                    text_content = int(text_element.text)
                    if text_content == expected_count:
                        found_last_track = True
                except:
                    pass
                try:
                    track_link = container.find_element(By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]')
                    track_name = track_link.text
                    # Get all span elements that follow the track_link and take the last one as the artist element
                    following_spans = track_link.find_elements(By.XPATH, './following-sibling::span')
                    artist_element = following_spans[-1]
                    artist_name = artist_element.text
                    if (track_name, artist_name) not in seen_tracks:
                        seen_tracks.add((track_name, artist_name))
                        tracks_info.append((track_name, artist_name))
                except Exception as e:
                    print(f"Error extracting track info: {str(e)}")
                    pass

            if found_last_track:
                break

            scrolled_through_tracks.append(len(tracks_info))
            print(f"Scrolled through {len(tracks_info)} tracks")

            if len(scrolled_through_tracks) >= 3 and len(set(scrolled_through_tracks[-3:])) == 1:
                print("No new tracks found in the last 3 scrolls. Breaking out of the loop.")
                break

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", last_track)
            
        print(f"Finished loading tracks. Total tracks found: {len(tracks_info)}")
        print(f"Found {len(tracks_info)} tracks")

        # Search each track on YouTube and collect URLs
        youtube_urls = []
        for track_name, artist_name in tracks_info:
            # URL-encode the track and artist names
            search_query = f"{track_name} {artist_name}"
            encoded_query = urllib.parse.quote(search_query)
            
            # Construct the YouTube search URL
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            driver.get(search_url)

            # Wait for search results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
            )
            time.sleep(1.5)

            try:
                # Find the first video renderer
                video_renderer = driver.find_element(By.CSS_SELECTOR, "ytd-video-renderer")
                # Get the video link from the renderer's thumbnail element
                video_link = video_renderer.find_element(By.CSS_SELECTOR, "a#thumbnail[href]")
                youtube_url = video_link.get_attribute('href')
                
                if youtube_url:
                    youtube_urls.append((track_name, artist_name, youtube_url))
                    print(f"\nFound video for: {track_name} by {artist_name}: {youtube_url}")
                    # Save each URL as we find it
                    with open(safe_filename, 'a', encoding='utf-8') as f:
                        f.write(f"{track_name} by {artist_name}: {youtube_url}\n")
                else:
                    print(f"No valid URL found for: {track_name} by {artist_name}")
            except Exception as e:
                print(f"Error finding video for {track_name} by {artist_name}: {str(e)}")

        # Print the final results
        print("\nTrack Names and YouTube URLs:")
        for track_name, artist_name, url in youtube_urls:
            print(f"{track_name} by {artist_name}: {url}")
        print(f"\nResults have been saved to {safe_filename}")

    finally:
        # Ensure the browser closes even if an error occurs
        driver.quit()

if __name__ == "__main__":
    main()