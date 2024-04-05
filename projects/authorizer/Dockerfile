FROM public.ecr.aws/lambda/python:3.12

COPY pyproject.toml  ${LAMBDA_TASK_ROOT}
COPY poetry.lock ${LAMBDA_TASK_ROOT}

RUN pip install poetry && poetry config virtualenvs.create false

RUN poetry export --without-hashes -f requirements.txt > requirements.txt

RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT} --upgrade

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
