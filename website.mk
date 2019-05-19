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


.PHONY: help
help :
	@echo "Website Makefile"
	@echo ""
	@echo "  Targets:"
	@echo "    all : Build and compile all project components."
	@echo "    rebuild : Clean, Build and compile all project components."
	@echo "    run : Run an NGINX docker image to test the website locally."
	@echo "    clean : Clean all built files (clean-dist, clean-build)."
	@echo "    clean-all : Clean all files, including installed packages."
	@echo "    clean-build : Remove the build dir."
	@echo "    clean-dist : Remove the dist dir."
	@echo "    clean-npm : Remove the local installed npm modules."
	@echo "    clean-css : Remove any built CSS files."
	@echo "    clean-js : Remove any built Javascript files."
	@echo "    build : Make build dir."
	@echo "    dist : Make dist dir."
	@echo "    install : install NPM packages."
	@echo "    css : Run both css-compile and css-prefix."
	@echo "    css-compile : compile from SCSS to CSS using SASS."
	@echo "    css-prefix : prefix the CSS sheet using postcss autoprefixer."
	@echo "    js : Use rollup and babel to compile javascript sources."
	@echo "    jslint : Use eslint to check the javascript style."


# overall build targets

all : html css js static images
	date > all

.PHONY: rebuild
rebuild : clean all
	@echo "rebuild target"

.PHONY: run
run : all
	sudo docker run --rm -p 80:80 -v $(DIST):/usr/share/nginx/html \
		-v $(IMAGES):/usr/share/nginx/html/images nginx

# clean targets

.PHONY: clean-build
clean-build :
	rm -rf $(BUILD) css-compile css-prefix css all

.PHONY: clean-dist
clean-dist :
	rm -rf $(DIST) css-prefix css all js jqueryjs bootstrapjs \
		cssdist jsdist static imgs

.PHONY: clean-npm
clean-npm :
	rm -rf $(NODE) install

.PHONY: clean-pyvenv
clean-pyvenv :
	rm -rf $(PYVENV) install-python python-venv

.PHONY: clean-css
clean-css :
	rm -rf $(CSS_BUILD) $(CSS_DIST) css-compile css-prefix css cssdist

.PHONY: clean-js
clean-js:
	rm -rf $(JS_DIST) js bootstrapjs jqueryjs jsdist

.PHONY: clean
clean : clean-build clean-dist clean-source-links

.PHONY: clean-all
clean-all : clean clean-npm clean-pyvenv


# directory targets

build :
	mkdir $(BUILD)

dist :
	mkdir $(DIST)

jsdist : dist
	mkdir -p $(JS_DIST)
	date > jsdist

cssdist : dist
	mkdir -p $(CSS_DIST)
	date > cssdist


# install targets

.PHONY: install
install : install-npm install-py

# note: the dev dependencies have been separated into individual commands here
# to avoid maxing out my proxy server's open connection limits.
install-npm :
	npm --prefix $(NODE_PKG) install -D @babel/core
	npm --prefix $(NODE_PKG) install -D @babel/plugin-proposal-class-properties
	npm --prefix $(NODE_PKG) install -D @babel/preset-env
	npm --prefix $(NODE_PKG) install -D autoprefixer
	npm --prefix $(NODE_PKG) install -D babel-eslint
	npm --prefix $(NODE_PKG) install -D bootstrap
	npm --prefix $(NODE_PKG) install -D eslint
	npm --prefix $(NODE_PKG) install -D jquery
	npm --prefix $(NODE_PKG) install -D node-sass
	npm --prefix $(NODE_PKG) install -D popper.js
	npm --prefix $(NODE_PKG) install -D postcss-cli
	npm --prefix $(NODE_PKG) install -D rollup
	npm --prefix $(NODE_PKG) install -D rollup-plugin-babel
	npm --prefix $(NODE_PKG) install -D rollup-plugin-inject
	npm --prefix $(NODE_PKG) install -D rollup-plugin-node-resolve
	npm --prefix $(NODE_PKG) install -D stylelint
	date > install-npm

install-py : python-venv
	test -f $(PYTHON_REQUIRES) && $(PYVENV)/bin/pip install -r $(PYTHON_REQUIRES) || true
	date > install-py

python-venv :
	python3 -m venv $(PYVENV)
	date > python-venv


# html targets
html : dist
	find $(HTML) -iname "*.html" -exec rsync -haP --no-whole-file --inplace '{}' $(DIST)/ ';'

static : dist cssdist jsdist
	test -d $(STATIC) && rsync -haP --no-whole-file --inplace $(STATIC)/* $(STATIC_DIST)/ || true
	date > static

images : dist link-sources
	test -d $(IMAGES) && rsync -haP --no-whole-file --inplace $(IMAGES) $(DIST) || true
	date > imgs

# css targets

css-compile : build
	for stylesheet in $$(find $(CSS) -iname "*.scss"); do npx --prefix $(NODE_PKG) node-sass --include-path $(BOOTSTRAP_SCSS) $$stylesheet -o $(CSS_BUILD); done
	date > css-compile

css-prefix : dist cssdist css-compile
	npx --prefix $(NODE_PKG) postcss --use autoprefixer --dir $(CSS_DIST) $(CSS_BUILD)
	date > css-prefix

css : css-compile css-prefix
	date > css


# js targets

bootstrap : jsdist
	cp $(BOOTSTRAP_JS) $(JS_DIST)
	date > bootstrapjs

jquery : jsdist
	cp $(JQUERY_JS) $(JS_DIST)
	date > jqueryjs

js : jsdist bootstrap jquery
	npx --prefix $(NODE_PKG) rollup -c
	date > js

.PHONY: jslint
jslint :
	$(ESLINT) $(JS)/*


# custom targets added for curtissand.com

link-sources :
	./bin/source_links.py -v
	date > link-sources

.PHONY: clean-source-links
clean-source-links :
	./bin/source_links.py -v --remove
	rm -f link-sources

build-sources: build link-sources
	mkdir $(SOURCES_BUILD)
	rsync -haLP --exclude "*.txt" $(SOURCES)/* $(SOURCES_BUILD)
	date > build-sources
