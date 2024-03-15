FROM python:3.11.3 as base

FROM base AS builder


WORKDIR /lib
COPY ./libraries/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location -r requirements.txt
COPY libraries/ .
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location --no-deps .
WORKDIR /build
COPY ./scraper/requirements.txt requirements.txt
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location -r requirements.txt
COPY scraper/ .
RUN pip install --no-cache-dir --prefix /install --no-warn-script-location --no-deps .

FROM base

WORKDIR /app
COPY --from=builder /install /usr/local
CMD ["/usr/local/bin/scraper"]
