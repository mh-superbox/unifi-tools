FROM python:3.8-alpine AS build
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/unifi-tools

COPY setup.cfg .
COPY setup.py .
COPY src/ src

RUN pip install virtualenv
RUN python -m virtualenv /.venv
ENV PATH="/.venv/bin:$PATH"

RUN python setup.py install

FROM python:3.8-alpine AS runner
ENV PATH="/.venv/bin:$PATH"

COPY --from=build /.venv /.venv

CMD ["unifi-tools"]
