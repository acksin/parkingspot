deps:
	sudo apt-get install python-pip python-dev python-psycopg2
	sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-0.8.0-cp27-none-linux_x86_64.whl
	sudo pip install redis

update_cache:
	# psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy spot_prices to stdout delimiter ',' csv" anatma > spot_prices.csv
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select * from spot_prices where timestamp > now() - interval '2 week') to stdout delimiter ',' csv" anatma > spot_prices2.csv

update_cache2:
	# psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy spot_prices to stdout delimiter ',' csv" anatma > spot_prices.csv
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select * from spot_prices where timestamp > now() - interval '3 day') to stdout delimiter ',' csv" anatma > spot_prices.csv

diff_prices:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy (select * from spot_prices where timestamp > timestamp '2016-06-24 18:29:10') to stdout delimiter ',' csv" anatma > spot_prices_diff.csv

clean:
	-rm spot_prices.csv
	-rm -rf spot_prices_split
	-rm -rf spot_prices_split_daily

spot_prices.csv:
	psql -h acksin.cbjkmgtzlru8.us-west-2.rds.amazonaws.com -U acksin -c "copy spot_prices to stdout delimiter ',' csv" anatma > spot_prices.csv

fullrun: clean
	$(MAKE) spot_prices.csv
	python split.py

smallrun:
	python main.py queue
	$(MAKE) -j25 run
