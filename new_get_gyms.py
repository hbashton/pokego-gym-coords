import os, re, requests, sys, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as Actions
from urllib.parse import urlparse
from urllib.parse import parse_qs


def main():

    apikey = ""; # PUT YOUR API KEY HERE. Example: apikey = "A4Fg2sf1edgRw-wQgrq2efwq"

    if apikey == "":
        print("I use the Google API. To make this program work, follow these steps:\nGo to https://console.cloud.google.com\nCreate a project\nEnable the geocode API\nLink a billing account to your project\nCreate an API key\nCopy that key and paste it in the code where it says PUT YOUR API KEY HERE")
        exit()

    i = 450
    count = 0

    if len(sys.argv) != 1:
        extradata = sys.argv[1]
    else:
        extradata = 12

    print("DISCLAIMER: I do not own pokemongomap.info. I use their website to get the coordinates for gyms in a given area.")
    print("Go to ")
    print("For this program to work, you must have urllib, requests, and selenium (with the chrome webdriver installed). You can install all of these with the exception of the webdriver using pip (https://pip.pypa.io). To install the webdriver, please visit https://sites.google.com/a/chromium.org/chromedriver/ and follow the getting started instructions.")

    latitude,longitude = latlong(input("Please enter a location (city, state, address): "), apikey)

    if latitude == "fail" and longitude == "fail":
       print("I couldn't find that location, please try a new location")
       exit()

    while i >= 450:
        try:
            driver = webdriver.Chrome()
            url = "https://www.pokemongomap.info/location/{0}/{1}/{2}".format(latitude.replace('.', ','),longitude.replace('.', ','),extradata)
            driver.get(url)

            # time.sleep(3)
            # driver.find_element_by_xpath('//button[contains(text(), "Close")]').click()

            wait = WebDriverWait(driver, 10)
            actions = Actions(driver)

            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Close")]')))
            element.click()
            time.sleep(1)

            wait = WebDriverWait(driver, 10)
            actions = Actions(driver)

            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@title="Map Settings"]')))
            element.click()
            time.sleep(2)

            wait = WebDriverWait(driver, 10)
            actions = Actions(driver)

            element = driver.find_element_by_xpath('//*[@id="pokecheck"]')
            actions.move_to_element(element).click().perform()
            time.sleep(1)

            wait = WebDriverWait(driver, 10)
            actions = Actions(driver)

            driver.find_element_by_xpath('//button[contains(text(), "Save")]').click()
            time.sleep(20)

            items = driver.find_element_by_xpath('//div[@id="sidebarR"]')
            loclist = driver.find_element_by_xpath('//a[@title="Location List"]')
            i = loclist.find_element_by_xpath('.//i')

            if "left" in i.get_attribute('class'):
                i.click()

            listitems = driver.find_elements_by_css_selector('div[id^="listitem"]')

            i = len(listitems)

            if i >= 450:
                driver.close()
            
            extradata += 1

        except:
            print("Something went wrong! If you got a request error, try loading the program with the argument 11 (keep decreasing the number if you get the same error). If that doesn't solve it, it's something with the code.")
            extradata += 1
            count += 1
            if count == 7:
                exit()

    print(str(i) + " gyms found. Now getting coordinates.")

    gymdict = {}

    for e in listitems:
        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)
        title = e.get_attribute('data-title')

        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)

        element = wait.until(EC.element_to_be_clickable((By.ID, e.get_attribute("id"))))
        element.click()

        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)

        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Info")]')))
        element.click()

        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)

        element = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[contains(text(), "Get Directions")]')))

        link = element.get_attribute('href')

        parsed_link = urlparse(link)
        query = parsed_link[4]
        parsed_query = parse_qs(query)
        coord = parsed_query['destination']

        print(title + " - " + coord[0])

        gymdict[title] = coord[0]

        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)

        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Close")]')))
        element.click()

        wait = WebDriverWait(driver, 10)
        actions = Actions(driver)

        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@id="infoboxclosehit"]')))
        actions.move_to_element(element).click().perform()

    try:
        os.remove('coordinates_list.txt')
    except OSError:
        pass

    string = "";

    for name, coords in gymdict.items():
        string += coords + "," + name + "\n"
        print(name + " - " + coords + "\n")

    print(string, file=open("coordinates_list.txt", "a"))
    print("Successfully saved coordinates to coordinates_list.txt")

def latlong(area, apikey):
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?key=" + apikey + "&address=" + area.replace(" ", "%20"))
    status = response.status_code

    print(status)

    resp_json_payload = response.json()

    if status != 200:
        return "fail", "fail"
    else:
        if resp_json_payload['status'] == "ZERO_RESULTS":
            return "fail", "fail"
        else:
            latitude = resp_json_payload['results'][0]['geometry']['location']['lat']
            longitude = resp_json_payload['results'][0]['geometry']['location']['lng']
            return str(latitude),str(longitude)

if __name__ == '__main__':
    main()