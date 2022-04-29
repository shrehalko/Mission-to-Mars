# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

# When we were testing our code in Jupyter, headless was set as False so we could see the scraping in action.
# Now that we are deploying our code into a usable web app, we don't need to watch the script work.
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres":hemisphere_images(browser),
        "last_modified": dt.datetime.now()
    }
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #slide_elem

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        #news_title

        news_p = slide_elem.find('div',class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
    
    return news_title,news_p


# ### Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
   
    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# ### Mars Facts
def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


# ### Mars Hemisphere Images
def hemisphere_images(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Find the hemisphere images and store them in a variable 
    full_image_elem = browser.find_by_css('img.thumb')

    # 2. Create a list to hold the dictionaries of images and titles extracted for each hemisphere.
    hemisphere_image_urls = []

    for i in range(len(full_image_elem)):
        # Create an empty dictionary to hold the image url and the title 
        hemispheres = {}
        try:
            #Click the image on the website
            browser.find_by_css('img.thumb')[i].click()
    
            #Parse the html of the browser visited after clicking the image
            html = browser.html
            image_soup = soup(html, 'html.parser')
            #Find the image of the hemisphere on the webpage
            image_soup1 = image_soup.find('div',class_ = "downloads")
            # Retrieve the url of the .jpg image url  
            temp_url = image_soup1.a["href"]
            #Create a full url and store in the dictionary - hemispheres
            hemispheres['img_url'] = 'https://marshemispheres.com/' + temp_url
            #Retrieve the title of the image from the 'h2' tag
            hemispheres['title'] = image_soup.find('div',class_ = "cover").h2.get_text()
    
            #Finally append the dictionary containing the url and the title of the image to the List - hemisphere_image_urls
            hemisphere_image_urls.append(hemispheres)
    
            # Go back to the main page to retrive the information of the other hemisphere image
            browser.back()
        except AttributeError:
            return None
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

