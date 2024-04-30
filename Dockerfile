FROM python:3.12
WORKDIR /EventApi
COPY . .
RUN pip install -r requirements.txt
CMD ["flask", "run", "--host=0.0.0.0", "-p", "5000"]
EXPOSE 5000