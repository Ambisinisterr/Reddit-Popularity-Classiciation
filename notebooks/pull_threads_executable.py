import os
import datetime
import time
import json
import requests
import numpy as np

####################################
##        Global Variables        ##
####################################
#global file_dir


####################################
##           Functions            ##
####################################

def authorize():
    """Used to Authorize Access to the API"""
    global headers

    #Get the various passwords from the hidden password directory file
    with open("./auth/password_directory.ini", "r") as f:
        lines = f.read().splitlines()
    KEYS = {line.split(":")[0]:line.split(":")[1] for line in lines}
    
    #Key Variables Required for Auth Requests
    CLIENT_ID = KEYS["CLIENT_ID"]
    SECRET_KEY = KEYS["SECRET_KEY"]

    #Init Authorization Request
    auth = requests.auth.HTTPBasicAuth(KEYS["CLIENT_ID"], KEYS["SECRET_KEY"])
    headers = {"User-Agent": "MyAPI/0.0.1"}
    
    #Account Settings
    data = {
        "grant_type" : "password",
        "username" : KEYS["USERNAME"],
        "password" : KEYS["PASSWORD"]
    }
    
    #Request Authorization
    res = requests.post("https://www.reddit.com/api/v1/access_token",
                        auth=auth, data=data, headers=headers)
    if not res.ok:
        print(f"**Warning!** Response: {res}")
    else:
        print(f"Response: {res}")
        
    TOKEN = res.json()["access_token"]
    headers["authorization"] = f"bearer {TOKEN}"
    print(headers["authorization"])


def generate_folder_dir():
    """Generates a folder directory string
    Example folder directory format:
    ./data/json/YYYY-MM-DD/"""
    
    folder = str(datetime.datetime.now()).split()[0]
    return f"./data/json/{folder}/"


def generate_file_name():
    """Generates a file name string
    Example file name format:
    YYYY-MM-DD-HH"""
    
    return str(datetime.datetime.now()).split(":")[0].replace(" ", "-")


def pull_threads(number_of_threads):
    """Function to pull a number of threads in json format from r/popular
    Threads must be divisible by 25. If the number entered is not then it will be
    rounded up to the next <brain fart> of 25"""
    
    #Variable Declarations. after and count are used in url generation
    pages = []
    after = ""
    count = 0
    
    #forces number_of_threads to be evenly divisble by 25. Always goes up in value
    if (number_of_threads % 25) != 0:
        number_of_threads = number_of_threads + (25 - (number_of_threads % 25))

    #Make sure the program is authorized to access the API
    authorize()
    print(f"Pulling {number_of_threads} at {datetime.datetime.now()}")
    
    #This basically increases 25 per iteration until reaching the #
    while(count < number_of_threads):
        #Status Update every 500 threads
        if count % 500 == 0:
            print(f"Pulling thread {count}")
            
        #define the url.    
        url = f"https://oauth.reddit.com/r/popular/?count={count}&after={after}"
        try:
            pages.append(requests.get(url, headers=headers).json())
            
        #in the event the request fails the status code should hint of the issue
        except:
            print(f"Failed to Authorize: {requests.get(url, headers=headers).status_code}")
            break
        
        #define the next page url values
        after = pages[-1]["data"]["after"]
        count += pages[-1]["data"]["dist"]
    print(f"Finished pulling {number_of_threads} threads at {datetime.datetime.now()}")
    return pages


def output_data(thread_data):
    """Outputs thread data in json format
    Directory Example:
    ./data/json/{folder}/{file}
    folder = YYYY-MM-DD
    file = YYYY-MM-DD-HH"""
    
    #Decleare the folder and file directory names
    folder_dir = generate_folder_dir()
    file_dir = folder_dir + generate_file_name()
    
    #Create a new folder for the day if one does not exist
    if not os.path.exists(os.path.dirname(folder_dir)):
        try:
            os.mkdir(folder_dir)
        except:
            print("Error: Something went wrong.")


    #Output the thread_data in json format
    with open(file_dir, "w") as outfile:
        json.dump(thread_data, outfile)


def determine_seconds_to_sleep(interval):
    """Determines the seconds until the next hour interval.
    e.g. if the interval is 4 it will determine the seconds until
    4, 8, 12, 16, 20 or 24
    NOTE: Function will not work multple days if 24 is not evenly divisible by the interval"""
    #returns an array of target times (in seconds) based on the interval
    target_times = [x * 3600 for x in range(0,25, interval)]
    
    #current time in seconds
    current_time = (datetime.datetime.now().hour * 3600 +
                    datetime.datetime.now().minute * 60 +
                    datetime.datetime.now().second)
    
    #index for target_time. This is the (current time in min / interval in min) rounded up
    index = int(np.ceil((datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
                        / (interval * 60)))
    
    #if the index is the last value (24:00) then make the target_time is 00:00 tomorrow
    #Add 1 second to either return to account for milliseconds
    if index == len(target_times) - 1:
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        target_time = datetime.datetime.combine(tomorrow, datetime.datetime.min.time())
        return (target_time - datetime.datetime.now()).seconds + 1
    #else return the next interval
    return target_times[index] - current_time + 1


def convert_seconds(seconds):
    """Returns a tuple of (hours, minutes) for use in printing output to the console."""
    str_seconds = str(seconds/3600).split(".")
    hours = int(str_seconds[0])
    minutes = int(float(f".{str_seconds[1]}") * 60)
    return (hours, minutes)


def main():
    #Initial Variable Declarations
    number_of_threads = 2000
    INTERVAL = 4
    already_pulled = False

    #Until Jan 5, 2021
    while(datetime.date.today() < datetime.date(2022,1,8)):
        #Boolean: is current hour a desired interval?
        is_interval = (datetime.datetime.now().hour % INTERVAL) == 0
        
        #Decleare the folder and file directory names
        folder_dir = generate_folder_dir()
        file_dir = folder_dir + generate_file_name()
        #If file already exists, do not pull again
        if os.path.exists(file_dir):
            already_pulled = True
            sleep_seconds = determine_seconds_to_sleep(INTERVAL)
            hours, minutes = convert_seconds(sleep_seconds)
            print("Threads already pulled.")
            print(f"Sleeping for {hours} hours and {minutes} minutes")
            time.sleep(sleep_seconds)
            already_pulled = False

        #If not already pulled or and a pull interval, pull
        elif (not already_pulled) and is_interval:
            threads = pull_threads(number_of_threads)
            output_data(threads)
            already_pulled = True
            time.sleep(120)
            
            #Sleep
            sleep_seconds = determine_seconds_to_sleep(INTERVAL)
            hours, minutes = convert_seconds(sleep_seconds)
            print(f"Sleeping for {hours} hours and {minutes} minutes")
            time.sleep(sleep_seconds)
            #reset already_pulled after sleep
            already_pulled = False
        
        #if not an interval, sleep
        elif not is_interval:
            sleep_seconds = determine_seconds_to_sleep(INTERVAL)
            hours, minutes = convert_seconds(sleep_seconds)
            print(f"Not a time interval of {INTERVAL}")
            print(f"Sleeping for {hours} hours and {minutes} minutes")
            time.sleep(sleep_seconds)
            
        else:
            sleep_seconds = determine_seconds_to_sleep(INTERVAL)
            print(f"This shouldn't happen. Debug")
            time.sleep(sleep_seconds)



####################################
##              Main              ##
####################################

if __name__ == "__main__":
    main()

