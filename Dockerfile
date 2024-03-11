# GDA

FROM python:3.12-slim-bullseye

WORKDIR /curves

COPY requirements.txt requirements.txt
COPY requirements_dev.txt requirements_dev.txt

RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_dev.txt

EXPOSE 8501

COPY . .

CMD ["python3", "-m" , "streamlit", "run", "streamlit_app.py"]
