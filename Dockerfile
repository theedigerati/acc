FROM python:3.10-alpine
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . /code/
# COPY build.sh /code/build.sh
# RUN chmod +x /code/build.sh && /code/build.sh
RUN pip install -r requirements.txt
RUN chmod +x /code/init.sh
# CMD ["/bin/sh", "./build.sh"]
