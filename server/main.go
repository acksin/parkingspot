package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"

	"github.com/acksin/fugue/commons"
	"github.com/acksin/fugue/config"
	// "github.com/acksin/gameasure"

	"github.com/patrickmn/go-cache"
)

var (
	Config *config.Config

	c *cache.Cache
)

func router() *mux.Router {
	r := mux.NewRouter()

	r.HandleFunc("/v1/instance_types", GetInstanceTypesHandler).Methods("GET")
	r.HandleFunc("/v1/availability_zones", GetAZsHandler).Methods("GET")

	r.Handle("/v1/spot/me", commons.AuthMiddleware(commons.SubscriptionMiddleware((http.HandlerFunc(SpotMeHandler))))).Methods("POST")
	r.Handle("/v1/spot/hourly/{availabilityZone}/{instanceType}", commons.AuthMiddleware(commons.SubscriptionMiddleware(http.HandlerFunc(GetSpotHourly)))).Methods("GET")
	r.Handle("/v1/spot/{availabilityZone}/{instanceType}/{duration}", commons.AuthMiddleware(commons.SubscriptionMiddleware(http.HandlerFunc(GetSpotPricing2)))).Methods("GET")

	return r
}

func main() {
	Config = config.NewConfig(os.Getenv("ACKSIN_ENV"), config.ParkingSpotApp)
	commons.Setup(Config)

	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "worker":
			Config.ParkingSpotDataDB()
			go downloadWriter()

			for {
				for _, region := range getRegions() {
					go GetDownloadPricing(region, 3, "")
				}
				<-time.After(time.Hour)
			}
		}
	}

	c = cache.New(60*time.Minute, 60*time.Second)

	r := commons.CommonRouter(router())
	log.Fatal(http.ListenAndServe(":8081", r))
}
