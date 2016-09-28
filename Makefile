build:
	go build

deps:
	go get -u github.com/mitchellh/gox

release: 
	./scripts/dist.sh
