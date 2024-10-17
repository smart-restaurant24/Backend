FROM python:3.12.7
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN python -m spacy download en_core_web_sm

COPY ./app /code/app
COPY ./.env /code/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]