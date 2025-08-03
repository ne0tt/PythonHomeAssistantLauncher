This project came about after watching an Excellent video by Paul Hibbert Home Tech about controlling your computer using Home Assistant.

Open apps or run things on your computer by accessing a URL?

The Result?
I now have a Home Assistant script that calls rest commands through automation.

When My existing Home Automation runs in the evening my blinds close and the lights dim.
I now have my Linux machine (I use Arch BTW) changes the daytime theme from blue to orange and runs HyprShade to lower the blue tones of my monitors.

It's Pretty neat....

What were my requirements?
Security and
Ease of Configuration.

I currently have this running in a python venv.

Packages used :
    flask AND
    dotenv (to pull a secret key)

How does this work?
Basically you run a light weight web server on your machine, You add a url that you wish to use and a script or shell command that you wish to run on your local machine when the URL is accessed.

It uses a POST method and expects a header bearer (matching the SECRET_KEY in your .env file)
Home Assistant uses the rest_commands in your HA config,  posts to the url whch in turn runs things on your machine.

It is locked down so only IP addresses you specify can access and run commands.

Setup...

Install python, create a python venv (optional but reccomended)
run the virtual enviro

pip install flask

pip install dotenv

Create a file called .env in the same dir as HomeAsistantLauncher.py

Add the line SECRET_KEY=YourSecretKey

Configure HomeAssitantLauncher.json with:

The port you want flask to run on

The IP of the machine you wish to control

IP's of machines that are allowed access (Your local host for text and Your Home Assitant IP)

a URL and the full path to the thing you want to run.


When you first run Home AssitantLauncher.py it will generate a file called:
HA-Rest-Commands.txt that can be pasted into yout ome Assistant Configuration file

Restart Home Assistant (i'd reccomend creating a backup!)

Set up a script or automation that calls your URL in your Configuration.

---

The Future - 
I'll move the Bearer string from HA Config
Might create a .service file so I can run this all the time.

You need to be familiar with Home Assitant and a little bit of python.
Have fun!
