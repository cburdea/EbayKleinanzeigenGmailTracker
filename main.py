from lxml import html
import requests
import time
import smtplib
import random

#Go to the EBAY Kleinanzeigen website and create a search
#Enter the criteria of your search
#Once finished, update the following URL 
MONITORED_EBAY_KLEINANZEIGEN_URL = "https://www.ebay-kleinanzeigen.de/s-preis:100:/katzenbilder/k0"
FREQUENCY = 60 #Seconds 

#GMAIL Specific Parameters
GMAIL_APP_PWD = "" #Enter APP Passwort created in GMAIL account
USER = "" #Enter your EMAIL
RECIPIENT = [""] #Enter recipient email(s)
SUBJECT = "NEW EBAY KLEINANZEIGEN POSTING" #Enter Subject of Email
BODY = "New Posting for the following link: \n" + MONITORED_EBAY_KLEINANZEIGEN_URL #Enter Message of Email

current_id = 0
previous_id = 0

#Searches elements of a scpecific class in HTML DOM and returns a list
def get_elements_by_class_from_url(class_name):

    url = MONITORED_EBAY_KLEINANZEIGEN_URL

    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} 
    response = requests.get(url,headers=header)

    dom = html.fromstring(response.text)
    elements = dom.find_class(class_name)
    return elements

#Checks if the latest ID is new. In that case a email is triggered
def detect_new_id_and_send_email(elements):
    global current_id
    global previous_id
    latest_id = elements[0].get('data-adid')

    #Checks if the latest element is not known yet
    #The latest two IDs are stored to ensure that the new posting is in fact new
    if latest_id != current_id and latest_id != previous_id:
        previous_id = current_id
        current_id = latest_id
        print("> New Posting detected: " + current_id)
        send_email()
        trigger_windows_notification()
    else:
        print("> "+ str(datetime.datetime.now()) +" Idle - current ID: " + current_id)
        
#Send out email with GMAIL API
def send_email():
    FROM = USER
    TO = RECIPIENT if isinstance(RECIPIENT, list) else [RECIPIENT]
    TITLE = SUBJECT
    TEXT = BODY

    #Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), TITLE, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(USER, GMAIL_APP_PWD)
        server.sendmail(FROM, TO, message)
        server.close()
        print('> successfully sent the mail')
    except:
        print ("> failed to send mail, check parameters")

#main function that loops in a specified intervall
def main():    
    while(True):
        elements = get_elements_by_class_from_url(class_name="aditem")    
        detect_new_id_and_send_email(elements)
        #Adding a random range to the requests in case the website detects automated calls 
        time.sleep(random.randrange(FREQUENCY * 0.8, FREQUENCY * 1.2))
        
if __name__ == "__main__":
    main()