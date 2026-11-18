##
# Scout
#
# @file
# @version 0.1

.DEFAULT_GOAL := help
.PHONY: build run init prune help up down bash-scout test

# Number of parallel test workers for `make test` (pytest-xdist). WORKERS=0 runs serially.
WORKERS ?= auto

build:    ## Build new images
	docker-compose build
init:    ## Initialize scout database and load demo data
	echo "Setup a complete scout database with demo institute, panel and case"
	docker-compose run scout-cli uv run scout --host mongodb setup database --yes
	docker-compose run scout-cli uv run scout --host mongodb load panel scout/demo/panel_1.txt
	docker-compose run scout-cli uv run scout --host mongodb load case scout/demo/643594.config.yaml
up:    ## Run Scout software
	docker-compose up --detach
down:    ## Take down Scout software
	docker-compose down --volumes
bash-scout:    ## Enter bash on scout web containers
	docker-compose exec scout-web /bin/bash
test:    ## Run the tests in containers, in parallel (needs only Docker). TESTS=path for a subset, WORKERS=0 for serial
	docker compose -f docker-compose.test.yml run --rm --build test $(or $(TESTS),tests) -n $(WORKERS); status=$$?; \
	docker compose -f docker-compose.test.yml down --volumes; exit $$status
prune:    ## Remove orphans and dangling images
	docker-compose down --remove-orphans
	docker images prune
help:    ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# end
