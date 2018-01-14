#!/bin/bash

set -e

if [[ ${TRAVIS_PULL_REQUEST} = false ]] && [[ $TRAVIS_BRANCH == "master-docker" ]]; then
  TAG=${TRAVIS_TAG:-"latest"}
else
  TAG=${TRAVIS_PULL_REQUEST_BRANCH}
fi

export ${TAG}