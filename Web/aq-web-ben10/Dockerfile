FROM node:22-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev

RUN adduser -D -u 1001 penguinistrator

COPY index.js .
COPY flag.txt .

RUN chmod 444 flag.txt

RUN chown -R penguinistrator:penguinistrator /app

USER penguinistrator

EXPOSE 3333

CMD ["node", "index.js"]