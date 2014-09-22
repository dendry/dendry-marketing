#!/bin/sh

ICO_SIZES := 64 48 32 16
SIZES := 256 152 120 76 64 60 48

WEB_DIR := ../website/dendry.org
IMG_DIR := ${WEB_DIR}/img
LOGOS := ${foreach SIZE, ${SIZES}, ${IMG_DIR}/logo_${SIZE}.png}
FAVICON := ${WEB_DIR}/favicon.ico
FAV_SRC := ${foreach SIZE, ${ICO_SIZES}, /tmp/logo_${SIZE}.png}

FULL_SIZE := logo_1024.png
SRC := logo.svg

all: ${FULL_SIZE} ${LOGOS} ${FAVICON}

${FULL_SIZE}: ${SRC}
	convert -background none $^ $@

/tmp/logo_%.png: ${FULL_SIZE}
	convert $^ -thumbnail $*x$* $@

${IMG_DIR}/logo_%.png: ${FULL_SIZE}
	mkdir -p ${IMG_DIR}
	convert $^ -thumbnail $*x$* $@

${FAVICON}: ${FAV_SRC}
	convert $^ $@
