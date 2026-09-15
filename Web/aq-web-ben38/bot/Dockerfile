FROM node@sha256:cbe2d5f94110cea9817dd8c5809d05df49b4bd1aac5203f3594d88665ad37988

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release xdg-utils wget libu2f-udev libvulkan1 p11-kit
WORKDIR /tmp
RUN wget https://download-installer.cdn.mozilla.net/pub/firefox/nightly/latest-mozilla-central/firefox-132.0a1.en-US.linux-x86_64.tar.bz2 
RUN tar xf firefox*
RUN mv firefox /opt/
RUN ln -s /opt/firefox/firefox /usr/bin/firefox
RUN cp /usr/lib/x86_64-linux-gnu/pkcs11/p11-kit-trust.so /opt/firefox/libnssckbi.so
WORKDIR /app
COPY ./stuff/ca/cacert.pem /usr/local/share/ca-certificates/cacert.crt
COPY ./stuff/ /app/
RUN update-ca-certificates
RUN PUPPETEER_SKIP_DOWNLOAD=1 PUPPETEER_PRODUCT=firefox npm ci
RUN chmod +x /app/index.js
CMD NODE_ENV=production /app/index.js
