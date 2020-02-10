#Main library for the Webcrawler Medieval Art

from bs4         import BeautifulSoup
from selenium    import webdriver
from collections import OrderedDict
from urllib      import request
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
from selenium.webdriver.common.by  import By
import time
import parameters
import csv
import re

def browser_open():
    driver = webdriver.Firefox(executable_path=parameters.Firefox_Driver_PATH)
    return driver

def browser_open_url(browser, url) :
    browser.get(url)
    return browser

def get_html_page(browser):
    res = browser.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(res, 'lxml')
    return soup

def medieval_art_login(browser):
    print("Signing in ...")
    browser = browser_open_url(browser, parameters.login_URL)
    wait = WebDriverWait(browser, 10)
    # wait2 = WebDriverWait(browser, 10)
    searchbox = wait.until(EC.presence_of_element_located((By.XPATH,"//*/input[@id='username']")))

    username_box = browser.find_element_by_xpath("//*/input[@id='username']")
    username_box.send_keys(parameters.USERNAME)
    password_box = browser.find_element_by_xpath("//*/input[@id='password']")
    password_box.send_keys(parameters.PASSWORD)

    submit_button = browser.find_element_by_xpath("//*/button[@type='submit']")
    submit_button.click()

    print("Signed in!")
    cookies = browser.get_cookies()
    print("Got cookies from Firefox")

    # Pass on cookies to requests so we keep being logged in
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    return browser

def search_for_keyword(browser):

    browser = medieval_art_login(browser)
    time.sleep(1)
    browser = browser_open_url(browser,parameters.search_URL)
    wait = WebDriverWait(browser, 30)
    # wait2 = WebDriverWait(browser, 10)
    searchbox = wait.until(EC.presence_of_element_located((By.XPATH, "//*/input[@id='topbarSearchForm:SearchExpressionInput']")))

    search_box = browser.find_element_by_xpath("//*/input[@id='topbarSearchForm:SearchExpressionInput']")
    search_box.send_keys(parameters.KEYWORD)
    submit = browser.find_element_by_xpath("//*/a[@id='topbarSearchForm:searchCommand']")
    submit.click()

    time.sleep(2)

    return  browser

def extract_page_links(browser):
    page_links = []
    #item_boxes = soup.find_all('a', {'class': 'list-card'})
    wait = WebDriverWait(browser, 30)
    # wait2 = WebDriverWait(browser, 10)
    boxestowaitfor = wait.until(EC.presence_of_element_located((By.XPATH, "//*/tr[@class='ui-widget-content ui-datatable-even']/td[@class='highlighted']/a")))
    even_item_boxes = browser.find_elements_by_xpath("//*/tr[@class='ui-widget-content ui-datatable-even']/td[@class='highlighted']/a")
    odd_item_boxes  = browser.find_elements_by_xpath("//*/tr[@class='ui-widget-content ui-datatable-odd']/td[@class='highlighted']/a")
    item_boxes = even_item_boxes + odd_item_boxes

    if item_boxes is not None:
        print("Items found in this page. " + str(len(item_boxes)) + " items found.")
        link_counter = 0
        for box in item_boxes:

            try:
                href = box.get_attribute('href')
                if 'http' in href:
                    link = href
                else:
                    link = parameters.base_url + href

                if link is not None:
                    link_counter += 1
                    page_links.append(link)
                    print(str(link_counter) + "- " + link)
            except:
                link = ''

    return page_links

def save_links(browser):
    all_links = []
    page_counter = 0
    f = open(parameters.LINKS_File_PATH, "w+")
    print("Extracting the item links of all pages...")
    NEXT_PAGE_EXISTS = True
    while NEXT_PAGE_EXISTS:
        page_counter += 1
        print("Page number " + str(page_counter))
        page_links = extract_page_links(browser)
        for link in page_links:
            f = open(parameters.LINKS_File_PATH, "a")
            f.write(link + "\n")

        time.sleep(1)
        NEXT_PAGE_EXISTS = go_to_next_page(browser)

def refine_date(raw_date):
    earliest_date = ''
    latest_date = ''
    refined_date = []
    dates_array = re.findall(r"\d+", raw_date)
    try:
        earliest_date = dates_array[0]
    except:
        pass
    try:
        latest_date = dates_array[1]
    except:
        pass
    refined_date.append(earliest_date)
    refined_date.append(latest_date)
    return refined_date

def extract_item_metadatas(browser,link):
    metadata_list = []
    item_metadata = {}
    title = ''
    details_url = link
    file_name = ''
    artist = ''
    date = ' '
    earliest_date = ''
    latest_date = ''
    genre = ''
    material = ''
    subtitle = ''
    current_location = ''
    original_location = ''
    image_url = ''
    image_tag = ""
    repository_number = ''

    wait  = WebDriverWait(browser, 10)
    #wait2 = WebDriverWait(browser, 10)
    table = wait.until(EC.presence_of_element_located((By.XPATH,'//*/div[@id="form1:j_idt70"]')))
    #img   = wait2.until(EC.presence_of_element_located((By.XPATH, '//*/div[@class="image-gallery-image"]')))
    if table is not None :
        print("Metadatas Found!")
        try:
            artist_tag = browser.find_element_by_xpath('//*/div[@id="form1:j_idt160:0:j_idt163"]/a')
            artist = artist_tag.text
        except:
            pass

        #try:
        #    title_tag = browser.find_element_by_xpath('//*/h1[@class="title"]')
        #    title = title_tag.text.replace(',' , ' | ')
        #except:
        #    pass

        try:
            subtitle_box = browser.find_element_by_xpath('//*/div[@id="form1:j_idt173_content"]')
            subtitle = subtitle_box.text.replace('\n', ' ')
        except:
            pass

        try:
            date_box = browser.find_element_by_xpath('//*/div[@id="form1:j_idt138:0:j_idt141"]')
            raw_date = date_box.text.replace('\n', ' ')
            earliest_date = refine_date(raw_date)[0]
            latest_date   = refine_date(raw_date)[-1]
        except:
            pass

        try:
            material_tag = browser.find_element_by_xpath('//*/div[@class="description"]/h2')
            material = material_tag.text.replace(',' , ' | ')
        except:
            pass

        try:
            genre_box = browser.find_element_by_xpath('//*/div[@id="form1:j_idt148:0:j_idt151"]/a')
            genre = genre_box.text.replace('\n', ' ')
        except:
            pass

        try:
            repository_number_box = browser.find_element_by_xpath('//*/div[@id="form1:j_idt87"]')
            repository_number = repository_number_box.text.replace('\n', ' ')
        except:
            pass

        try:
            current_location_tag = browser.find_element_by_xpath('//*/div[@id="form1:j_idt101:0:j_idt104"]/a')
            current_location = current_location_tag.text.replace('\n', ' ')
        except:
            pass

        try:
            original_location_tag = browser.find_element_by_xpath('//*/div[@id="form1:j_idt101:1:j_idt104"]/a')
            original_location = original_location_tag.text.replace('\n', ' ')
        except:
            pass
        wait2 = WebDriverWait(browser, 5)

        imageboxxpath = '//*/div[@class="ui-outputpanel ui-widget image-gallery-item-text ui-g-12"]/a'
        image_boxes_wait = wait2.until(EC.presence_of_all_elements_located((By.XPATH, imageboxxpath)))
        if image_boxes_wait is not None:
            try:
                img_boxes = browser.find_elements_by_xpath(imageboxxpath)
                print('\tNumber of Images for Item: ' + str(len(img_boxes)))
            except:
                pass
        for img_box in img_boxes:
            image_url = img_box.get_attribute('href')
            file_name = "medieval_art" + image_url.split('/')[-1]
            #if not parameters.Images_are_already_downloaded:
                #browser = browser_open_url(browser,image_url)
                #time.sleep(1)
                #download_image(browser,image_url,file_name)

            item_metadata = {
                'Iconography'       : parameters.Iconography,
                'Branch'            : 'ArtHist',
                'Photo Archive'     : parameters.base_url,
                'File Name'         : file_name,
                'Title'             : title,
                'Additional Information'  : subtitle,
                'Artist'            : artist,
                'Earliest Date'     : earliest_date,
                'Latest Date'       : latest_date,
                'Original Location' : original_location,
                'Current Location'  : current_location,
                'Genre'             : genre,
                'Repository Number' : repository_number,
                'Material'          : material,
                'Image Credits'     : image_url,
                'Details URL'       : link
            }

            print('\t\tFile Name:        ' + file_name)
            print('\t\tURL:              ' + image_url)
            #print('Title:            ' + title)
            #print('Earliest Date:    ' + earliest_date)
            #print('Latest Date:      ' + latest_date)
            #print('Repository:       ' + repository_number)
            #print('Artist:           ' + artist)
            #print('Material:         ' + material)
            #print('Current Location: ' + current_location)

                # Fixing the order of dictionary

            keyorder = parameters.Header
            item_metadata = OrderedDict(sorted(item_metadata.items(), key=lambda i: keyorder.index(i[0])))
            print('_________________________________________________________')
            metadata_list.append(item_metadata)

        return metadata_list

def go_to_next_page(browser):

        next_page_button = browser.find_element_by_xpath('//*/a[@class="ui-paginator-next ui-state-default ui-corner-all"]')
        if next_page_button is not None:
            browser.execute_script("arguments[0].click();", next_page_button)
            time.sleep(10)
            return browser
        else:
            return False

def download_image(browser,url,file_name):
#   path = parameters.Images_PATH + file_name
    cookies = browser.get_cookies()
    print("Got cookies from Firefox")
    # Pass on cookies to requests so we keep being logged in
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    session = requests.Session()
    data = session.get(url).content
    file = parameters.Images_PATH + file_name
    with open(file, 'wb') as f:
        f.write(data)
    print("\t\tFile Downloaded successfully.")
    return file
#    resp = request.urlopen(url)
#    image_data = resp.read()
#    f = open(path, 'wb')
#    f.write(image_data)
#    f.close()

def create_csv_file(file_path, Header):
    keyorder = Header
    with open(file_path, "w", encoding="utf-8") as f:
        wr = csv.DictWriter(f, dialect="excel", fieldnames=keyorder)
        wr.writeheader()

def append_metadata_to_CSV(row, Header):
    keyorder = parameters.Header
    with open(parameters.CSV_File_PATH, "a", encoding="utf-8", newline='') as fp:
        wr = csv.DictWriter(fp,dialect="excel",fieldnames=keyorder)
        wr.writerow(row)

def quit_browser(browser):
    browser.quit()
