from tkinter import *
import math
import time
from openCV import *
from webscraping import *
from widgets import *
import random
from PIL import Image, ImageTk
import json
import logging
   
maxArticles = 5
maxLength = 40
smallTextSize = 18
mediumTextSize = 28
largeTextSize = 48
timerDelay = 100
longerTimerDelay = 500
prolongedTimerDelay = 300000

logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)


class Clock(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        
        self.second, self.minute, self.hour, self.meridiem = "", "", "", ""
        self.time, self.date = "", ""
        
        self.timeLbl = Label(self, font="Helvetica %d" % largeTextSize, 
            fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        
        self.dateLbl = Label(self, text=self.date, font="Helvetica %d" % \
            smallTextSize, fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.returnTime()
        self.returnDate()
        
    # Uses time to create a string containing the hour minute and AM or PM
    def returnTime(self):
        hour = str(int(time.strftime("%I")))
        minute = time.strftime("%M")
        meridiem = time.strftime("%p")
        self.time = hour + ":" + minute + " " + meridiem
        self.timeLbl.config(text=self.time)
        self.after(timerDelay, self.returnTime)
        
    # Uses same time feature to return the date and removes the time from it
    def returnDate(self):
        fullDate = time.strftime("%c").split()
        fullDate.pop(3) #Removes time from list
        fullDate = " ".join(fullDate)
        if self.date != fullDate:
            self.date = fullDate
            self.dateLbl.config(text=self.date)
        # Calls itself every 100 ms
        self.after(timerDelay, self.returnDate)
        
    def drawAnalog(self, canvas, xc, yc, r):
        self.xc, self.yc, self.r = xc, yc, r
        #draws outer circle of analog clock
        x0, x1 = self.xc - self.r, self.xc + self.r
        y0, y1 = self.yc - self.r, self.yc + self.r
        canvas.create_oval(x0, y0, x1, y1, outline="white", width=4)
        
        #draws the hour hand of the clock
        secPerMin = 60
        self.hour += self.minute/secPerMin
        hourAngle = math.pi/2 - 2*math.pi*self.hour/12
        hourRadius = self.r*1/2
        hourX = self.xc + hourRadius * math.cos(hourAngle)
        hourY = self.yc - hourRadius * math.sin(hourAngle)
        canvas.create_line(self.xc, self.yc, hourX, hourY, fill="white",
            width=2) #unhardcode this
        
        #draws the minite hand of the clock
        minuteAngle = math.pi/2 - 2*math.pi*self.minute/secPerMin
        minRatio = 8/10
        minuteRadius = self.r*minRatio
        minuteX = self.xc + minuteRadius * math.cos(minuteAngle)
        minuteY = self.yc- minuteRadius *math.sin(minuteAngle)
        canvas.create_line(self.xc, self.yc, minuteX, minuteY, fill="white", 
            width=2) #unhardcode this
            
        #draws the thinner second hand that moves more noticeably
        secAngle = math.pi/2 - 2*math.pi*self.second/secPerMin
        secRatio = 9/10
        secRadius = self.r*secRatio
        secX = self.xc + secRadius * math.cos(secAngle)
        secY = self.yc - secRadius * math.sin(secAngle)
        canvas.create_line(self.xc, self.yc, secX, secY, fill="white", width=1)
            
class Weather(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # Initializes variables for widgets
        self.temp, self.desc, self.icon, self.peiod = "", "", "", ""
        self.forecast = ""
        self.returnWeather()
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
    
    def returnWeather(self):
        self.forecast = returnForecast()
        periods = self.currentPeriods()
        currPeriod = periods[0]
        self.period = self.addSpaces(currPeriod)
        self.current = self.forecast[currPeriod]
        self.temp = self.forecast["Temp"]
        self.desc = self.forecast[currPeriod][0]
        self.desc = self.addSpaces(self.desc)
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
        
class Forecast(Frame):    
        
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.forecastContainer = Frame(self, bg="black")
        self.forecastContainer.pack(side=TOP)
        self.forecast = returnForecast()
        self.format()
        
    def format(self):
        periods = []
        for key in self.forecast:
            # Does not add the weekday night forecasts to list
            if "Night" not in key:
                periods.append(key)
        # Removes temp that was put in the end of the dict
        periods.pop() 
        for period in periods:
            desc = self.forecast[period][2]
            weather = desc
            if len(weather) > 2*maxLength:
                weather = weather[:2*maxLength] + "..."
            self.weatherLbl = Label(self, text=weather, font="Helvetica %d " \
                % smallTextSize, fg="white", bg="black")
            self.weatherLbl.pack(side=TOP, anchor=N)
        
class News(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.articles = ""
        self.category = "News"
        self.calendarLbl = Label(self, text=self.category, font= \
            "Helvetica %d underline" % mediumTextSize, fg="white", bg="black") 
        self.calendarLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.returnHeadlines()
        
    # Calls webscraping to get headlines and then packs them individually
    def returnHeadlines(self):
        self.articles = returnNews()
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
    
    #Gathers events from webscraping file and pack them individually    
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
        #Converts 24 hour clock time to 12 hour
        if int(time[:2]) > 12:
            time = str(int(time[:2]) - 12) + time[2:]
        #Removes zeroes from the date
        if date[0] == "0" or date[3] == "0":
            if date[0] == "0" and date[3] == "0":
                date = date[1:3] + date[4]
            elif date[0] == "0":
                date = date[1:]
            elif date[3] == "0":
                date = date[:3] + date[4]
        #Removes zeroes at the beginning of the time
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
        index = random.randint(0, len(self.greetings) - 1)
        self.greeting = list(self.greetings)[index]
        # If file that holds the dictionary doesn't exist, initialize it
        if not os.path.exists("users.txt"):
            self.users = {}
        # Else if it exists load it
        if os.path.exists("users.txt"):
            with open("users.txt") as jsonFile:
                self.users = json.load(jsonFile)
        self.user = recognizeFace(self.users)
        # If no face detected do not greet
        if self.user == "":
            self.greeting = ""
        self.greetingLbl = Label(self, text=self.greeting + "\n" + self.user, 
            font="Helvetica %d " % mediumTextSize, fg="white", bg="black")
        self.greetingLbl.pack()
        
        # UNCOMMENT THIS TO ENTER A NEW USER
        #self.enterNewUser()
        
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
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        # Hitting enter changes window to size of the screen
        self.tk.bind("<Return>", self.toggleFullscreen)
        self.tk.bind("<Escape>", self.endFullscreen)
        # Creates instances of each class created
        self.clock = Clock(self.topFrame)
        self.news = News(self.bottomFrame)
        self.calender = Calendar(self.bottomFrame)
        self.weather = Weather(self.topFrame)
        self.greeting = Greeting(self.bottomFrame)
        self.forecast = Forecast(self.topFrame)
        self.displayed = False # Does not start out displaying anything
        self.frozen = False # Overrides display completely with hand gestures
        self.checkFaces()
        self.checkHands()
        self.greetUser()
        
    def checkFaces(self):
        self.run = returnFaces()
        if self.frozen == False:
            if self.run == True and self.displayed == True:
                pass
            #If the screen is not displaying widgets but a face is now detected,
            #the widgets are placed again
            if self.run == True and self.displayed == False:
                self.toggleDisplayOn()
            #If the screen is displaying widgets but no face is detected, 
            #the widgets are temporarily removed
            if self.run == False and self.displayed == True:
                self.toggleDisplayOff()
            if self.run == False and self.displayed == False:
                self.toggleDisplayOff()
        #Function continues to call itself every 100 ms
        self.tk.after(longerTimerDelay, self.checkFaces)
        
    def checkHands(self):
        #If the display is on and any fingers detected, turn off screen
        if self.run == True:
            #print(returnFingers()) #Debugging purposes
            if returnFingers() == 3 and self.displayed == True:
                self.toggleDisplayOff()
                self.frozen = True
                print("off")
            if returnFingers() == 3 and self.displayed == False:
                self.toggleDisplayOn()
                self.frozen = True
                print("on")
            if returnFingers() == 5 and self.frozen == False:
                self.frozen == True
                self.forecast.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, 
                    anchor=CENTER)
                self.toggleDisplayOff()
            if returnFingers() == 5 and self.frozen == False:
                self.frozen == False
                self.forecast.place_forget()
                self.toggleDisplayOn()
        self.tk.after(timerDelay, self.checkHands)
        
    def greetUser(self):
        self.greeting.place(bordermode=OUTSIDE, relx=0.5, rely=0.5, y = -200, 
            anchor=CENTER)
        self.tk.after(100*timerDelay, self.stopGreeting)
        
    def stopGreeting(self):
        self.greeting.place_forget()
        
    # Toggles on if the display was not previously showing and a face is present
    def toggleDisplayOn(self):
        self.clock.pack(side=RIGHT, anchor=N, padx=100, pady=60)
        self.news.pack(side=LEFT, anchor=S, padx=(100,10), pady=60)
        self.calender.pack(side=RIGHT, anchor=S, padx=(10,100), pady=60)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
        self.displayed = True
    
    # If display was on but a face is no longer present display toggles off
    def toggleDisplayOff(self):
        self.clock.pack_forget()
        self.news.pack_forget()
        self.calender.pack_forget()
        self.weather.pack_forget()
        self.displayed = False
        
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
    
