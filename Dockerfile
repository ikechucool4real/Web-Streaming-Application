FROM python:3.11
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app/
ENTRYPOINT ["python"]
CMD ["app.py"]
EXPOSE 5000