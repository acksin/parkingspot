package main

import (
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	"github.com/jinzhu/now"

	"github.com/acksin/fugue/commons"
)

type SpotPrice struct {
	Region         string
	AZ             string
	InstanceType   string
	RecommendedBid float64
	Mean           float64
	Median         float64
	StdDev         float64
	Savings        float64
	OnDemandPrice  float64
	Len            int64
}

func GetSpotHourly(w http.ResponseWriter, r *http.Request) {
	var (
		vars         = mux.Vars(r)
		az           = vars["availabilityZone"]
		instanceType = vars["instanceType"]
		a            []*SpotPrice
		isFree       = true
	)

	sub := commons.SubscriptionValue(r)
	if sub != nil && !sub.IsFree() {
		isFree = false
	}

	if (isFree && freeInstance(instanceType)) || !isFree {
		t := now.BeginningOfDay()
		for i := 1; i < 24; i++ {
			a = append(a, GetAZSpotPricing(az, instanceType, t.Add(time.Duration(i)*time.Hour)))
		}

		commons.RespondJson(w, r, a)
		return
	}

	commons.RespondJson(w, r, a)
}

func GetSpotPricing2(w http.ResponseWriter, r *http.Request) {
	var (
		vars         = mux.Vars(r)
		az           = vars["availabilityZone"]
		instanceType = vars["instanceType"]
		duration     = vars["duration"]
		isFree       = true
	)

	log.Println("Pricing for", az, instanceType)

	dur, _ := strconv.ParseInt(duration, 10, 32)
	if dur == 0 {
		dur = 1
	}

	sub := commons.SubscriptionValue(r)
	if sub != nil && !sub.IsFree() {
		isFree = false
	}

	switch {
	case isFree && freeInstance(instanceType):
		commons.RespondJson(w, r, GetAZSpotDurationPricing(az, instanceType, time.Now().UTC(), int(dur)))
		return
	case isFree && !freeInstance(instanceType):
		commons.RespondJson(w, r, nil)
		return
	default:
		// is pro
		commons.RespondJson(w, r, GetAZSpotDurationPricing(az, instanceType, time.Now().UTC(), int(dur)))
	}
}
