import platform

os_name = platform.system()
if os_name != "Windows":
    print(f"This program only works on Windows.")
    quit()

import os
from datetime import datetime, timedelta
from time import sleep
from selenium import webdriver
from dateutil.tz import gettz
from recognizer import get_code
from alert import alert
from warnings import filterwarnings

filterwarnings("ignore")

def save_screen():
    try:
        os.remove(SS_PATH)
    except:
        pass
    my_find_element('//*[@id="screenshareVideo"]').screenshot(SS_PATH)


def yes_no_command(prompt=None):
    print(prompt)
    while True:
        command = input("User: ").lower()
        if command == "y" or command == "n":
            return command
        print("Please send a valid command! (y / n)")


def my_find_element(xpath):
    while True:
        try:
            return driver.find_element("xpath", xpath)
        except:
            continue


class Lecture:
    def __init__(self, start, end):
        self.start = start + semester_start + timedelta(weeks=num_weeks_passed)
        self.end = end + semester_start + timedelta(weeks=num_weeks_passed)

    def __str__(self):
        return f"class {self.start.strftime('%H %M')} -{self.end.strftime('%H %M')}"


def create_lectures():
    return (
        Lecture(
            timedelta(days=0, hours=12, minutes=40),
            timedelta(days=0, hours=14, minutes=20),
        ),
        Lecture(
            timedelta(days=3, hours=11, minutes=40),
            timedelta(days=3, hours=12, minutes=20),
        ),
    )


def find_next_lecture() -> Lecture:
    global num_weeks_passed
    lectures = create_lectures()
    minutes = [
        (lecture.end + timedelta(minutes=10) - now).total_seconds() / 60
        for lecture in lectures
    ]
    minimum = float("inf")
    index_minimum = -1
    for i, value in enumerate(minutes):
        if value > 0 and value < minimum:
            minimum = value
            index_minimum = i
    if index_minimum == -1:
        num_weeks_passed += 1
        return find_next_lecture()
    next_lecture = lectures[index_minimum]
    if now < next_lecture.start - timedelta(minutes=10):
        next_lecture_start = (next_lecture.start - timedelta(minutes=10)).strftime(
            "%d/%m/%Y %H:%M"
        )
        command = yes_no_command(
            f"The next lecture is at {next_lecture_start}. Do you want to wait? (y / n): "
        )
        if command == "y":
            print(f"The program will continue running at {next_lecture_start}.")
            sleep((next_lecture.start - timedelta(minutes=10) - now).total_seconds())
        elif command == "n":
            print("Exiting the program.")
            quit()

    return next_lecture


with open("user_credentials.txt", "r") as file:
    username, password = file.read().split()

SS_PATH = "ss.png"
tzinfo = gettz("Turkey")
semester_start = datetime(2021, 10, 18, tzinfo=tzinfo)
now = datetime.now(tzinfo)
num_weeks_passed = (now - semester_start).days // 7
current_lecture = find_next_lecture()

options = webdriver.ChromeOptions()
options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_setting_values.media_stream_mic": 2,
    },
)
options.add_argument("--window-size=1920,1080")
with webdriver.Chrome(options=options) as driver:
    driver.get("https://odtuclass2021f.metu.edu.tr/course/view.php?id=486")
    my_find_element('//*[@id="username"]').send_keys(username)
    my_find_element('//*[@id="password"]').send_keys(password)
    my_find_element('//*[@id="loginbtn"]').click()
    for i in 1, 2:
        lecture_link = my_find_element(
            f"/html/body/div[1]/div[2]/div/div[1]/section/div/div/ul/li[{num_weeks_passed+2}]/div[3]/ul/li[{i}]/div/div/div[2]/div/a/span"
        )
        if str(current_lecture) in lecture_link.text:
            break
    else:
        print("Lecture link could not be found!")
        quit()
    lecture_link.click()
    my_find_element('//*[@id="join_button_input"]').click()
    driver.switch_to.window(driver.window_handles[1])
    my_find_element(
        "/html/body/div[2]/div/div/div[1]/div/div/span/button[2]/span[1]"
    ).click()

    while True:
        sleep(10)
        save_screen()
        code = get_code(SS_PATH)
        if code:
            print(code)
            alert()
            quit()
            # TODO send the code
