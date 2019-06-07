##
#
#  Makefile for Website
#
#  https://bitbucket.org/fret/website.git
#
# Copyright 2018 Curtis Sand
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###

BUILD = $$(pwd)/build
DIST = $$(pwd)/dist
IMAGES = $$(pwd)/images
SRC = $$(pwd)/src
HTML = $(SRC)/pages
JS = $(SRC)/js
JS_DIST = $(DIST)/js
CSS = $(SRC)/css
CSS_BUILD = $(BUILD)/css
CSS_DIST = $(DIST)/css
STATIC = $(SRC)/static
STATIC_DIST = $(DIST)
NODE = $$(pwd)/website/node_modules
NODE_PKG = $$(pwd)/website/
BOOTSTRAP_SCSS = $(NODE)/bootstrap/scss
BOOTSTRAP_JS = $(NODE)/bootstrap/dist/js/bootstrap.min.js*
JQUERY_JS = $(NODE)/jquery/dist/jquery.min.js
ESLINT = $(NODE)/eslint/bin/eslint.js
PYTHON_REQUIRES = $$(pwd)/requirements.txt
PYVENV = $$(pwd)/pyvenv
LIGHTBOX_CSS = $(NODE)/lightbox2/dist/css/lightbox.min.css
LIGHTBOX_JS = $(NODE)/lightbox2/dist/js/lightbox.min.*
LIGHTBOX_IMAGES = $(NODE)/lightbox2/dist/images/*

SOURCES = $$(pwd)/sources
SOURCES_BUILD = $(BUILD)/sources
SOURCES_DIST = $(DIST)/sources

PAGES_BUILD = $(BUILD)/pages
PAGES_DIST = $(DIST)/pages

HOST = http://curtissand.com

DEPLOY_DEST = curtsan2@curtissand.com:~/www/

include website.mk

.PHONY: deploy
deploy :
	rsync -haLP --no-whole-file --inplace --exclude images $(DIST)/* $(DEPLOY_DEST)

.PHONY: deploy-images
deploy-images :
	rsync -haLP --no-whole-file --inplace $(IMAGES) $(DEPLOY_DEST)
