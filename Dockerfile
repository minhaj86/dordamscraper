FROM python:3.7

RUN pip install requests

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt


# RUN apk add gcc

# RUN apk add linux-headers
# RUN apk add libc-dev

# RUN apk add libxml2
# RUN apk add libxml2-dev
# RUN apk add libxslt
# RUN apk add libxslt-dev



COPY scripts /scripts
WORKDIR /scripts

CMD  ["python" , "daraz.py"]
