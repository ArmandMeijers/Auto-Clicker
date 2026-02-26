
#imports
import ttkbootstrap as ttk
from tkinter import PhotoImage
import time
import threading
from pynput.mouse import Controller, Button
from pynput import keyboard

class IntervalFrame(ttk.Frame): #Frame for interval chaning
    def __init__(self, master):
        super().__init__(master)

        #Setup grid format for widgets
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_rowconfigure((0,1), weight=0)

        #checks if entered value is a number
        def validate_input(input): 
            if input.isdigit() or input == "": 
                return True 
            return False

        vcmd = self.register(validate_input)

        #setUp entry widgets and starting values and place them in grid positions
        self.hoursEntry = ttk.Entry(self, validate="key", validatecommand=(vcmd, "%P"))
        self.hoursEntry.insert(0, 0)
        self.minsEntry = ttk.Entry(self, validate="key", validatecommand=(vcmd, "%P"))
        self.minsEntry.insert(0, 0)
        self.secEntry = ttk.Entry(self, validate="key", validatecommand=(vcmd, "%P"))
        self.secEntry.insert(0, 0)
        self.milisecEntry = ttk.Entry(self, validate="key", validatecommand=(vcmd, "%P"))
        self.milisecEntry.insert(0, 100)

        self.hoursEntry.grid(row=1, column=0, padx= 5)
        self.minsEntry.grid(row=1, column=1, padx= 5)
        self.secEntry.grid(row=1, column=2, padx= 5)
        self.milisecEntry.grid(row=1, column=3, padx= 5)

        #setup lables and place them in grid positions
        hoursLabel = ttk.Label(self, text="Hours").grid(row=0, column=0)
        minsLabel = ttk.Label(self, text="Minutes").grid(row=0, column=1)
        secsLabel = ttk.Label(self, text="Seconds").grid(row=0, column=2)
        milisecLabel = ttk.Label(self, text="Miliseconds").grid(row=0, column=3)

    #gets totalInterval and returns value in seconds
    def get_interval(self):
        hours = int(self.hoursEntry.get() or 0)
        minutes = int(self.minsEntry.get() or 0)
        seconds = int(self.secEntry.get() or 0)
        miliseconds = int(self.milisecEntry.get() or 0)

        totalInterval = ((hours * 3600) 
                         + (minutes * 60) 
                         + seconds 
                         + (miliseconds * 0.001))

        return totalInterval  #returned in seconds

class StartFrame(ttk.Frame): #Frame holds on/off button and  autoclicker logic
    def __init__(self, master, interval_frame):
        super().__init__(master)

        #Initialize Variables
        self.interval_frame = interval_frame

        self.running = False # state of autoclicker
        self.mouse = Controller()

        self.start_hotkey_listener() #Starts event listener for keyboard

        #set up grid psotions
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)

        #button style for on and off
        buttonStyle = ttk.Style()

        buttonStyle.configure(
            "Start.Big.TButton",
            font=("Helvetica", 25),
            padding=15,
            background="#27ae60",
            foreground="white"
        )
        buttonStyle.map(
            "Start.Big.TButton",
            background=[("active", "#2ecc71"), ("pressed", "#1e8449")],
            bordercolor="#27ae60"
        )

        buttonStyle.configure(
            "Stop.Big.TButton",
            font=("Helvetica", 25),
            padding=15,
            background="#c0392b",
            foreground="white"
        )
        buttonStyle.map(
            "Stop.Big.TButton",
            background=[("active", "#e74c3c"), ("pressed", "#922b21")],
            bordercolor="#c0392b"
        )

        #Create and place button widget
        self.startButton = ttk.Button(
            self,
            text="▶ Start",
            style="Start.Big.TButton",
            command=self.clickEngine
        )
        self.startButton.grid(row=0, column=0, sticky="nswe")

    #Keyboard press listener that runs on seperate thread
    def start_hotkey_listener(self):
        #function  that start auto clicker on press of F5 TODO make it dynamic eg user choice
        def on_press(key):
            if key == keyboard.Key.f6:
                self.clickEngine()

        #start function in another thread
        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    #switches between button styles and changes running variable boolean
    def toggleButtonState(self):
        self.running = not self.running

        if self.running:
            self.startButton.config(text="⏹ Stop (F6)", style="Stop.Big.TButton")
        else:
            self.startButton.config(text="▶ Start (F6)", style="Start.Big.TButton")

    #Clicks every x seconds while state = true
    def clickLoop(self):
        time.sleep(1) #small delay to prevent clicking again and turning off
        while self.running:
            value = self.interval_frame.get_interval() #gets entered values in intervalFrames entry widgets
            time.sleep(value)
            self.mouse.click(Button.left)

    #main controller of clicking logic, call functions and is called on button press
    def clickEngine(self):
        self.toggleButtonState()
        if self.running:
            #calls function in seperate thread to prevent Tkinter gui and autoclicker causing problems
            thread = threading.Thread(target=self.clickLoop, daemon=True)
            thread.start()

class MainApp(ttk.Window): #Main ui initializer
    def __init__(self):
        super().__init__()

        self.title("AutoClicker v1")
        self.geometry("500x400")
        self.maxsize(280,150)
        self.minsize(280,150)

        #configure grid layout for frames
        self.grid_rowconfigure(0, weight=0) #weight controlls ratio 0:10:2 (how much each frame take up of window)
        self.grid_rowconfigure(1, weight= 1)
        self.grid_columnconfigure(0, weight= 1)

        #place frames (sticky fills all sides if nsew)
        self.intervalFrame = IntervalFrame(self)
        self.intervalFrame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        startFrame = StartFrame(self, self.intervalFrame)
        startFrame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)


# Entry point of the program
if __name__ == "__main__":
    mainApp = MainApp()
    mainApp.mainloop() #mainloop of ui