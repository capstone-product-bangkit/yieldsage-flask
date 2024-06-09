FROM python:3.10

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "flask", "run", "--host=0.0.0.0", "--port=8000"]
