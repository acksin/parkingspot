package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

var url = "https://api.parkingspot.bid/v1/spot/me"

type SpotMeRequest struct {
	Region    string
	MaxBid    float64
	MinCPU    int
	MinMemory float64
	Duration  int

	apiKey string
}

type SpotMeResponse struct {
	AZ             string
	Region         string
	RecommendedBid float64
	InstanceType   string
}

func main() {
	c := &SpotMeRequest{}

	flag.StringVar(&c.Region, "region", "", "What region do you want the machines from. If empty will get the lowest priced machine")
	flag.StringVar(&c.apiKey, "api-key", os.Getenv("PARKINGSPOT_API_KEY"), "Set the ParkingSpot API Key. If not set it will look at PARKINGSPOT_API_KEY environment variable.")
	flag.Float64Var(&c.MaxBid, "max-bid", 0.10, "Set the maximum amount you want to bid.")
	flag.IntVar(&c.MinCPU, "cpu", 1, "Set the minimum number of CPU cores you want.")
	flag.Float64Var(&c.MinMemory, "memory", 0.5, "Set the minimum number of memory you want in GB.")
	flag.IntVar(&c.Duration, "duration", 2, "Max duration of time that this machie is going to run. Set it to -1 if it is to run forever.")

	flag.Parse()

	b, err := json.Marshal(c)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(b))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-PARKINGSPOT-API-KEY", c.apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	// if resp.StatusCode == 200 {
	fmt.Println(string(body))
	//}
}
