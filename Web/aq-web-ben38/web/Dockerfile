FROM node@sha256:cbe2d5f94110cea9817dd8c5809d05df49b4bd1aac5203f3594d88665ad37988

WORKDIR /app
COPY ./stuff/ /app
RUN npm ci 
RUN chmod +x /app/index.js
RUN chmod 555 /app/certs -R
RUN openssl genrsa -out ./certs/sitekey.pem 2048
RUN openssl req -subj '/CN=web' -addext 'subjectAltName=DNS:web' -new -key ./certs/sitekey.pem -out ./certs/sitecert.csr
RUN openssl x509 -req -in ./certs/sitecert.csr -copy_extensions copyall -CA ./certs/cacert.pem -CAkey ./certs/cakey.pem -out ./certs/sitecert.pem
RUN useradd -m app
USER app
ENV NODE_ENV=production
CMD ["/app/index.js"]

