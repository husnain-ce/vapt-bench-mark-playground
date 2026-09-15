FROM debian:latest

WORKDIR /usr/app

RUN apt-get update && apt-get install -y ca-certificates curl gnupg && rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    chmod a+r /etc/apt/keyrings/google-chrome.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get update && apt-get install -y \
      google-chrome-stable uuid \
    && rm -rf /var/lib/apt/lists/* \
    && curl -o- https://deb.nodesource.com/setup_22.x | bash \
    && apt-get install nodejs -y

COPY ./src/package.json .

COPY ./flag.txt /
RUN mv /flag.txt /flag`uuid`.txt

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /usr/app/ 
USER app

RUN npm install

COPY ./src/ .

CMD ["node","/usr/app/app.js"]