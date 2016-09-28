build:
	go build

deps:
	go get -u github.com/mitchellh/gox

release: gox

gox:
	./scripts/dist.sh
