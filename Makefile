# import build config
# You can change the default build config with `make dpl="build_special.env" release`
conf ?= ci/build.env
include $(conf)
export $(shell sed 's/=.*//' $(conf))

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


release: build-nc push ## Make a release by building and pushing the `{version}` and `latest` tagged images to the registry

# GIT TASKS
git-tag: ## Tag the latest commit
	git tag -m 'Automated release' $(VERSION)

git-push: ## Push tag to the upstream
	git push origin --tags

# DOCKER TASKS
build: ## Build the image
	docker build \
		-t $(IMAGE_NAME) .

build-nc: ## Build the image without caching
	docker build --no-cache --force-rm \
		-t $(IMAGE_NAME) .

push: push-latest push-version ## Push the `{version}` and `latest` tagged images to the registry

push-latest: tag-latest ## Push the `latest` taged container to the registry
	@echo 'push latest to the Docker registry'
	docker push $(IMAGE_NAME):latest

push-version: tag-version ## Push the `{version}` taged container to the registry
	@echo 'push $(VERSION) to to the Docker registry'
	docker push $(IMAGE_NAME):$(VERSION)

tag: tag-latest tag-version ## Tag the image with the `{version}` and `latest` tags

tag-latest: ## Tag the image with the `{version}` tag
	@echo 'create tag latest'
	docker tag $(IMAGE_NAME) $(IMAGE_NAME):latest

tag-version: ## Tag the image with the `latest` tag
	@echo 'create tag $(VERSION)'
	docker tag $(IMAGE_NAME) $(IMAGE_NAME):$(VERSION)


# HELPERS
check-version:  ## Check if the chart version has been bumped
	ci/check_version.sh

version: ## Output the current version
	@echo $(VERSION)
