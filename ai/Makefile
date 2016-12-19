deps:
	sudo apt-get install python-pip python-dev python-psycopg2
	sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp27-none-linux_x86_64.whl
	sudo pip install redis

clean:
	-rm spot_prices.csv
	-rm insts.csv
	-rm azs.csv

spot_prices.csv:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy spot_prices to stdout delimiter ',' csv" anatma > spot_prices.csv

insts.csv:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select instance_type from instance_types) to stdout delimiter ',' csv" anatma > insts.csv

azs.csv:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select availability_zone from availability_zones) to stdout delimiter ',' csv" anatma > azs.csv

fullrun: clean
	$(MAKE) spot_prices.csv
	python split.py

smallrun:
	python main.py queue
	$(MAKE) -j25 run
