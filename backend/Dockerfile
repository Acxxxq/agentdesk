FROM python:3.12-slim AS dependencies
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY pyproject.toml /app/pyproject.toml
# Install dependencies before copying source so edits do not redownload packages.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import tomllib; p=tomllib.load(open('pyproject.toml','rb')); print('\n'.join(p['project']['dependencies'] + p['project']['optional-dependencies']['infrastructure'] + p['build-system']['requires']))" > /tmp/runtime-requirements.txt \
    && pip install -r /tmp/runtime-requirements.txt

FROM dependencies AS development-dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import tomllib; p=tomllib.load(open('pyproject.toml','rb')); print('\n'.join(p['project']['optional-dependencies']['dev']))" > /tmp/dev-requirements.txt \
    && pip install -r /tmp/dev-requirements.txt 'editables>=0.5,<1'

FROM dependencies AS runtime
COPY README.md /app/README.md
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
RUN pip install --no-deps --no-build-isolation .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "agentorbis.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM development-dependencies AS development
COPY README.md /app/README.md
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY tests /app/tests
RUN pip install --no-deps --no-build-isolation -e .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "agentorbis.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
