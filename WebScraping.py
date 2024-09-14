#TODO need to decide how to go about this. It is either going to be beutiful soup or selenium, selinium is better apparently
# I just don't know it but I will get to know it for this task
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime

# Dict of supermarkets and their URLs 
supermarkets = {
    'Tesco': 'https://www.tesco.com/groceries/',
    'Sainsburys': 'https://www.sainsburys.co.uk/gol-ui/groceries',
    'Asda': 'https://groceries.asda.com', #TODO - has a cookies blockage
    'Morrisons': 'https://groceries.morrisons.com/browse'
}

# List of products to scrape (you'll need to define these) we can specify this to be the stuff we suually buy, lets not break the bank
products = ['milk', 'bread', 'eggs', 'bananas']

def setup_driver():
    """Set up and return a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    return webdriver.Chrome(options=options)

#This is a general function which is not at all filled out. 
#When webscraping there are a lot of diffferent hoops that need to be jumped through to be able to get the the correct point like pop-ups
#Also worth nothing that the differernt here as well that differernt companies have differernt naes and sections for differernt items 
def scrape_supermarket(driver, supermarket, url, product):
    """
    Scrape the price of a product from a supermarket's website.
    This function needs to be customized for each supermarket.
    """
    try:
        driver.get(url)
        
        # Wait for the search input to be present (adjust timeout as needed)
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
        )
        
        # Enter the product name and submit the search
        search_input.send_keys(product)
        search_input.send_keys(Keys.RETURN)
        
        # Wait for the search results to load (you might need to adjust the selector and timeout)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-list"))
        )
        
        # Find the first product and its price (you'll need to customize these selectors)
        product_element = driver.find_element(By.CSS_SELECTOR, ".product-item")
        price_element = product_element.find_element(By.CSS_SELECTOR, ".price")
        
        return price_element.text.strip()
    
    except TimeoutException:
        print(f"Timeout while scraping {supermarket} for {product}")
    except NoSuchElementException:
        print(f"Could not find element while scraping {supermarket} for {product}")
    except Exception as e:
        print(f"Error scraping {supermarket} for {product}: {str(e)}")
    
    return None

#the main function will run each product for every url we should jsut be able to flesh out the actual scraping algo
def main():
    driver = setup_driver()
    data = []
    
    try:
        for product in products:
            for supermarket, url in supermarkets.items():
                price = scrape_supermarket(driver, supermarket, url, product)
                data.append({
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'supermarket': supermarket,
                    'product': product,
                    'price': price
                })

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)

        # Clean the price data
        df['price'] = df['price'].replace('£', '', regex=True).astype(float)

        # Perform some basic analysis
        print(df.groupby('supermarket')['price'].mean())
        print(df.groupby('product')['price'].describe())

        # Find the cheapest supermarket for each product
        cheapest = df.loc[df.groupby('product')['price'].idxmin()]
        print(cheapest)

        # Save the results to a CSV file
        df.to_csv('supermarket_prices.csv', index=False)

        # Optionally, you could save to Excel for more complex formatting
        df.to_excel('supermarket_prices.xlsx', index=False)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()