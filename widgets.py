# File contains each class which correlates to a widget that gets displayed on
# the tkinter screen

from tkinter import *
import math
import time
from openCV import *
from webscraping import *
from widgets import *
from speechRecognition import *
import random
from PIL import Image, ImageTk
import json
import threading
   
# Initializes vairiables used by mutliple classes
maxArticles = 5
maxLength = 40
lineLength = 100
maxLines = 32
smallTextSize = 18
mediumTextSize = 28
largeTextSize = 48
timerDelay = 200
longerTimerDelay = 500
prolongedTimerDelay = 300000
forecastCommands = {"weather", "forecast"}
toggleCommands = {"on", "off"}
articleCommands = {"article", "news", "text"}

"""Concept of data used from 112 course notes
   https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html"""

class Struct(object): pass
data = Struct()
data.radius = 20
data.margin = 10
data.alert = ""


thread = threading.Thread(target=recognizeSpeech, args=())
thread.start()
  
print(thread)
        
        

class Clock(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        # Initializes the variables used in the widgets
        self.minute, self.hour, self.meridiem = "", "", ""
        self.time, self.date = "", ""
        
        # Creates text displaying the current time with AM or PM
        self.timeLbl = Label(self, font="Helvetica %d" % largeTextSize, 
            fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        
        # Creates a frame for the analog clock to be placed in 
        self.analogFrame = Frame(self, bg="black")
        self.analogFrame.pack(side=TOP, anchor=E, pady = 10)
        
        # Creates text diplaying an abbreviated date
        self.dateLbl = Label(self, text=self.date, font="Helvetica %d" % \
            smallTextSize, fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        
        # Calls recursive functions
        self.returnTime()
        self.returnDate()
        
        # Draws the clock which is packed in the frame
        self.width = data.width // 8
        self.analog = Canvas(self.analogFrame, width=self.width, 
            height=self.width, highlightthickness=0, bg="black")
        self.analog.pack(side=TOP, anchor=E)
        data.radius = self.width//2
        self.drawAnalog(self.width//2, self.width//2, data.radius)
        
    # Uses time to create a string containing the hour minute and AM or PM
    def returnTime(self):
        
        # Gathers hour and from time.strftime to use in widgets
        hour = str(int(time.strftime("%I")))
        minute = time.strftime("%M")
        self.hourInt, self.minuteInt = int(hour), int(minute)
        meridiem = time.strftime("%p")
        self.time = hour + ":" + minute + " " + meridiem
        self.timeLbl.config(text=self.time)
        
        # Calls everytime the day changes
        if self.hourInt == 12 and self.minuteInt == 0 and self.meridiem == "AM":
            self.returnDate()
        self.after(timerDelay, self.returnTime)
        
    # Uses same time feature to return the date and removes the time from it
    def returnDate(self):
        fullDate = time.strftime("%c").split()
        fullDate.pop(3) #Removes time from list
        fullDate = " ".join(fullDate)
        if self.date != fullDate:
            self.date = fullDate
            self.dateLbl.config(text=self.date)
                
    def drawAnalog(self, xc, yc, r):
        
        # Draws outer circle of analog clock
        self.xc, self.yc, self.r = xc, yc, r
        x0, x1 = self.xc - self.r, self.xc + self.r
        y0, y1 = self.yc - self.r, self.yc + self.r
        self.analog.create_oval(x0, y0, x1, y1, outline="white", width=4)
        
        # Draws the short hour hand of the clock
        secPerMin = 60
        self.hourInt += self.minuteInt/secPerMin
        hourAngle = math.pi/2 - 2*math.pi*self.hourInt/12
        hourRadius = self.r*1/2
        hourX = self.xc + hourRadius * math.cos(hourAngle)
        hourY = self.yc - hourRadius * math.sin(hourAngle)
        self.analog.create_line(self.xc, self.yc, hourX, hourY, fill="white",
            width=2) 
        
        # Draws the minute hand of the clock that is longer than the hour hand
        minuteAngle = math.pi/2 - 2*math.pi*self.minuteInt/secPerMin
        minRatio = 8/10
        minuteRadius = self.r*minRatio
        minuteX = self.xc + minuteRadius * math.cos(minuteAngle)
        minuteY = self.yc - minuteRadius *math.sin(minuteAngle)
        self.analog.create_line(self.xc, self.yc, minuteX, minuteY, 
            fill="white", width=2) 
        
        self.after(longerTimerDelay, self.update)
    
    # Redraws the analog clock so the time is always correct
    def update(self):
        self.analog.delete(ALL)
        self.drawAnalog(self.width//2, self.width//2, data.radius)
            
class Weather(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        # Initializes variables for widgets
        self.temp, self.desc, self.icon, self.peiod = "", "", "", ""
        self.forecast = ""
        self.returnWeather()
        
        # Creates the frames used in the weather widget and organizes them
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.iconLbl = Label(self.degreeFrm, image=self.icon, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.temperatureLbl = Label(self.degreeFrm, text=self.temp, 
            font=('Helvetica %d' % (largeTextSize)), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.descLbl = Label(self, text=self.period + ": " + self.desc, 
            font=('Helvetica %d' % mediumTextSize), fg="white", bg="black")
        self.descLbl.pack(side=TOP, anchor=W)
    
    # Calls the webscraping function and formats to create text on screen
    def returnWeather(self):
        self.forecast = returnForecast()
        periods = self.currentPeriods()
        currPeriod = periods[0]
        self.period = self.addSpaces(currPeriod)
        self.current = self.forecast[currPeriod]
        self.temp = self.forecast["Temp"]
        
        # Makes sure the short desc is only two descriptive words 
        self.desc = self.forecast[currPeriod][0]
        self.desc = self.addSpaces(self.desc)
        self.desc = self.format(self.desc)
        
        # Assigns an image based on the current weather and resizes 
        file = self.weatherIcon()
        self.icon = Image.open(file)
        self.icon = self.icon.resize((100,100), Image.ANTIALIAS)
        self.icon = ImageTk.PhotoImage(self.icon)
        
        # Calls itself every 5 minutes since weather doesn't change much
        self.after(prolongedTimerDelay, self.returnWeather)
        
    # Looks at the description in the dictionary and assigns an icon accordingly
    def weatherIcon(self):
        if "Showers" in self.current or "Rain" in self.current:
            file="Rain.png"
        elif "Sun" in self.current or "Clear" in self.current: 
            file="Sun.png"
        elif "Snow" in self.current: 
            file="Snow.png"
        elif "Cloudy" in self.current: 
            file="PartlySunny.png"
        elif "T-storm" in self.current:
            file="Storm.jpg"
        else: 
            file="Cloud.png"
        return file
        
    # Loops through keys in order so next time of day can be identified
    def currentPeriods(self):
        periods = []
        for key in self.forecast:
            periods.append(key)
        #Removes key for temperature which is not a period
        periods.pop() 
        return periods
        
    # Some descriptions do not have spaces so this adds them where necessary
    def addSpaces(self, phrase):
        for i in range(0, len(phrase)-1):
            if phrase[i].islower() and phrase[i+1].isupper():
                phrase = phrase[:i+1] + " " + phrase[i+1:]
        return phrase
        
    # Changes messed up descs like "Partly Cloudythen" to "Partly Cloudy"
    def format(self, phrase):
        phrase = phrase.split(" ")
        phrase = phrase[0:2]
        desc = []
        for item in phrase:
            if "then" in str(item):
                item = item[:len(item)-len("then")]
            desc.append(item)
        phrase = " ".join(desc)
        return phrase
        
class Forecast(Frame):    
        
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.forecastContainer = Frame(self, bg="black")
        self.forecastContainer.pack(side=TOP)
        self.forecast = returnForecast()
        self.format()
        
    def format(self):
        periods = []
        # Does not add the weekday night forecasts to list
        for key in self.forecast:
            if "Night" not in key: periods.append(key)
            
        periods.pop() # Removes temp that was put in the end of the dict
        for period in periods:
            desc = self.forecast[period][2]
            weather = desc + "\n"
            # Formats strings to specific length over the space of two lines
            if len(weather) > 2*maxLength:
                firstHalf = weather[:2*maxLength]
                index = self.findLastSpace(firstHalf)
                if len(weather) > 2*2*maxLength:
                    weather = (weather[:index] + "\n" + 
                        weather[index:2*2*maxLength] + "..." + "\n")
                else:
                    weather = weather[:index] + "\n" + weather[index:]
            photo = self.weatherIcon(weather) 
            
            # Places a small icon representing the weather above each day
            self.iconLbl = Label(self.forecastContainer, bg='black', image=photo)
            self.iconLbl.image = photo
            self.iconLbl.pack(side=TOP, anchor=N)
            
            # Places a longer desc of the weather for each day of the week
            self.weatherLbl = Label(self.forecastContainer, text=weather, 
                font="Helvetica %d " % smallTextSize, fg="white", bg="black")
            self.weatherLbl.pack(side=TOP, anchor=N)
        
    # Checks the weather, assigns a pic, opens it, and resizes it
    def weatherIcon(self, weather):
        if "Showers" in weather or "Rain" in weather:
            file="Rain.png"
        elif "Sun" in weather or "Clear" in weather: 
            file="Sun.png"
        elif "Snow" in weather: 
            file="Snow.png"
        elif "Cloudy" in weather: 
            file="PartlySunny.png"
        elif "T-storm" in weather:
            file="Storm.jpg"
        else: 
            file="Cloud.png"
        image = Image.open(file)
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)
        return photo
        
    # Finds the index of the last space so a string can be split at a full word
    def findLastSpace(self, s):
        spaces = []
        for i in range(len(s)):
            if s[i] == " ":
                spaces.append(i)
        return spaces[-1]
        
class News(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.category = "News"
        self.calendarLbl = Label(self, text=self.category, font= \
            "Helvetica %d underline" % mediumTextSize, fg="white", bg="black") 
        self.calendarLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.articles = []
        self.returnHeadlines()
        
    # Calls webscraping to get headlines and then packs them individually
    def returnHeadlines(self):
        data.articleDict = returnNews()
        for article in data.articleDict:
            self.articles.append(article)
        if len(self.articles) < maxArticles:
            self.gatherMore()
        for title in self.articles[:maxArticles]:
            headline = Headlines(self.headlinesContainer, title)
            headline.pack(side=TOP, anchor=W)
        # Calls itself every 5 minutes so news headlines stay put for a while
        self.after(prolongedTimerDelay, self.returnHeadlines)
    
    # If not enough articles found calls the function again    
    def gatherMore(self):
        self.articles += returnNews()
        
class Headlines(Frame):
    
    def __init__(self, parent, title):
        Frame.__init__(self, parent, bg='black')
        
        # Restricts the length of articles titles placed in the widget
        if len(title) > maxLength:
            self.title = title[:maxLength] + "..."
        else:
            self.title = title
        self.eventLbl = Label(self, text=self.title, font="Helvetica %d " \
            % smallTextSize, fg="white", bg="black")
        self.eventLbl.pack(side=LEFT, anchor=N)
        
class Article(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        self.article = ""
        for article in data.articleDict:
            self.article = article
            break #Only takes the text for the first article in the dict
        self.content = data.articleDict[self.article]
        self.paragraphs = self.content.split("\n")
        self.formatted = ""
        
        self.articleContainer = Frame(self, bg="black")
        self.articleContainer.pack(side=TOP)
        self.format()
        
    # Makes sure no line is longer than a presest length 
    def format(self):
        for paragraph in self.paragraphs:
            result = ""
            lines = len(paragraph) // lineLength
            for i in range(lines+1):
                if i == lines:
                    slice = paragraph[(i)*lineLength:] + "\n"
                    result += slice
                else:
                    slice = paragraph[(i)*lineLength: (i+1)*lineLength] + "\n"
                    result += slice
            self.formatted += result
        count = 0
        # Limits the number of lines of the article that is displayed on screen
        for i in range(len(self.formatted)):
            if self.formatted[i] == "\n":
                count += 1
                if count >= maxLines:
                    self.formatted = self.formatted[:i+1]
                    break
        self.articleLbl = Label(self.articleContainer, text=self.formatted, 
            font="Helvetica %d " % smallTextSize, fg="white", bg="black")
        self.articleLbl.pack(side=LEFT, anchor=N, pady = 20)
        
class Calendar(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        self.eventLst = ""
        self.category = "Calendar"
        
        self.calendarLbl = Label(self, text=self.category, font= \
            "Helvetica %d underline" % mediumTextSize, fg="white", bg="black") 
        self.calendarLbl.pack(side=TOP, anchor=E)
        
        self.eventsContainer = Frame(self, bg="black")
        self.eventsContainer.pack(side=TOP)
        
        self.returnEvents()
    
    # Gathers events from webscraping file and pack them individually    
    def returnEvents(self):
        self.events = returnCalendar()
        for title in self.events:
            event = Events(self.eventsContainer, title)
            event.pack(side=TOP, anchor=W)
        # Calls itself every 5 minutes since personal events will not change much
        self.after(prolongedTimerDelay, self.returnEvents)
        
class Events(Frame):
    
    def __init__(self, parent, title):
        Frame.__init__(self, parent, bg='black')
        
        self.title = title
        self.format()
        
        self.eventLbl = Label(self, text=self.title, font="Helvetica %d " \
            % smallTextSize, fg="white", bg="black")
        self.eventLbl.pack(side=LEFT, anchor=N)
        
    def format(self):
        details, name = self.title[0], self.title[1]
        time, date = details[11:16], details[5:10]
        
        # Converts 24 hour clock time to 12 hour
        if int(time[:2]) > 12:
            time = str(int(time[:2]) - 12) + time[2:]
            
        # Removes zeroes from the date
        if date[0] == "0" or date[3] == "0":
            if date[0] == "0" and date[3] == "0":
                date = date[1:3] + date[4]
            elif date[0] == "0":
                date = date[1:]
            elif date[3] == "0":
                date = date[:3] + date[4]
        # Removes zeroes at the beginning of the time
        if time[0] == "0": 
            time = time[1:]
        event =  "%s %s %s" % (date, time, name)
        if len(event) > maxLength:
            event = event[:maxLength] + "..."
        self.title = event
        
class Greeting(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        # Set of possible greetings to the user which is chosen randomly
        self.greetings = {"Welcome,", "Hello,", "Hi,", "Greetings,"}
        self.timeBasedGreeting()
        self.index = random.randint(0, len(self.greetings) - 1)
        self.greeting = list(self.greetings)[self.index]
        
        # If file that holds the dictionary doesn't exist, initialize it
        if not os.path.exists("users.txt"):
            self.users = {}
            
        # Else if it exists load it
        if os.path.exists("users.txt"):
            with open("users.txt") as jsonFile:
                self.users = json.load(jsonFile)
        
        self.user = recognizeFace(self.users) 

        # If no face detected do not greet
        
        self.greetingLbl = Label(self, text=self.greeting + "\n" + self.user 
        + "\n" + data.alert, 
            font="Helvetica %d " % mediumTextSize, fg="white", bg="black")
        self.greetingLbl.pack()
        
        self.returnUser()
        
               
        # UNCOMMENT THIS TO ENTER A NEW USER
        #self.enterNewUser()
        
    def returnUser(self):
        if self.user == "":
            self.greeting = ""
        self.greetingLbl.config(text=self.greeting + "\n" + self.user + "\n" + data.alert)
        
    # Changes the greetings based on the time of the day
    def timeBasedGreeting(self):
        hour = str(int(time.strftime("%I")))
        meridiem = time.strftime("%p")
        
        # If the morning could greet user with good morning
        if meridiem == "AM":
            self.greetings.add("Good Morning,")
            if "Good Afternoon," in self.greetings:
                self.greetings.remove("Good Afternoon,")
            if "Good Evening," in self.greetings:
                self.greetings.remove("Good Evening,")
                
        # If the afternoon, based on the hour greets user differently
        if meridiem == "PM":
            if int(hour) < 5:
                self.greetings.add("Good Afternoon,")
            if int(hour) >= 5:
                self.greetings.add("Good Evening,")
            if "Good Morning," in self.greetings:
                self.greeting.remove("Good Morning,")
        self.after(prolongedTimerDelay, self.timeBasedGreeting)
        
    # Trains the facial recognizer for a new user
    def enterNewUser(self):
        
        # If dict is empty start with an id of 0
        if len(self.users) == 0:
            id = 0
        else:
            id = int(self.prevID()) + 1
        name = datasetGenerator(id)
        self.users[id] = name
        
        # Feeds the data to the recognizer to be trained
        faces, ids = getImagesAndLabels("trainer")
        recognizer.train(faces, np.array(ids))
        recognizer.save("recognizer/trainingData.yml")
        
        # Save the json file whenever a new user registers their id and name
        with open("users.txt", "w") as outfile:
            json.dump(self.users, outfile)

    # Looks at the last id used in the dictionary for a user
    def prevID(self):
        ids = []
        for key in self.users:
            ids.append(key)
        return ids[-1]
            
"""Modified this code to allow the window to encompass the entier screen
   https://github.com/HackerHouseYT/Smart-Mirror"""
            
class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        
        # Creates the two main frames used for widgets on the top and bottom
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        
        # Retrives the width and height of the window size 
        data.width = self.tk.winfo_screenwidth()
        data.height = self.tk.winfo_screenheight()
        
        # Hitting enter changes window to size of the screen
        self.state = False
        self.tk.bind("<Return>", self.toggleFullscreen)
        self.tk.bind("<Escape>", self.endFullscreen)
        
        
        # Creates instances of each class created
        self.greeting = Greeting(self.topFrame)
        self.clock = Clock(self.topFrame)
        self.news = News(self.bottomFrame)
        self.calender = Calendar(self.bottomFrame)
        self.weather = Weather(self.topFrame)
        self.forecast = Forecast(self.tk)
        self.article = Article(self.tk)
        
        # Initializes bools that control the display
        self.displayed = False # Does not start out displaying anything
        self.frozen = False # Overrides display completely with hand gestures
        self.listening = False
        self.checkFaces()
        
    # Calls the OpenCV function and displays widgets if a face is detected
    def checkFaces(self):
        self.run = returnFaces()
        if self.frozen == False:
            
            #If the screen is not displaying widgets but a face is now detected,
            #the widgets are placed again
            if self.run == True and self.displayed == False:
                self.toggleDisplayOn()
                #self.toggleGreetingOn()
            #If the screen is displaying widgets but no face is detected, 
            #the widgets are temporarily removed
            if self.run == False and self.displayed == True:
                self.toggleDisplayOff()
                #self.toggleGreetingOff()
            if self.run == False and self.displayed == False:
                self.toggleDisplayOff()
                #self.toggleGreetingOff()
        #Function continues to call itself every 100 ms
        self.tk.after(longerTimerDelay, self.checkFaces)
        self.tk.after(100*timerDelay, self.checkHands)

        
    # Calls the OpenCV function and listens for speech if any fingers detected
    def checkHands(self):
        
        # Busy environments will often mistake background as two fingers so more
        # must be used to initiate speech commands
        if self.run == True and self.listening == False and \
        returnFingers() >= 2:
            data.alert = "* Listening *"
            print(data.alert)
            self.greeting.returnUser()
            self.tk.after(10*timerDelay, self.checkSpeech())
        self.tk.after(longerTimerDelay, self.checkHands)
        
    # Calls the PyAudio function and sees if it correlates to available commands
    def checkSpeech(self):
        # Runs the recognition function and checks that it was successful
        self.keyword = ""
        if self.frozen == False:
            self.listening = True
            response = recognizeSpeech()
            if response != None and response != "":
                self.keyword = response
            # If a command word is found it is executed
            for command in forecastCommands:
                if command in self.keyword.lower(): self.toggleForecastOn()
            for command in articleCommands:
                if command in self.keyword.lower(): self.toggleArticleOn()
            for command in toggleCommands:
                if command in self.keyword.lower():
                    if command == "on":
                        self.frozen = True
                        self.toggleDisplayOff()
                        #self.toggleGreetingOff()
                    if command == "off":
                        self.frozen = False
                        self.toggleDisplayOn() 
                        #self.toggleGreetingOn()
        data.alert = ""
        self.greeting.returnUser()
        self.listening = False
            
    # Turns off the rest of the display and places forecast
    def toggleForecastOn(self):
        self.frozen = True
        self.toggleDisplayOff()
        self.toggleGreetingOff()
        self.forecast.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, 
            anchor=CENTER)
        self.tk.after(100*timerDelay, self.toggleForecastOff)
        
    # Displays the main after a certain amount of time and removes forecast
    def toggleForecastOff(self):
        self.frozen = False
        self.forecast.place_forget()
        self.toggleDisplayOn()
        self.toggleGreetingOn()
        
    # Turn off the display and places the article to be read
    def toggleArticleOn(self):
        self.frozen = True
        self.toggleDisplayOff()
        self.toggleGreetingOff()
        self.article.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, 
            anchor=CENTER)
        self.tk.after(100*timerDelay, self.toggleArticleOff)
        
    # After some time changes article back to main screen
    def toggleArticleOff(self):
        self.frozen = False
        self.article.place_forget()
        self.toggleDisplayOn()
        #self.toggleGreetingOn()
        
    # Initially displays greeting for user and disappears after a short time
    def toggleGreetingOn(self):
        self.greeting.returnUser()
        self.greeting.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, y = +200, 
            anchor=CENTER)
        #self.tk.after(100*timerDelay, self.toggleGreetingOff)
        
    def toggleGreetingOff(self):
        self.greeting.place_forget()
        
    # Toggles on if the display was not previously showing and a face is present
    def toggleDisplayOn(self):
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=(60,10))
        self.news.pack(side=LEFT, anchor=S, padx=(100,10), pady=60)
        self.calender.pack(side=RIGHT, anchor=S, padx=(10,100), pady=60)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=(60,10))
        
        self.greeting.returnUser()
        self.greeting.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, y = +200, 
            anchor=CENTER)
        
        self.displayed = True
        
# If display was on but a face is no longer present display toggles off
    def toggleDisplayOff(self):
        self.clock.pack_forget()
        self.news.pack_forget()
        self.calender.pack_forget()
        self.weather.pack_forget()
        #self.toggleForecastOff()
        #self.toggleGreetingOff()
        self.displayed = False
        
    # Bool for fullscreen changes each time this function is called
    def toggleFullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def endFullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()

    
