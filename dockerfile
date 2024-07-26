FROM python:3.12-slim

WORKDIR /app

COPY src/ ./src/

WORKDIR /app/src

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py", "-c", "/benz_finder/benz_finder.yaml", "-l", "/benz_finder/benz_finder.log", "-d", "/benz_finder/benz_finder.db"]