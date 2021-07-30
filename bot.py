import sqlite3
import selenium
import schedule
import re
import time
import os.path
from os import path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import discord_webhook
import pyautogui

opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
opt.add_argument("--disable-default-apps")
#opt.binary_location = "C:\Program Files\Google\Chrome Beta\Application"
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
	"profile.default_content_setting_values.media_stream_mic": 1,
	"profile.default_content_setting_values.media_stream_camera": 1,
	"profile.default_content_setting_values.geolocation": 1,
	"profile.default_content_setting_values.notifications": 1,
	"protocol_handler": {"excluded_schemes": {"Open Cisco Webex Meeting?": "false"}}
  })

driver = None

TEAMS_CREDS = {'email' : ,'passwd':}

WEBEX_CREDS = {'email' : ,'name':}

timelost = 1




def createDB():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	# Create table
	c.execute('''CREATE TABLE teamstimetable(class text, start_time text, end_time text, day text)''')
	c.execute('''CREATE TABLE webextimetable(class text, start_time text, end_time text, day text, url text)''')
	conn.commit()
	conn.close()
	print("Created timetable Database")

def validate_input(regex,inp):
	if not re.match(regex,inp):
		return False
	return True

def validate_day(inp):
	days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

	if inp.lower() in days:
		return True
	else:
		return False

def validate_platform(inp):
	platforms = ["teams","webex","zoom"]

	if inp.lower() in platforms:
		return True
	else:
		return False

def add_timetable():
	if(not(path.exists("timetable.db"))):
		createDB()

	inp = int(input("1. Add Class\n2. Done Adding\nEnter Option : "))
	while (inp == 1):
		name = input("Enter class name : ")

		start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",start_time)):
			print("Invalid input, try again")
			start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

		end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",end_time)):
			print("Invalid input, try again")
			end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

		day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
		while not(validate_day(day.strip())):
			print("Invalid input, try again")
			day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")

		platform = input("Platform class being held (Teams/Webex/Zoom) : ")
		while not(validate_platform(platform.strip())):
			print("Invalid input, try again")
			platform = input("Platform class being held (Teams/Webex/Zoom) : ")

		if platform.lower() == "webex":
			url = input("URL of class : ")

		conn = sqlite3.connect('timetable.db')
		c=conn.cursor()

		# Insert a row of data
		if platform.lower() == "teams":
			c.execute("INSERT INTO teamstimetable VALUES ('%s','%s','%s','%s')"%(name,start_time,end_time,day))
		if platform.lower() == "webex":
			c.execute("INSERT INTO webextimetable VALUES ('%s','%s','%s','%s','%s')"%(name,start_time,end_time,day,url))
		conn.commit()
		conn.close()

		print("Class added to database\n")

		inp = int(input("1. Add Class\n2. Done Adding\nEnter Option : "))

def view_timetable():
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	print("teamstimetable")
	for row in c.execute('SELECT * FROM teamstimetable'):
		print(row)
	print("webextimetable")
	for row in c.execute('SELECT * FROM webextimetable'):
		print(row)
	conn.close()

def joinwebexclass(class_name,start_time,end_time,url):
	driver = webdriver.Chrome(options=opt,service_log_path='NUL')

	driver.get(url)

	time.sleep(5)

	cancel_button = pyautogui.locateCenterOnScreen('cancel.png')
	pyautogui.moveTo(cancel_button)
	pyautogui.click()

	time.sleep(4)

	discard_button = pyautogui.locateCenterOnScreen('discard.png')
	if discard_button != None :
		pyautogui.moveTo(discard_button)
		pyautogui.click()

	#join from browser button
	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[3]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/div[3]/a')))
	driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[1]/div/div[2]/div[1]/div[2]/div[2]/div[3]/a').click()

	#switching to iframe
	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[2]/iframe')))
	iframe = driver.find_element_by_xpath('/html/body/div[2]/iframe')
	driver.switch_to.frame(iframe)

	name = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/input')
	name.clear()
	name.send_keys(WEBEX_CREDS['name'])

	email = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[3]/input')
	email.clear()
	email.send_keys(WEBEX_CREDS['email'])

	#Next Button
	driver.find_element_by_xpath('//*[@id="guest_next-btn"]').click()

	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[4]/div[2]/div/div/div/div/div[1]/button')))

	driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div/div/div/div[1]/button').click() #pop Up Message

	microphone = driver.find_element_by_xpath('//*[@id="meetingSimpleContainer"]/div[3]/div[2]/div[1]/div/button')
	microphone.click()


	webcam = driver.find_element_by_xpath('//*[@id="meetingSimpleContainer"]/div[3]/div[2]/div[2]/div/button')
	webcam.click()

	#join Meeting Button
	driver.find_element_by_xpath('//*[@id="interstitial_join_btn"]').click()

	print("Joined Class ", class_name)
	discord_webhook.send_msg(class_name=class_name,status="joined",start_time=start_time,end_time=end_time)

	tmp = "%H:%M"

	current_time = datetime.now().strftime("%H:%M")

	class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(current_time,tmp)

	time.sleep(class_running_time.seconds - 30)

	#leave Meeting Buttons
	driver.find_element_by_xpath('//*[@id="react_controlbar"]/div[2]/div[1]/div[6]/div/button').click()
	driver.find_element_by_xpath('//*[@id="leave_dlg_content"]/div/button[2]').click()

	print("Class left ", class_name)
	discord_webhook.send_msg(class_name=class_name,status="left",start_time=start_time,end_time=end_time)

	driver.switch_to.default_content()

	driver.close()


def jointeamsclass(class_name,start_time,end_time):
	global driver

	driver = webdriver.Chrome(options=opt,service_log_path='NUL')

	driver.get("https://teams.microsoft.com")

	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

	if("login.microsoftonline.com" in driver.current_url):
		print("logging in")
		emailField = driver.find_element_by_xpath('//*[@id="i0116"]')
		emailField.click()
		emailField.send_keys(TEAMS_CREDS['email'])
		driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Next button
		time.sleep(2)
		passwordField = driver.find_element_by_xpath('//*[@id="i0118"]')
		passwordField.click()
		passwordField.send_keys(TEAMS_CREDS['passwd'])
		driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
		time.sleep(2)
		driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #remember login

	time.sleep(5)

	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="app-bar-2a84919f-59d8-4441-a975-2a8c2643b741"]')))
	driver.find_element_by_xpath('//*[@id="app-bar-2a84919f-59d8-4441-a975-2a8c2643b741"]').click()


	classes_available = driver.find_elements_by_class_name("team-card")

	for i in classes_available:
		if class_name.lower() in i.get_attribute('innerHTML').lower():
			print("JOINING CLASS ",class_name)
			i.click()
			break


	time.sleep(4)


	try:
		joinbtn = driver.find_element_by_class_name("ts-calling-join-button")
		joinbtn.click()

	except:
		#join button not found
		#refresh every minute until found
		global timelost
		while(timelost <= 15):
			print("Join button not found, trying again")
			time.sleep(60)
			driver.refresh()
			timelost += 1
			jointeamsclass(class_name,start_time,end_time)
			# schedule.every(1).minutes.do(joinclass,class_name,start_time,end_time)
		timelost = 1
		print("Seems like there is no class today.")
		discord_webhook.send_msg(class_name=class_name,status="noclass",start_time=start_time,end_time=end_time)

	else:
		time.sleep(4)
		webcam = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
		if(webcam.get_attribute('title')=='Turn camera off'):
			webcam.click()
		time.sleep(1)

		microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
		if(microphone.get_attribute('title')=='Mute microphone'):
			microphone.click()

		time.sleep(1)
		joinnowbtn = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
		joinnowbtn.click()

		discord_webhook.send_msg(class_name=class_name,status="joined",start_time=start_time,end_time=end_time)

		#now schedule leaving class
		tmp = "%H:%M"

		current_time = datetime.now().strftime("%H:%M")

		class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(current_time,tmp)

		time.sleep(class_running_time.seconds - 30)

		driver.find_element_by_class_name("ts-calling-screen").click()


		driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click() #come back to homepage
		time.sleep(1)

		driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
		print("Class left")
		discord_webhook.send_msg(class_name=class_name,status="left",start_time=start_time,end_time=end_time)

		driver.find_element_by_xpath('//*[@id="app-bar-2a84919f-59d8-4441-a975-2a8c2643b741"]').click()
		driver.close()

def start_bot():
	global driver
	conn = sqlite3.connect('timetable.db')
	c=conn.cursor()
	for row in c.execute('SELECT * FROM teamstimetable'):
		#schedule all classes
		name = row[0]
		start_time = row[1]
		end_time = row[2]
		day = row[3]

		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="friday":
			schedule.every().friday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))
		if day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(jointeamsclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s on Teams"%(name,day,start_time))

	for row in c.execute('SELECT * FROM webextimetable'):
		#schedule all classes
		name = row[0]
		start_time = row[1]
		end_time = row[2]
		day = row[3]
		url = row[4]

		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="friday":
			schedule.every().friday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))
		if day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(joinwebexclass,name,start_time,end_time,url)
			print("Scheduled class '%s' on %s at %s on webex"%(name,day,start_time))

	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)

if __name__ == '__main__':

	inp = int(input("1. Modify timtable\n2. View Timetable\n3. Start Bot\nEnter Option : "))

	if inp == 1:
		add_timetable()
	if inp == 2:
		view_timetable()
	if inp == 3:
		start_bot()
