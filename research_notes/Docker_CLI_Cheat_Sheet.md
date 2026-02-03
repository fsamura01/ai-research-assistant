# Docker CLI Cheat Sheet

Date: 2026-02-01

Build an Image from a Dockerfile: docker build -t <image_name> .
Build an Image from a Dockerfile without the cache: docker build -t <image_name> . --no-cache
List local images: docker images
Delete an Image: docker rmi <image_name>
Remove all unused images: docker image prune
Login into Docker: docker login -u <username>
publish an image to Docker Hub: docker push <username>/<image_name>
Search Hub for an image: docker search <image_name>
Pull an image from a Docker Hub: docker pull <image_name>
Create and run a container: docker run <image_name>