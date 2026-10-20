FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY tasks ./tasks
COPY tests ./tests

ENTRYPOINT ["rl-taskkit"]
CMD ["list", "--tasks-dir", "/app/tasks"]
