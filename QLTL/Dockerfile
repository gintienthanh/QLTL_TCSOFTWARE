FROM --platform=linux/amd64 python:3.8

COPY requirements.txt /tmp/requirements.txt
# install python dependencies
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

CMD ["bash", "server-entrypoint.sh"]