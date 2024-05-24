import logging
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import requests
import statistics
from datetime import datetime, date, timedelta
import calendar
import time

# Set up logging
logging.basicConfig(filename='telegram_bot.log', level=logging.DEBUG)

# Function to handle the /item command
def item(update, context):
    # Extract the search string from the command arguments
    string_search = " ".join(context.args)
    if not string_search:
        update.message.reply_text("Please provide a search string. If it contains spaces, enclose it in double quotes.")
        return
    try:
        # Call the function to scrape item info asynchronously
        scrape_item_info(update, context, string_search)
    except Exception as e:
        # Handle any exceptions here, e.g., send an error message to Telegram
        update.message.reply_text(f"An error occurred: {str(e)}")

# Function to scrape item information asynchronously
def scrape_item_info(update, context, string_search):
    # Start a loading indicator
    loading_message = update.message.reply_text("Processing Results...")

    # Create a logger
    logger = logging.getLogger(__name__)

    service = webdriver.firefox.service.Service(executable_path='/usr/bin/geckodriver')
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    driver = webdriver.Firefox(service=service, options=options)

    search_url = "https://130point.com/sales/"

    searching = string_search.strip('"')
    logger.info(f"\nSearch String: \"{searching}\"")

    try:
        # Navigate to 130point landing sales page
        driver.get(search_url)
        time.sleep(7)

        search_field = driver.find_element_by_id('searchBar')
        search_field.send_keys(searching)
        time.sleep(5)

        # Submit search string on 130Point
        submit_button = driver.find_element_by_xpath('/html/body/div[6]/div[3]/div/div[2]/div/div[2]/div[5]/div[2]/div/div/div/div[10]/div[2]/button')
        submit_button.click()

        # Wait for the search results to load
        time.sleep(15)
        search_results = driver.find_element_by_xpath("/html/body/div[6]/div[3]/div/div[2]/div/div[2]/div[9]/div[2]/div/div/div/div")

        # Extract item info and process it
        item_rows = search_results.find_elements_by_xpath("//tr[starts-with(@id, 'row')]")
        if not item_rows:
            update.message.reply_text("No matching items found.")
            return

        # Process item rows
        for item_row in item_rows:
            # Extract item data here
            pass

        # Once processing is complete, send the results back to the user
        update.message.reply_text("Here is the information you requested.")

    except Exception as e:
        logger.error(f"An error occurred while scraping item information: {str(e)}")
        update.message.reply_text(f"An error occurred while processing the request. Please try again later.")

    finally:
        # Close the browser window
        driver.quit()
        # Remove the loading indicator
        loading_message.delete()

# Define the main function to start the bot
def main():
    # Insert your Telegram Bot token below
    updater = Updater(token='TOKEN', use_context=True)
    dispatcher = updater.dispatcher

    # Register the /item command handler
    item_handler = CommandHandler('item', item)
    dispatcher.add_handler(item_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

# Start the bot when the script is run
if __name__ == '__main__':
    main()
