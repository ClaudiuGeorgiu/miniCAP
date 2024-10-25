FROM python:3.13-alpine

RUN adduser -D minicap
USER minicap

WORKDIR /app/

# Copy requirements and install.
COPY ./requirements.txt /app/
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Copy the needed files.
COPY . /app/

EXPOSE 8000

ENTRYPOINT ["python3", "-m", "minicap.main"]
