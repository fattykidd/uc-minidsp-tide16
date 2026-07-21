FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY uc_minidsp_tide16 ./uc_minidsp_tide16

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "-m", "uc_minidsp_tide16.main"]
