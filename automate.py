import datetime
from pathlib import Path
import random
import os
from time import sleep
import requests
import subprocess
import hashlib
from xml.dom import minidom
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
import multiprocessing
from multiprocessing import Process, Lock
import hashlib

def test_one(memu_port, lock):
    print(str(memu_port) + " " + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))    
    
    lock.acquire()
    try:  
        desired_caps = {}      
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '5.1.1'
        desired_caps['deviceName'] = '127.0.0.1:' + str(memu_port)
        desired_caps['udid'] = '127.0.0.1:' + str(memu_port)      
        desired_caps['appPackage'] = 'com.spotify.music'
        desired_caps['appActivity'] = '.MainActivity'
        desired_caps['newCommandTimeout'] = int(60)
        desired_caps['noReset'] = 'false'
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        driver.implicitly_wait(10)

        ## proxy change adb
        def proxy_change():
            proxy_http_code = 0
            while proxy_http_code != 200:
                proxy_list = requests.get("http://dablspot.h1n.ru/prx.php")
                content = list(proxy_list.text.split("\r\n"))
                print("proxy count: " + str(len(content)))
                proxyline = random.choice(content)
                proxysplit = proxyline.split(":")
                proxyaddress = proxysplit[0]
                proxyport = proxysplit[1]
                try:
                    proxies = {'http': proxyline, 'https': proxyline}
                    r = requests.get("https://www.google.com", proxies=proxies)
                    proxy_http_code = r.status_code
                    driver.execute_script('mobile: shell', {'command': 'settings put global http_proxy ' + str(proxyline)})
                    print(str(memu_port) + " using proxyline: " + str(proxyline))
                except requests.ConnectionError:
                    print(str(memu_port) + " failed to connect: " + str(proxyline))

        proxy_change()
            
        ##creating reg information
        reg_sex = random.randint(1,2)
         
        sleep(2)
        button_signup = driver.find_element_by_id("com.spotify.music:id/button_signup")
        button_signup.click()
        def reg_account(reg_sex):

            if reg_sex > 1:
                names = "names-female.txt"
            else:
                names = "names-male.txt"
            with open("res/names-male.txt") as infile:
                content = infile.read().splitlines()
            infile.close()
            secure_random = random.SystemRandom()
            reg_name = secure_random.choice(content)

            with open("res/surnames.txt") as infile:
                content = infile.read().splitlines()
            infile.close()
            secure_random = random.SystemRandom()
            reg_surname = secure_random.choice(content)
            
            s = "abcdefghijklmnopqrstuvwxyz01234567890"
            pass_len = 12
            reg_password = "".join(random.sample(s,pass_len))
            mailbox_len = random.randint(3,5)
            reg_mailbox = reg_name + reg_surname + "".join(random.sample(s,mailbox_len))
            el1 = driver.find_element_by_id("com.spotify.music:id/sign_up_email")
            el1.click()
            sleep(2) 
            el1.send_keys(reg_mailbox)
            driver.press_keycode(77)  ## AT @
            driver.press_keycode(35) ## g
            driver.press_keycode(41) ## m
            driver.press_keycode(29) ## a           
            driver.press_keycode(37) ## i
            driver.press_keycode(40) ## l
            driver.press_keycode(56) ## period 56           
            driver.press_keycode(31) ## c
            driver.press_keycode(43) ## o
            driver.press_keycode(41) ## m

            el2 = driver.find_element_by_id("com.spotify.music:id/sign_up_password")
            el2.clear()            
            el2.send_keys(reg_password)

        while driver.find_element_by_id('com.spotify.music:id/sign_up_next_button').is_enabled() != True:
            driver.press_keycode(4) ## back button
            button_signup.click()
            reg_account(reg_sex)
            
    finally:
        lock.release()

    ## dob and gender   
    el13 = driver.find_element_by_id("com.spotify.music:id/sign_up_next_button")
    el13.click()
    sleep(2)
    el14 = driver.find_element_by_id("com.spotify.music:id/sign_up_age_text")
    el14.click()
    el21 = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.DatePicker/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.NumberPicker[1]/android.widget.EditText")
    el21.click()

    reg_day = random.randint(0,5)
    i = 1
    while i <= reg_day:
        driver.press_keycode(19) ## dpad up
        sleep(0.5)
        i += 1
    driver.press_keycode(22) ## dpad right
    
    reg_month = random.randint(0,5)
    i = 1
    while i <= reg_month:
        driver.press_keycode(19)
        sleep(0.5) #0.5g
        i += 1
    driver.press_keycode(22) ## dpad right

    reg_year = random.randint(7,12)
    i = 1
    while i <= reg_year:
        driver.press_keycode(19)
        sleep(0.5) #0.5g
        i += 1

    el41 = driver.find_element_by_id("com.spotify.music:id/signup_datepicker_ok")
    el41.click()    
    el51 = driver.find_element_by_id("com.spotify.music:id/sign_up_gender_text")
    el51.click()
    el61 = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.ListView/android.widget.CheckedTextView[" + str(reg_sex) + "]")
    el61.click()

    ##create account with dob and gender
    create_acc_done = driver.find_element_by_id("com.spotify.music:id/sign_up_create_button")
    create_acc_done.click()
    sleep(10) ## 10g
    driver.press_keycode(61) ## dpad Tab
    sleep(0.5)
    driver.press_keycode(61) ## dpad Tab
    sleep(0.5)
    driver.press_keycode(66) ## Enter
    sleep(7) ## 3g
    driver.press_keycode(61) ## dpad Tab
    sleep(0.5)
    driver.press_keycode(61) ## dpad Tab
    sleep(0.5)
    driver.press_keycode(66) ## Enter

    ##clear browser data and open url
    def browser_open_playlist():
        driver.execute_script('mobile: shell', {'command': 'pm clear com.android.browser'})        
        driver.start_activity("com.android.browser", ".BrowserActivity");  
        el81 = driver.find_element_by_id("com.android.browser:id/url")
        el81.send_keys("https://open.spotify.com/user/nfgggrctc/playlist/0PbUgfhth?si=7HUVQRbhthtshqHiYJ_XlA")

        driver.press_keycode(66) ## keypad enter


    def save_stat():
        user_id = "pro2"
        non_hashed_stat = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\t" + str(user_id) + "\t" + str(memu_port)
        myhash = hashlib.sha1((non_hashed_stat.encode('utf-8')))
        hashed_stat = myhash.hexdigest()
        save_stat_filename = "stat/stat_" + str(datetime.datetime.now().strftime("%Y-%m-%d")) + ".txt"
        stat_file = open(save_stat_filename, "a+")
        stat_file.write(non_hashed_stat + "\t" + hashed_stat + "\n")
        stat_file.close()
    browser_open_playlist()

    ## follow button
    try:
        follow = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.View/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.View[1]/android.view.View/android.view.View/android.view.View/android.support.v4.view.ViewPager/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.ToggleButton")
        follow.click()
        print(str(memu_port) + " follow found")
    except NoSuchElementException:
        print(str(memu_port) + " follow NOT found")
        driver.quit()

    ## shuffle button
    try:
        shuffle = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.View/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.View[1]/android.view.View/android.view.View/android.widget.Button")
        shuffle.click()
        print(str(memu_port) + " shuffle found")
    except NoSuchElementException:
        print(str(memu_port) + " shuffle NOT found")
        driver.quit() 
    save_stat()
    sleep(random.randint(35,45))

    driver.implicitly_wait(5)
    next_count = random.randint(100,300)
    print(str(memu_port) + " next_count: " + str(next_count))
    for number in range(next_count): # 6g 30g
        print(str(memu_port) + " " + str(number))
        try:
            next = driver.find_element_by_accessibility_id("Skip to next")
            next.click()
            now_playing = driver.find_element_by_accessibility_id("Show Now Playing")
            now_playing.click()
            add_to_your_music = driver.find_element_by_accessibility_id("Add to Your Music")
            add_to_your_music.click()
            driver.press_keycode(4) ## back button
            print(str(memu_port) + " add_to_your_music found w/o no thanks") 
            save_stat()
            sleep(random.randint(35,45))
        except NoSuchElementException:
            driver.press_keycode(4) ## back button
            next = driver.find_element_by_accessibility_id("Skip to next")
            next.click()
            now_playing = driver.find_element_by_accessibility_id("Show Now Playing")
            now_playing.click()
            add_to_your_music = driver.find_element_by_accessibility_id("Add to Your Music")
            add_to_your_music.click()
            driver.press_keycode(4) ## back button
            print(str(memu_port) + " add_to_your_music found after no thanks")
            save_stat()
            sleep(random.randint(35,45))
    driver.quit()

if __name__ == '__main__':    
    lock = Lock()

    ## locating vms
    path_to_vms = 'c:/Program Files/Microvirt/MEmu/MemuHyperv VMs/'
    config_filename = 'MEmu.memu'
    dirlist = os.listdir(path_to_vms)
    commands = [
        'adb kill-server',
        'adb start-server'
        ]
    memu_ports = []
    for x in dirlist:
        path_to_memu_config = path_to_vms + x + '/' + x + '.memu'
        xmldoc = minidom.parse(path_to_memu_config)
        forwarding = xmldoc.getElementsByTagName("Forwarding")[0]
        adb_port = forwarding.attributes['hostport'].value
        print(x + " port: " + adb_port)
        commands.append('adb connect 127.0.0.1:' + adb_port)
        memu_ports.append(adb_port)
    commands.append('adb devices')
    print(commands)
    print(memu_ports)       
    
    def save_log(event):
        non_hashed_stat = event
        myhash = hashlib.sha1((non_hashed_stat.encode('utf-8')))
        hashed_stat = myhash.hexdigest()
        stat_file = open("stat/log.txt", "a+")
        stat_file.write(non_hashed_stat + "\t" + hashed_stat + "\n")
        stat_file.close()
    
    procs = []
    event = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\tstarting multiprocessing..."
    save_log(event)
    
    for index, number in enumerate(memu_ports):
        proc = Process(target=test_one, args=(number, lock), name=number)
        procs.append(proc)
        proc.start()
        event = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\tstarting process..."
        save_log(event)
        sleep(1)
        
    event = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\twaiting after proceses complete..."
    save_log(event)

    while True:    
        for proc in procs:
            if proc.is_alive():
                pass
            else:
                print("RESTART: " + str(proc.name))
                proc.join(15)
                procs.remove(proc)
                proc = Process(target=test_one, args=(proc.name, lock), name=proc.name)
                procs.append(proc)
                proc.start()
        sleep(30)