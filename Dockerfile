# syntax=docker/dockerfile:1
FROM python:3.12.6

WORKDIR /app

# Dependencies are installed before the source is copied, so that editing a .py
# file no longer invalidates this layer and forces the whole install again.
COPY requirements.txt .

# The cache mount keeps the downloaded wheels outside the image and between
# builds, so an interrupted download is resumed instead of started over. The
# timeout and retries are here because the link to PyPI is slow enough that
# pip's defaults give up in the middle of a wheel.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 120 --retries 10 -r requirements.txt

COPY . .

CMD ["python", "app.py"]
