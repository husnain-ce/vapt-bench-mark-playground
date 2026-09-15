FROM golang:latest AS builder

WORKDIR /app

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o internal .

FROM alpine:latest

RUN adduser -D ctf && apk add --no-cache curl

WORKDIR /app

COPY --from=builder /app/internal .

USER ctf

EXPOSE 8080

CMD ["./internal", "ARA7{FAKE}"]