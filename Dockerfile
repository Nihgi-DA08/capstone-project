# Tóm tắt: build image chạy Dash app, cài dependency từ requirements và expose cổng 8050.
FROM python:3.10

# Tắt debug mode mặc định trong container production.
ENV DASH_DEBUG_MODE False

COPY . /app
WORKDIR /app

# Cài toàn bộ dependency cho app và notebook phân tích.
RUN set -ex && \
    pip install -r requirements.txt

EXPOSE 8050

# Gunicorn serve `server` được expose từ app.py.
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app:server"]
