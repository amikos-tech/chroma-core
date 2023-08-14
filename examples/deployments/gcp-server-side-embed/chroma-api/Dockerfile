FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./main.py /app/main.py
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \

