FROM python:3.7
RUN pip install flask numpy
COPY main.py game.py boards.py greedy.py /home/app/

WORKDIR /home/app/
ENV FLASK_APP=/home/app/main.py
CMD [ "flask", "run", "--host", "0.0.0.0" ]

