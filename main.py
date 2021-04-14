from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from googletrans import Translator
import time
import os
import random

#Set the variables
driver = webdriver.Firefox(executable_path="./geckodriver.exe")
targetLang = ''
lang = ''
wrongAnswers = {}

email = ''
password = ''
translator = Translator()

def welcome():
    print('welcome to Duolenium...')
    driver.get("https://www.duolingo.com")
 
    global email
    global password

    email = input("Enter your email: ")

    if email == 'default':
    	email = 'zlmiwlh@biojuris.com'
    	password = 'awenADH123LA9'
    else:
    	password = input("Enter your password: ")


def login():
    print("logging in...")

    #Click already have account
    driver.find_element_by_xpath('//a[@data-test="have-account"]').click()

    #Find email input field and enter email
    email_field = driver.find_element_by_xpath('//input[@data-test="email-input"]')
    email_field.clear()
    email_field.send_keys(email)

    #Now enter passwaord
    password_field = driver.find_element_by_xpath('//input[@data-test="password-input"]')
    password_field.send_keys(password)

    #Click login button
    driver.find_element_by_xpath('//button[@data-test="register-button"]').click()

    #Waits for page elements to load
    try:
        #Duolingo leage board
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, "_3Gj5_")))
    except Exception as e:
        pass


def detectLanguage():

    #Duolingo title always has language at the end
    global lang 
    lang = driver.title.split()[-1]

    #Print detected language
    print("Language detected is %s" %lang)
    #Need to set the 2 letter target
    set_lang_target(lang)

def set_lang_target(target):
    if target.lower() == 'french':
        global targetLang
        targetLang = 'fr'

def skillOrPractise():
    #Gets user choice to train or practise
    #choice = input("Would you like to train existing skills or practise a new topic? (Train or Learn) ")
    choice = 'train'

    if choice.lower() == "train":
        #Clicks train button
        driver.find_element_by_xpath('//a[@data-test="global-practice"]').click()
        training()
    elif choice.lower() == "learn":
        print("ok")
    else:
        print("choose a valid option.... ")
        skillOrPractise()

def training():
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@data-test="challenge-header"]/span')))
    while True:
        try:
            time.sleep(1)
            questionType = ''

            testEndConditions()

            try:
                #Skip the encouraging messages
                questionType = driver.find_element_by_xpath('//*[@data-test="challenge-header"]/span').text
                questionType = questionType.lower()
                print('Question: ',questionType)
            except:
                print('Motivational message detected.. skipping')
                driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
                continue


            if questionType == "write this in english":
                writeInEnglish()

            elif questionType[:7] == 'write “':
                tok1 = questionType.split('“')
                tok2 = tok1[1].split('”')
                writeBlankInLang(tok2[0])
                
            elif questionType == "write this in " + lang.lower():
                writeInLanguage()
                
            elif questionType == "select the missing word" or questionType == "fill in the blank":
                chooseMissing()

            elif questionType == "mark the correct meaning":
                markCorrectMeaning()

            else:
                #Hit skip button
                driver.find_element_by_xpath('//button[@data-test="player-skip"]').click()
                #Click continue
                driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[3]/div/div/div[2]/button/span').click()
        
        except Exception as e:
            print(e)
            break

def testEndConditions():
    try:
        #Testing for end screen
        driver.find_element_by_xpath('//*[@data-test="player-end-carousel"]')

        #Click continue button if at end screen
        driver.find_element_by_xpath('//button[@data-test="player-next"]').click()

        print('You have reached the end of training')

        time.sleep(0.5)
        #Testing for streak wager screen
        try:    
            questionType = driver.find_element_by_xpath('//*[@data-test="streak-wager-slid"]/span')
            driver.find_element_by_xpath('//button[@data-test="player-next"]').click()

        except:
            print('Not wagering lingots..')

        time.sleep(0.5)
        #Testing for Premium Prompt
        try:    
            questionType = driver.find_element_by_xpath('//*[@data-test="plus-continue"]/span')
            driver.find_element_by_xpath('//button[@data-test="player-next"]').click()

        except:
            print('Not subscribing to premium..')
    except:
        print('continuing training...')


def writeBlankInLang(translateMe):
    #translate the sentence
    translated = translator.translate(translateMe, src='en', dest=targetLang).text

    #Write in the translation
    inField = driver.find_element_by_xpath('//*[@data-test="challenge-text-input"]')
    inField.send_keys(translated)

    #Check it   
    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
    time.sleep(0.1)

    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()

attempts = 0

def chooseMissing():
    #Just guess this one lol
    options = driver.find_elements_by_xpath('//div[@data-test="challenge-judge-text"]')
    r = random.randint(1, len(options))

    inner = options[r-1].get_attribute('innerHTML')
    global wrongAnswers

    if inner in wrongAnswers:
        time.sleep(0.5)

        global attempts
        attempts += 1
        if attempts > len(options):
            wrongAnswers.clear()
        chooseMissing()
    else:
        options[r - 1].click()

        #Check it   
        driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
        time.sleep(0.1)

        try:
            incorrect = driver.find_element_by_xpath('//div[@data-test="blame blame-incorrect"]')
            wrongAnswers[inner] = 'wrong'
        except:
            print('right answer')

        #continue
        driver.find_element_by_xpath('//button[@data-test="player-next"]').click()


def writeInLanguage():
    #Grab hints to form a words
    hints = driver.find_elements_by_xpath('//div[@data-test="hint-token"]')
    words = []

    #Stor hints in word array
    for hint in hints:
        words.append(hint.get_attribute('innerHTML'))
    
    #Reform into a sentence
    sentence = ' '.join(words)

    #translate the sentence
    translated = translator.translate(sentence, src='en', dest=targetLang).text

    #Put translation into text area
    input_field = driver.find_element_by_xpath('//*[@data-test="challenge-translate-input"]')
    input_field.send_keys(translated)

    #Check it
    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
    time.sleep(0.1)

    #continue
    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()

def writeInEnglish():
    #Seperate words by hints since that's how the html is on Duolingos
    hints = driver.find_elements_by_xpath('//*[@data-test="hint-token"]')
    words = []
    
    #Append each hint to a list of words
    for hint in hints:
        words.append(hint.get_attribute('innerHTML'))

    #Reform into a sentence
    sentence = ' '.join(words)

    #translate the sentence
    translated = translator.translate(sentence).text
    
    #Put translation into text area
    input_field = driver.find_element_by_xpath('//*[@data-test="challenge-translate-input"]')
    input_field.send_keys(translated)

    #Check it
    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
    time.sleep(0.1)

    #continue
    driver.find_element_by_xpath('//button[@data-test="player-next"]').click()
    


def markCorrectMeaning():

    #Accuracy increases if we translate the english to the language and then back to english
    english = driver.find_element_by_class_name("_3-JBe").get_attribute("innerHTML")
    english_to_lang = translator.translate(english, src='en', dest=targetLang).text
    back_to_english = translator.translate(english_to_lang).text

    #print in eng
    print('in english: %s' %english)

    #Gets all the choices
    choices = driver.find_elements_by_xpath("//div[@data-test='challenge-judge-text']")

    #Goes through all the choices to check for matches
    for choice in choices:
        sentence = choice.get_attribute('innerHTML')
        translated = translator.translate(sentence).text
        print(sentence, "translated as:", translated)

        #click the correct answer if found
        if translated.lower() == back_to_english.lower():
            print("FOUND : ", translated, "=", english)

            #Click check and continue
            choice.click()
            driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[3]/div/div/div[2]/button/span').click()
            time.sleep(0.1)
            driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div[3]/div/div/div[2]/button/span').click()
            break

        time.sleep(0.1)

# Commands listed here.
if __name__ == "__main__":
    welcome()
    login()
    detectLanguage()
    skillOrPractise()
	#driver.quit()