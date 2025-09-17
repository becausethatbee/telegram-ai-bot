#!/bin/bash

# Прекращать выполнение при возникновении ошибки
set -e

IMAGE_NAME="telegram-ai-bot"
CONTAINER_NAME="ai-bot"

# Проверка, запущен ли контейнер с таким именем, и его удаление для обеспечения идемпотентности
if [ "$(docker ps -a -q -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping and removing existing container: ${CONTAINER_NAME}"
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
fi

# Сборка образа (если требуется перед каждым запуском)
# echo "Building Docker image: ${IMAGE_NAME}"
# docker build -t ${IMAGE_NAME} .

echo "Running new container: ${CONTAINER_NAME}"
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    --env-file ./.env \
    "${IMAGE_NAME}"

echo "Container started successfully."
echo "To view logs, run: docker logs -f ${CONTAINER_NAME}"
