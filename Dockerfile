FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg tini ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/
COPY .streamlit/ /app/.streamlit/

RUN mkdir -p /data/Videos /data/tmp /config

EXPOSE 8501
ENTRYPOINT ["/usr/bin/tini","--"]
CMD ["streamlit", "run", "main.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.address=0.0.0.0"]
