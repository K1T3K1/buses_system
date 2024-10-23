FROM python:3.11.3 as base

FROM base AS builder

RUN pip install --upgrade pip
WORKDIR /lib
COPY ./libraries/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location -r requirements.txt
COPY libraries/ .
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location --no-deps .
WORKDIR /build
COPY ./shovel/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location -r requirements.txt
COPY shovel/ .
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location --no-deps .

FROM base

WORKDIR /app
COPY --from=builder /install /usr/local
CMD ["/usr/local/bin/shovel"]
