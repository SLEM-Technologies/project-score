#!/bin/bash

BUILD_REASON=$1
BUILD_SOURCEBRANCH=$2
BUILD_SOURCEVERSION=$3
IS_OUTPUT=$4
BUILD_MANUALTAG=${5:-manual}
BUILD_BASE=${6:-false}
BASE_DIFF_FILES=$7


case $BUILD_BASE in
true) ;;
false) ;;
*)
  echo "Error: BUILD_BASE must be either 'true' or 'false'."
  exit 1
  ;;
esac

if [ "$IS_OUTPUT" = true ]; then
  ID_OUTPUT=';isOutput=true'
else
  ID_OUTPUT=''
fi

if [ -z "$(echo 'IndividualCI|BatchedCI|PullRequest' | grep ${BUILD_REASON})" ]; then
  echo ''
  echo "-> Manual tag [${BUILD_MANUALTAG}_${BUILD_SOURCEVERSION:0:7}] is used"
  echo "##vso[task.setvariable variable=TAG$ID_OUTPUT]${BUILD_MANUALTAG}_${BUILD_SOURCEVERSION:0:7}"
else
  if [ ${BUILD_SOURCEBRANCH:0:10} == 'refs/tags/' ]; then
    echo ''
    echo "-> Git tag [${BUILD_SOURCEBRANCH:10}] is used"
    echo "##vso[task.setvariable variable=TAG$ID_OUTPUT]${BUILD_SOURCEBRANCH:10}"
  else
    echo ''
    echo "-> Git commit short hash [${BUILD_SOURCEVERSION:0:7}] is used"
    echo "##vso[task.setvariable variable=TAG$ID_OUTPUT]${BUILD_SOURCEVERSION:0:7}"
  fi
fi

if [ "$BUILD_BASE" = true ]; then
  if [ -z "$BASE_DIFF_FILES" ]; then
    echo "Error: BASE_DIFF_FILES must be provided when BUILD_BASE is true."
    exit 1
  fi

  BASE_TAG=$(cat $BASE_DIFF_FILES | md5sum | cut -c1-9)
  echo "-> Base tag [$BASE_TAG]"
  echo "##vso[task.setvariable variable=BASE_TAG$ID_OUTPUT]${BASE_TAG}"
fi
