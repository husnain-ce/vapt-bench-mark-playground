package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

func main() {
	host, port := "0.0.0.0", "8080"

	rdb := redis.NewClient(&redis.Options{
		Addr:     "redis:6379",
		Password: "",
		DB:       0,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		data := map[string]string{
			"message": "oke",
		}

		if err := json.NewEncoder(w).Encode(data); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
	})

	mux.HandleFunc("/healthcheck", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		check := r.URL.Query().Get("check")
		if check == "" {
			w.WriteHeader(http.StatusOK)
			data := map[string]string{
				"healthy": "ok",
			}

			if err := json.NewEncoder(w).Encode(data); err != nil {
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
				return
			}
			return
		}

		status, err := CurlStatus(check)
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to run curl: %v", err), http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusOK)
		data := map[string]string{
			"status": status,
		}
		if err := json.NewEncoder(w).Encode(data); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
	})

	mux.HandleFunc("/debug", func(w http.ResponseWriter, r *http.Request) {
		host := r.Host
		parts := strings.Split(host, ":")
		if len(parts) > 1 {
			host = parts[0]
		}

		if host != "localhost" && host != "127.0.0.1" {
			http.Error(w, "Forbidden", http.StatusForbidden)
			return
		}

		otp := r.URL.Query().Get("otp")
		cmd := r.URL.Query().Get("cmd")
		if otp == "" {
			http.Error(w, "OTP is required", http.StatusBadRequest)
			return
		}

		ctx := r.Context()

		exists, err := rdb.Exists(ctx, otp).Result()
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to check OTP: %v", err), http.StatusInternalServerError)
			return
		}
		if exists == 0 {
			http.Error(w, "OTP not found", http.StatusNotFound)
			return
		}

		if err := rdb.Del(ctx, otp).Err(); err != nil {
			http.Error(w, fmt.Sprintf("Failed to delete OTP: %v", err), http.StatusInternalServerError)
			return
		}

		if cmd == "" {
			http.Error(w, "Command is required", http.StatusBadRequest)
			return
		}

		cmdExec := exec.CommandContext(ctx, "sh", "-c", cmd)

		if err := cmdExec.Run(); err != nil {
			http.Error(w, fmt.Sprintf("Failed to run command: %v", err), http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusOK)
		data := map[string]string{
			"message": "Command executed successfully",
		}

		if err := json.NewEncoder(w).Encode(data); err != nil {
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			return
		}
	})

	err := http.ListenAndServe(fmt.Sprintf("%s:%s", host, port), mux)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func CurlStatus(url string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url)

	output, err := cmd.Output()
	if ctx.Err() == context.DeadlineExceeded {
		return "", fmt.Errorf("curl timed out")
	}
	if err != nil {
		return "", fmt.Errorf("failed to run curl: %v", err)
	}

	return string(output), nil
}
