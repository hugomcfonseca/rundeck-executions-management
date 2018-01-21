#!/bin/bash

echo "Build successfully done."

if [[ ${TRAVIS_PULL_REQUEST} == false ]]; then
    echo "\t- Branch: '${TRAVIS_BRANCH}'"
    echo "\t- Tag: '${TAG}'"
else
    echo 1"\t- Pull Rquest: '${TRAVIS_PULL_REQUEST}'"
fi

echo -e "Push container to Docker Hub"
docker login -u=$DOCKER_USERNAME -p=$DOCKER_PASSWORD
docker tag $REPO:$COMMIT $REPO:$TAG

if [[ ${TRAVIS_PULL_REQUEST} = false ]]; then
    docker push $REPO:$TAG
fi

if [[ "${TAG}" != "latest" ]] && [[ ${TRAVIS_PULL_REQUEST} = false ]]; then
    docker push $REPO
fi