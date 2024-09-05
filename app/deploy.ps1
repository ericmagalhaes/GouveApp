az login
az acr login --name acrryzeprod
docker build --pull --rm -f "dockerfile" -t gouveapp:latest "."
docker push acrryzeprod.azurecr.io/samples/hello-world
docker tag gouveapp:latest acrryzeprod.azurecr.io/gouveapp:latest
docker push acrryzeprod.azurecr.io/gouveapp:latest