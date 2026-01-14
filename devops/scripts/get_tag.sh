#!/bin/bash

BUILD_SOURCEBRANCH=$1
BUILD_SOURCEVERSION=$2
IS_OUTPUT=$3

if [ "$IS_OUTPUT" = true ]; then
  ID_OUTPUT=';isOutput=true'
else
  ID_OUTPUT=''
fi

if [ ${BUILD_SOURCEBRANCH:0:10} == 'refs/tags/' ]; then
  echo ''
  echo "-> Git tag [${BUILD_SOURCEBRANCH:10}] is used"
  echo "##vso[task.setvariable variable=TAG$ID_OUTPUT]${BUILD_SOURCEBRANCH:10}"
else
  echo ''
  echo "-> Git commit short hash [${BUILD_SOURCEVERSION:0:7}] is used"
  echo "##vso[task.setvariable variable=TAG$ID_OUTPUT]${BUILD_SOURCEVERSION:0:7}"
fi
