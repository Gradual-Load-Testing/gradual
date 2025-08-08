# 🚀 FastAPI Server - Development Guide with Docker

This FastAPI server is used for stress testing. It supports **hot reload**, logs all incoming requests to disk, and runs inside a Docker container with logs accessible on the host.

---

## 📦 Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py           # FastAPI app entrypoint
│   └── logger.py         # Logger that writes to /app/logs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── server_logs/          # Logs appear here (auto-created if missing)
```

---

## 🐳 Run the FastAPI Server

```bash
docker-compose up --build
```

This will:
- Build the Docker image.
- Start the server on `http://localhost:8000`.
- Enable **auto-reloading** on code changes inside the `app/` directory.
- Store logs in `./server_logs/api_requests.log`.

---

## 🔁 Auto-Reload for Development

The server runs with `uvicorn --reload`, so any changes inside the `app/` directory will automatically restart the server.

> Note: If you rename or add new Python modules, the server may need a manual restart.

---

## 📄 Logging

All HTTP requests are logged to:
```
./server_logs/api_requests.log
```

This is helpful for verifying server behavior during integration or stress testing.

---

## 🧪 Test Endpoints

You can test the server with:

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/data
curl -X POST http://localhost:8000/submit -H "Content-Type: application/json" -d '{"key": "value"}'
```

Logs for each request will be appended to the log file.

---

## 🧹 Clean Up

To stop and remove the container:

```bash
docker-compose down
```

To rebuild everything from scratch:

```bash
docker-compose down --volumes --rmi all
docker-compose up --build
```