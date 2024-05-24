FROM python:3.12-slim-bullseye

WORKDIR /curves

COPY requirements.txt requirements.txt
COPY requirements_dev.txt requirements_dev.txt

RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements_dev.txt

RUN groupadd -g 999 app && \
    useradd -m -d /home/app/ -u 999 -g app app && \
    chown app:app /curves

USER app

COPY --chown=app:app . .

EXPOSE 8501
CMD ["python3", "-m" , "streamlit", "run", "streamlit_app.py"]
