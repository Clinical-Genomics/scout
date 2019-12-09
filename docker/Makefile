build:
	@docker build -t scout:latest ../
	@docker build -t scout-setup:v1.0 scout-setup/
	@docker build -t scout-import:v1.0 scout-import/
	@docker build -t scout-remove:v1.0 scout-remove/
	@docker build -t scout-adduser:v1.0 scout-adduser/
	@docker build -t scout-removeuser:v1.0 scout-removeuser/


setup:
	@docker-compose run --rm scout-setup


run:
	@docker-compose up -d scout

stop:
	@docker-compose down
