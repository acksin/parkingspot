package main

import (
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
	"github.com/aws/aws-sdk-go/service/s3"

	"github.com/jinzhu/now"
	"github.com/patrickmn/go-cache"
)

// {
//   AvailabilityZone: "us-west-2a",
//   InstanceType: "m3.2xlarge",
//   ProductDescription: "Linux/UNIX",
//   SpotPrice: "0.080400",
//   Timestamp: 2016-05-26 03:05:06 +0000 UTC
// }

/*

create table spot_prices (
availability_zone varchar(20),
instance_type varchar(20),
product_description varchar(20),
spot_price money,
timestamp timestamp
);

create index availability_zone_idx on spot_prices (availability_zone);
create index instance_type_idx on spot_prices (instance_type);
create index timestamp_idx on spot_prices (timestamp);
create index product_description_idx on spot_prices (product_description);

create materialized view instance_types as select distinct instance_type from spot_prices;
refresh materialized view instance_types;

create materialized view availability_zones as select distinct availability_zone from spot_prices;
refresh materialized view availaiblity_zones;

*/

func getRegions() (a []string) {
	sess, err := session.NewSession()
	if err != nil {
		fmt.Println("failed to create session,", err)
		return
	}

	svc := ec2.New(sess)

	resp, err := svc.DescribeRegions(&ec2.DescribeRegionsInput{})
	if err != nil {
		// Print the error, cast err to awserr.Error to get the Code and
		// Message from an error.
		fmt.Println(err.Error())
		return
	}

	// Pretty-print the response data.
	for _, i := range resp.Regions {
		a = append(a, *i.RegionName)
	}

	return a
}

var (
	insertChan chan []*ec2.SpotPrice
)

func init() {
	insertChan = make(chan []*ec2.SpotPrice)
}

func downloadWriter() {
	for {
		spotPriceHistory := <-insertChan

		log.Println("writing to db")

		for _, i := range spotPriceHistory {
			_, err := Config.ParkingSpotDataDB().Exec("INSERT INTO spot_prices (availability_zone, instance_type, product_description, spot_price, timestamp) select $1, $2, $3, $4, $5 WHERE NOT EXISTS (SELECT 1 FROM spot_prices WHERE availability_zone = $6 and instance_type = $7 and product_description = $8 and spot_price = $9 and timestamp = $10);", i.AvailabilityZone, i.InstanceType, i.ProductDescription, i.SpotPrice, i.Timestamp, i.AvailabilityZone, i.InstanceType, i.ProductDescription, i.SpotPrice, i.Timestamp)
			if err != nil {
				fmt.Println("err", err)
			} else {
				fmt.Println("Written")
			}
		}
		fmt.Println("stuck")
	}
}

func GetDownloadPricing(region string, o int, nextToken string) {
	n := now.New(time.Now().UTC())
	beg := n.BeginningOfDay().AddDate(0, 0, -o)
	end := n.EndOfDay().AddDate(0, 0, -o)

	for {
		fmt.Println("day", o, "token", nextToken, region)

		conf := aws.NewConfig().WithCredentials(credentials.NewStaticCredentials("AKIAJW5I32K2JDA353DA", "QVfXxvaRogsL4DKgxGM1PKtmV95w0D4+Muihn+qe", "")).WithRegion(region)
		svc := ec2.New(session.New(conf))

		params := &ec2.DescribeSpotPriceHistoryInput{
			StartTime:  aws.Time(beg),
			EndTime:    aws.Time(end),
			MaxResults: aws.Int64(1000),
		}

		if nextToken != "" {
			params.NextToken = aws.String(nextToken)
		}

		resp, err := svc.DescribeSpotPriceHistory(params)
		if err != nil {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
			return
		}

		insertChan <- resp.SpotPriceHistory

		if *resp.NextToken != "" {
			fmt.Println("nexttoken", nextToken)
			GetDownloadPricing(region, o, *resp.NextToken)
		} else {
			break
		}

	}
}

func GetAZSpotDurationPricing(az, instance string, t time.Time, duration int) (cur *SpotPrice) {
	for i := 0; i < int(duration); i++ {
		var (
			t    = time.Now().UTC().Add(time.Duration(i) * time.Hour)
			inst = GetAZSpotPricing(az, instance, t)
		)

		if inst != nil {
			if cur == nil {
				cur = inst
			}

			if inst.RecommendedBid > cur.RecommendedBid {
				cur = inst
			}
		}
	}

	return cur
}

func GetAZSpotPricing(az, instance string, t time.Time) (a *SpotPrice) {
	var (
		weekday = int(t.Weekday())
		hour    = int(t.Hour())
	)

	a = &SpotPrice{}
	a.Region = az[0 : len(az)-1]
	a.AZ = az
	a.InstanceType = instance

	key := filepath.Join(az, instance, "linux", fmt.Sprintf("%d", weekday), fmt.Sprintf("%d", hour), "stats.json")

	cached, found := c.Get(key)
	if found {
		log.Println(key, "Cache")
		return cached.(*SpotPrice)
	} else {
		params := &s3.GetObjectInput{
			Bucket: aws.String(Config.ParkingSpot.S3Bucket),
			Key:    aws.String(key),
		}

		resp, err := Config.S3().GetObject(params)
		if err != nil {
			log.Println(key, err.Error())
			return nil
		}

		err = json.NewDecoder(resp.Body).Decode(a)
		if err != nil {
			log.Println(key, err)
			return nil
		}

		c.Set(key, a, cache.DefaultExpiration)
	}

	return a
}
