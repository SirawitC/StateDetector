FROM python:3.8.5-slim

ENV OPENCV_VERSION="4.5.2.54"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        python3-opencv \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -qq autoremove \
    && apt-get -qq clean


WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD [ "python3", "app.py"]
