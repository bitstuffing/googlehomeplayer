# googlehomeplayer
This is a django web project to send music and generate a playlist for Google Home speakers with a simple and useful browser (your mobile have one)

Now it's working with static content, it's just a prove of concept. But this project will evolve

This project is based on django, so if you want to run this project simply:

`python3 manage.py runserver 0.0.0.0:8000`

If you want to use other port just remember change it and sudo is required from 1 to 1024 ports (80 and 443 are in this range)

Open your favorite browser (please, use Firefox, it's your biggest friend!)

To install dependencies use pip:

`sudo pip3 install django django-background-tasks youtube_dl pychromecast`

First time, like any other django app needs some `synchronization` with internal model, to make it simply launch:

`python3 manage.py makemigrations`
`python3 manage.py migrate`

This proyect probably will be growing supporting more pages and functionalities, but you can just tests current functionalities working fine.
