package stats

import (
	"encoding/csv"
	"fmt"
	"github.com/gonum/stat"
	"os"
	"strconv"
	"strings"
	"text/tabwriter"
)

type SpotMeRequest struct {
	Region    string
	MaxBid    float64
	MinCPU    int
	MinMemory float64

	PricingAlgo string
}

type InstanceInfo struct {
	Region        string
	Type          string
	CPU           int
	Memory        float64
	OnDemandPrice float64
}

func (r *SpotMeRequest) Filter() (ii []InstanceInfo) {
	r2 := csv.NewReader(strings.NewReader(instanceTypeCsv))
	records, err := r2.ReadAll()
	if err != nil {
		_ = err
	}

	for _, i := range records {
		cpu, _ := strconv.Atoi(i[2])
		memory, _ := strconv.ParseFloat(i[2], 64)
		ondemandPrice, _ := strconv.ParseFloat(i[5], 64)

		if (i[0] == r.Region || r.Region == "") && (r.MinCPU <= cpu || r.MinCPU == -1) && (r.MinMemory <= memory || r.MinMemory == -1) {
			ii = append(ii, InstanceInfo{
				Region:        i[0],
				Type:          i[1],
				CPU:           cpu,
				Memory:        memory,
				OnDemandPrice: ondemandPrice,
			})
		}
	}

	return
}

func (s *Stats) SpotMe(r SpotMeRequest) {
	instanceInfo := r.Filter()

	var regions []string
	var instanceTypes []string
	for _, i := range instanceInfo {
		regions = append(regions, fmt.Sprintf("availability_zone like '%s%%'", i.Region))
		instanceTypes = append(instanceTypes, i.Type)
	}

	var sp []SpotPrice
	s.db.Where(strings.Join(regions, " or ")).Where("instance_type in (?)", instanceTypes).Where("product = ?", "Linux/UNIX").Find(&sp)

	type spot struct {
		ondemand float64
		prices   []float64
	}
	prices := make(map[string]*spot)
	for _, i := range sp {
		region := i.AvailabilityZone[0 : len(i.AvailabilityZone)-1]
		if _, ok := prices[region+"/"+i.InstanceType]; !ok {
			prices[region+"/"+i.InstanceType] = &spot{}
		}

		prices[region+"/"+i.InstanceType].prices = append(prices[region+"/"+i.InstanceType].prices, i.Price)

		for _, j := range instanceInfo {
			if j.Region == region && i.InstanceType == j.Type {
				prices[region+"/"+i.InstanceType].ondemand = j.OnDemandPrice
			}
		}

	}

	w := tabwriter.NewWriter(os.Stdout, 0, 0, 5, ' ', tabwriter.TabIndent)
	fmt.Fprintf(w, "Instance\tMean\tStdDev\tOnDemand\tRecommendedBid\tSavings\t\n")

	for k, v := range prices {
		mean, std := stat.MeanStdDev(v.prices, nil)

		if (mean+std) <= r.MaxBid || r.MaxBid == -1 {
			fmt.Fprintf(w, "%s\t%f\t%f\t%f\t%f\t%2.0f%%\t\n", k, mean, std, v.ondemand, mean+std, (v.ondemand-(mean+std))/v.ondemand*100)
		}
	}
	w.Flush()
}

// func (s *SpotMeRequest) instWithMinMemory(i []string) (a []string) {
// 	for _, instType := range i {
// 		if instanceMatrix[instType].Memory >= s.MinMemory {
// 			a = append(a, instType)
// 		}
// 	}

// 	return
// }

// func (s *SpotMeRequest) instWithMinCPU(i []string) (a []string) {
// 	for _, instType := range i {
// 		if instanceMatrix[instType].VCPU >= s.MinCPU {
// 			a = append(a, instType)
// 		}
// 	}

// 	return
// }

// func (s *SpotMeRequest) regionToAZs() (azs []string) {
// 	// Find all regions that can be called upon.
// 	if s.Region == "" {
// 		return AllAZs()
// 	}

// 	for _, az := range AZs(s.Region) {
// 		azs = append(azs, az)
// 	}

// 	return
// }
