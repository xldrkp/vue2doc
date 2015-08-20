# vue2doc

This tool converts a VUE concept map to various formats (Markdown, PDF, HTML, OPT).

## Docker Deployment - Client Side

### Create Docker repo

First of all you need to create the repo you want to push to on the Docker hub.

### Tagging the image

Before pushing the image to the Docker Hub, we need to tag it. To tag the latest image built, do the following:

```
~ $ docker tag vue:latest username/vue2doc:version
```

*version* can be something like *0.1* or such.

### Pushing the image to the Docker Hub

```
~ $ docker push username/vue2doc:version
```

## Docker Deployment - Server Side

Ssh into the server and pull the image from the Docker hub.

### Pull the image from the Docker hub

```
~ $ docker pull username/vue2doc:version
```

You should get a digest after successfully pulling the image that you need for the next step.

## Run a container

```
~ $ docker run -p 80:8000 digest
```

Finally you can open the application in the browser.
