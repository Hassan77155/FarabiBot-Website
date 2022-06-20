import os
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_bootstrap import Bootstrap
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from time import sleep

# ---------------MYU----------------------#
myu_URL = "http://193.227.50.64/"
# -----------------------------------------#

# ---------------Chrom driver--------------#
# The chrome driver path
# This path depends on where is your chromedriver
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('window-size=1920x1080')
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_driver_bath = "./chromedriver.exe"
chrome_driver_bath = os.environ.get("CHROMEDRIVER_PATH")

# -----------------------------------------#

# ---------------Flask app-----------------#
# Create a flask app
app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = os.environ.get("FARABI_SECRET_KEY")
# -----------------------------------------#


# --------------Flask Form------------------#
class User(FlaskForm):
    id = IntegerField(label="ID", validators=[DataRequired()], render_kw={"placeholder": "Put your Id here"})
    password = PasswordField(label="Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    rate = IntegerField(
        label="Rate",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"placeholder": "The rate you want"},
    )
    submit = SubmitField(label="Start")


# -----------------------------------------#
@app.route("/", methods=["POST", "GET"])
def home():
    # Create a form
    login_form = User()
    # If the user sumbits the data
    if login_form.validate_on_submit():
        id = request.form.get("id")
        password = request.form.get("password")
        rate = request.form.get("rate")
        main(id, password,rate)
        return "<p>Done</p>"
    return render_template("index.html", form=login_form)


# Log in
def login(user_id, user_password):
    """Open the browser and login to your MYU account"""
    # Open MYU tab
    driver.get(myu_URL)
    sleep(2)
    # Enter Username
    username_input = driver.find_element(by=By.NAME, value="txtUserName")
    username_input.send_keys(user_id)
    # Enter Password
    password_input = driver.find_element(by=By.NAME, value="txtPassword")
    password_input.send_keys(user_password)
    sleep(2)
    # Prees Enter To login
    password_input.send_keys(Keys.ENTER)
    print("Login in done")
    # Wait for the page to load
    sleep(5)


def go_to_farabi():
    """Go to farabi Page, This function needs you to be already logedin MYU"""
    # Press farabi
    print("Farabi start")
    estbian_btn = driver.find_element(by=By.XPATH, value='//*[@id="land-page"]/div/ul/li[10]')
    estbian_btn.click()
    sleep(2)
    print("Farabi loaded")


def do_first_subject(rate):
    """Select the first subject and complete its requirements"""
    # Switch to the second tab
    driver.switch_to.window(driver.window_handles[1])
    # Press on the subjects
    latest_estbian = driver.find_element(by=By.XPATH, value='//*[@id="appMenu"]/li[2]/a/span')
    latest_estbian.click()
    sleep(3)
    # Click on the first Subject
    first_subject = driver.find_element(by=By.XPATH, value='//*[@id="appMenu"]/li[2]/ol/li[1]/a/span')
    first_subject.click()
    sleep(5)
    # Press on all checkboxes
    check_boxes = driver.find_elements(by=By.CSS_SELECTOR, value="input[type='checkbox']")
    for box in check_boxes:
        try:
            box.click()
        except ElementNotInteractableException:
            continue
    sleep(3)
    # Get the value the user chose to check
    value = str(rate)
    # Get all the radio buttons
    radio_btns = driver.find_elements(by=By.CSS_SELECTOR, value=f"input[value='{value}']")
    # Click on the radio buttons
    for btn in radio_btns:
        try:
            btn.click()
        except ElementNotInteractableException:
            continue
    # Type the opinion the user chose to write
    type_opinions()
    sleep(2)
    # Press sumbit to save changes
    driver.find_element(by=By.XPATH, value='//*[@id="qzQ"]/div[2]/div/button').click()


def type_opinions():
    """Type 'No thing' on the three questions in the end of the page"""
    # Select the inputs
    inputs = driver.find_elements(by=By.CSS_SELECTOR, value="input[type='text']")
    # Type 'No thing' in every input
    for inp in inputs:
        try:
            inp.send_keys("No thing")
        except NoSuchElementException:
            continue


def main(user_id, user_password, rate):
    """The main function where all the magic happens"""
    # Create a webdirver
    global driver
    # driver = webdriver.Chrome(executable_path=chrome_driver_bath)
    driver = webdriver.Chrome(executable_path=chrome_driver_bath,chrome_options=chrome_options)
    # Keep asking the user for input untill they cooperates
    # while True:
    #     try:
    #         # Get a number from user between 1 and 5
    #         rate = int(input("Enter the rate you want to press for every thing: "))
    #     except:
    #         # In case the user doesn't give a valid int
    #         print("Please enter an int between 1 and 5:")
    #         rate = int(input("Enter the rate you want to press for every thing: "))
    #     # Only break when we have a valid int
    #     if rate > 0 or rate <= 5:
    #         break

    # Login to MYU
    login(user_id, user_password)
    # Go to farabi
    go_to_farabi()
    # This assumes we have 6 subjects
    for i in range(6):
        do_first_subject(rate)
        # Refresh the page
        driver.refresh()


if __name__ == "__main__":
    # Start the application
    app.run(debug=True)
