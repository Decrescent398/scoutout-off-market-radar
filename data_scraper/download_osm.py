import os
import sched, schedule, time, datetime, threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

DOWNLOAD_PATH = "./data"
GEOFABRIK_DATA_URL = "https://download.geofabrik.de/north-america.html"

def schedule_once_next_day(job_func):
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(86400, 1, job_func)
    # Run the scheduler in a separate thread so it doesn't block the main loop
    threading.Thread(target=scheduler.run, daemon=True).start()

def update_geofabrik():
    # Start the update process
    print("Beginning OSM update")

    try:
        # Attempt to fetch the Geofabrik download page
        geofabrik_response = requests.get(GEOFABRIK_DATA_URL)
        geofabrik_response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        # Handle HTTP errors and retry after 1 day
        print(f"HTTP Error: {http_error}\nResetting scheduled OSM update to tomorrow")
        schedule_once_next_day(update_geofabrik())
    except Exception as error:
        # Handle other exceptions and retry after 1 day
        print(f"Error: {error}\nResetting scheduled OSM update to tomorrow")
        time.sleep(86400)
        schedule_once_next_day(update_geofabrik())
    else:
        if geofabrik_response:
            # Parse the HTML to find download links for .osm.pbf files
            geofabrik_html = geofabrik_response.text
            soup = BeautifulSoup(geofabrik_html, "html.parser")
            geofabrik_download_links = [
                urljoin(GEOFABRIK_DATA_URL, a['href'])
                for a in soup.find_all("a", href=True)
                if a['href'].endswith(".osm.pbf")
            ]    
            # Find the latest US OSM PBF file link
            north_america_latest = next(link for link in geofabrik_download_links if "us-latest.osm.pbf" in link)
            try:
                # Download the latest OSM PBF file
                north_america_latest_download = requests.get(north_america_latest, stream=True)
            except requests.exceptions.HTTPError as http_error:
                # Handle HTTP errors during file download and retry after 1 day
                print(f"HTTP Error while downloading OSM file\nReschedulint OSM download to tomorrow")
                time.sleep(86400)
                update_geofabrik()
            except Exception as error:
                # Handle other exceptions during file download and retry after 1 day
                print(f"Error {error} occured while downloading OSM file\nRescheduling OSM download to tomorrow")
                time.sleep(86400)
                update_geofabrik()
            else:
                # Remove any outdated OSM files in the download directory
                for outdated_osm in os.listdir(DOWNLOAD_PATH):
                    path = os.path.join(DOWNLOAD_PATH, outdated_osm)
                    os.remove(path)
                # Save the new OSM file with today's date in the filename
                with open(f"{DOWNLOAD_PATH}/north-america-latest-{datetime.date.today()}.osm.pbf", "wb") as f:
                    for chunk in north_america_latest_download.iter_content(chunk_size=8192): #8KB for performance
                        f.write(chunk)

def runner():
    # Schedule the update to run every Monday at 1:00 AM
    schedule.every().monday.at("01:00").do(update_geofabrik)

    # Main loop to run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)

runner()