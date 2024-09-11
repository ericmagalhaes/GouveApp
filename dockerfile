FROM node:16 AS build-frontend
WORKDIR /ui
COPY /ui/package*.json ./
RUN npm install
COPY /ui ./
ENV REACT_APP_API_URL=https://gouveapp-avgcgnh0e7gkbgfb.westus2-01.azurewebsites.net
ENV REACT_APP_LOCALE=pt-BR
ENV REACT_APP_KEYWORD_TRIGGER="Fale sobre"
RUN npm run build

FROM python:3.11
WORKDIR /app
COPY /app /app
COPY --from=build-frontend /ui/build /app/static
COPY --from=build-frontend /ui/build/static /app/static
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker", "-b", ":80","--timeout", "300", "main:app"]
