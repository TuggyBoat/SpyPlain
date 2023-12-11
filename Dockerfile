FROM python:3.10-slim-buster
RUN apt-get update && apt-get install -y git
RUN pip3 install -U git+https://github.com/Rapptz/discord.py
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
COPY setup.py .
COPY README.md .
COPY ptn ptn
RUN pip3 install .
RUN mkdir /root/spyplane
RUN ln -s /root/spyplane/.env /root/.env
WORKDIR /root/spyplane
ENTRYPOINT ["/usr/local/bin/spyplane"]