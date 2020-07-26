### Run container   
```
docker run -d --name cusg-b \
    -p 8088:80 \
    -e GUNICORN_WORKERS=3 \
    -e CUSG_SECRET=topsecret \
    -e CUSG_DB_CONNETION_STRING=postgresql://postgres:pgpassword@pgserver:5432/cusg
    critical-usg-backend:latest
```
