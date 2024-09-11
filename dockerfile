FROM node:16 AS build-frontend
WORKDIR /ui
COPY /ui/package*.json ./
RUN npm install
COPY /ui ./
RUN npm run build

FROM python:3.11
WORKDIR /app
COPY /app /app
COPY --from=build-frontend /ui/build /app/static
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker", "-b", ":80","--timeout", "300", "main:app"]
