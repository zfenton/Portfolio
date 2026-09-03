FROM python:3.11-slim-buster
ARG APP_DIR=/inference

RUN apt-get update && apt-get install -y python3-venv && rm -rf /var/lib/apt/lists/*

WORKDIR ${APP_DIR}

RUN python3 -m venv /venv

ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

COPY inference.py ./
##COPY /data ./

ENTRYPOINT ["python", "inference.py"]

