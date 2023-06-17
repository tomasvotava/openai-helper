FROM python:3.10-slim

WORKDIR /code

ADD . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

RUN pip install --no-dependencies --no-cache-dir -r requirements.txt

CMD ["python", "-um", "openai_helper.main"]