FROM python:3-alpine
ENV PYTHONUNBUFFERED=1
RUN date
RUN apk --no-cache upgrade
RUN apk add --no-cache python3-dev libffi-dev openssl-dev make automake gcc build-base tzdata
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev
WORKDIR /app
ADD https://raw.githubusercontent.com/eficode/wait-for/master/wait-for .
RUN chmod +x ./wait-for
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apk add git
RUN git clone https://github.com/networktocode/ntc-templates.git
ENV NET_TEXTFSM ./ntc-templates/templates
ADD . .
CMD ["./wait-for", "redis:6379", "--", "python", "cisco_config.py"]
