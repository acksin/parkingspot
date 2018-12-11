dev-deps:
	sudo apt-get install -y s3cmd
	npm install babel-cli babel-preset-es2015 babel-preset-react

jswatch:
	mkdir -p website/javascripts/build/
	babel website/javascripts/src --watch --out-file website/javascripts/build/acksin.js

download_sample:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select availability_zone, extract(dow from timestamp) as day,extract(hour from timestamp) as hour, instance_type, spot_price::money::numeric::float8 from spot_prices  tablesample system (10) where product_description = 'Linux/UNIX' limit 100000) to stdout delimiter ',' csv" anatma > training_data.csv
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select availability_zone, extract(dow from timestamp) as day,extract(hour from timestamp) as hour, instance_type, spot_price::money::numeric::float8 from spot_prices tablesample system (1) where product_description = 'Linux/UNIX' limit 10000) to stdout delimiter ',' csv" anatma > test_data.csv

docs:
	echo "none"

js:
	babel website/javascripts/src --out-file website/javascripts/build/acksin.js

release: docs js
	go build
	docker build -t acksin/parkingspot .
