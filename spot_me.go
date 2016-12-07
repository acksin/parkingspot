package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/acksin/fugue/commons"
)

type SpotMeRequest struct {
	Region    string
	MaxBid    float64
	MinCPU    int
	MinMemory float64
	Duration  int

	isFree bool
}

func SpotMeHandler(w http.ResponseWriter, r *http.Request) {
	var (
		s SpotMeRequest
	)

	decoder := json.NewDecoder(r.Body)
	err := decoder.Decode(&s)
	if err != nil {
		log.Println("meh", err)
	}

	sub := commons.SubscriptionValue(r)
	if sub == nil || sub.IsFree() {
		s.isFree = true
	}

	// log.Printf("Spot Me Criteria %#v", sub)

	go commons.NewEvent(commons.Event{
		//Username:    commons.UsernameValue(r),
		Type:        commons.UXEventType,
		Action:      commons.APIUsageActionType,
		Description: fmt.Sprintf("%s %#v", r.URL.Path, s),
	})

	commons.RespondJson(w, r, s.GetRecommendation())
}

func (s *SpotMeRequest) instWithMinMemory(i []string) (a []string) {
	for _, instType := range i {
		if instanceMatrix[instType].Memory >= s.MinMemory {
			a = append(a, instType)
		}
	}

	return
}

func (s *SpotMeRequest) instWithMinCPU(i []string) (a []string) {
	for _, instType := range i {
		if instanceMatrix[instType].VCPU >= s.MinCPU {
			a = append(a, instType)
		}
	}

	return
}

func (s *SpotMeRequest) planInstances() (i []string) {
	if s.isFree {
		return previousGenInsts()
	}

	for instType, _ := range instanceMatrix {
		i = append(i, instType)
	}

	return
}

func (s *SpotMeRequest) regionToAZs() (azs []string) {
	// Find all regions that can be called upon.
	if s.Region == "" {
		return AllAZs()
	}

	for _, az := range AZs(s.Region) {
		azs = append(azs, az)
	}

	return
}

// Find all the instances and also their price points
func (s *SpotMeRequest) GetRecommendation() *SpotPrice {
	instanceTypes := s.planInstances()
	instanceTypes = s.instWithMinMemory(instanceTypes)
	instanceTypes = s.instWithMinCPU(instanceTypes)

	var (
		azs = s.regionToAZs()
		c   = make(chan *SpotPrice)
		i   = 0
	)

	for _, instanceType := range instanceTypes {
		for _, az := range azs {
			go func(s chan *SpotPrice, i, a string, duration int) {
				s <- GetAZSpotDurationPricing(a, i, time.Now().UTC(), duration)
			}(c, instanceType, az, s.Duration)

			i++
		}
	}

	var (
		instances []*SpotPrice
	)
	// Remove all instances that go past the maxbid
	for j := 0; j < i; j++ {
		out := <-c

		if out != nil && out.Len > 0 {
			if out.RecommendedBid <= s.MaxBid {
				instances = append(instances, out)
			}
		}
	}

	log.Println("All instances", instances)

	if len(instances) > 0 {
		return instances[0]
	}

	return nil
}
