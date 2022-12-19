# googlehomeplayer
This is an old django web project to send music and generate a playlist for Google Home speakers with a simple and useful browser (your mobile have one).

Just I have improved 3 years of this forgotten project, I've migrated it to last django version and I've made some fixes related to new commits on pychromecast library (to new people). But nothing incredible, just the easiest fixes to get it working today with lastest dependencies.

In the past it was working with static content, it's just a prove of concept. But this project will evolve Google is breaking functionalities, so, probably one day it will not work anymore, sorry, is Google.

This project is based on django, so if you want to run this project simply:

`python3 manage.py runserver 0.0.0.0:8000`

If you want to use other port just remember change it and sudo is required from 1 to 1024 ports (80 and 443 are in this range)

Open your favorite browser (please, use Firefox, it's your biggest friend!)

To install dependencies use pip:

`sudo pip3 install -r requirements.txt`

or do a manually instalation:

`sudo pip3 install django youtube_dl pychromecast`

With the past of years probably you'll need upgrade youtube_dl and pychromecast, so try with pip install --upgrade PACKAGE

First time, like any other django app needs some `synchronization` with internal model (at least when it was developed at first time, and contains those scripts), to make it simply launch:

Generates migrations (model):

`python3 manage.py makemigrations`

Migrate (sqlite):

`python3 manage.py migrate`

I'm not very sure if this project will be growing, probably I just do other project instead of re-work it, but if you want you could try launching a petition or opening issues or request support for more pages and functionalities. Anyway, you can tests current functionalities working fine.

Now I migrate 4 years and just test radio and youtube with an old first revision working chromecast (incredible, today is 2022!).

This project was released by @bitstuffing with love in 2018, and his license is GPLv3.

Enjoy!