build:
	-rm stats/instance_types.go stats/instance_types.json
	make stats/instance_types.go
	go build

deps:
	go get -u github.com/mitchellh/gox

release: 
	./scripts/dist.sh

stats/instance_types.go: stats/instanceTypes.js
	cat stats/instanceTypes.js | sed '1,5 d' | sed 's/callback(//' | sed 's/);//' | ruby -rjson -e "a=eval STDIN.read; puts a.to_json" | jq '.' >> stats/instance_types.json
	ruby scripts/instgen.rb stats/instance_types.json > stats/instance_types.go

stats/instanceTypes.js:
	wget -O stats/instanceTypes.js http://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js
