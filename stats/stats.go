package stats

import (
	"fmt"
	"log"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/sqlite"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
	"strconv"
	"sync"
)

type SpotPrice struct {
	AvailabilityZone string
	InstanceType     string
	Product          string
	Price            float64
	Timestamp        *time.Time
}

type Stats struct {
	db     *gorm.DB
	insert chan *SpotPrice
}

func (s *Stats) LoadDB() {
	var err error

	s.db, err = gorm.Open("sqlite3", "parkingspot2.db")
	if err != nil {
		panic("failed to connect database")
	}

	s.db.LogMode(true)

	s.db.AutoMigrate(&SpotPrice{})
}

func (s *Stats) inserter() {
	for {
		s.db.Create(<-s.insert)
	}
}

func (s *Stats) DownloadPrices() {
	s.insert = make(chan *SpotPrice)
	go s.inserter()

	var wg sync.WaitGroup

	for _, region := range GetRegions() {
		wg.Add(1)

		go func(r string) {
			defer wg.Done()
			s.download(r, "", nil)
		}(region)
	}

	wg.Wait()
}

func (s *Stats) download(region string, nextToken string, params *ec2.DescribeSpotPriceHistoryInput) {
	var (
		conf = aws.NewConfig().WithRegion(region)
		svc  = ec2.New(session.New(conf))
	)

	if params == nil {
		var last *SpotPrice
		var beg time.Time

		s.db.Where(fmt.Sprintf("availability_zone like '%s%%'", region)).Order("timestamp desc").First(last)

		if last == nil {
			beg = time.Now().UTC().AddDate(0, -4, 0)
		} else {
			beg = *last.Timestamp
		}

		params = &ec2.DescribeSpotPriceHistoryInput{
			StartTime:  aws.Time(beg),
			EndTime:    aws.Time(time.Now().UTC()),
			MaxResults: aws.Int64(1000),
		}
	}

	if nextToken != "" {
		params.NextToken = aws.String(nextToken)
	}

	resp, err := svc.DescribeSpotPriceHistory(params)
	if err != nil {
		log.Println(err.Error())
		return
	}

	for _, i := range resp.SpotPriceHistory {
		f, _ := strconv.ParseFloat(*i.SpotPrice, 64)

		s.insert <- &SpotPrice{
			AvailabilityZone: *i.AvailabilityZone,
			InstanceType:     *i.InstanceType,
			Product:          *i.ProductDescription,
			Price:            f,
			Timestamp:        i.Timestamp,
		}
	}

	if *resp.NextToken != "" {
		s.download(region, *resp.NextToken, params)
	}
}
