package main

import (
	"net/http"

	"github.com/acksin/fugue/commons"
)

type InstanceInfo struct {
	VCPU                  int
	Memory                float64
	Storage               string
	NetworkingPerformance string
	PhysicalProcessor     string
	ClockSpeed            string
	IntelAVX              string
	IntelAVX2             string
	IntelTurbo            string
	EBSOPT                string
	EnhancedNetworking    string
}

var (
	instanceMatrix map[string]InstanceInfo
)

func freeInstance(inst string) bool {
	for _, j := range previousGenInsts() {
		if j == inst {
			return true
		}
	}

	return false
}

func previousGenInsts() []string {
	return []string{
		"c1.medium",
		"c1.xlarge",
		"cc2.8xlarge",
		"cg1.4xlarge",
		"cr1.8xlarge",
		"hi1.4xlarge",
		"m1.large",
		"m1.medium",
		"m1.small",
		"m1.xlarge",
		"m2.2xlarge",
		"m2.4xlarge",
		"m2.xlarge",
		"m3.2xlarge",
		"m3.large",
		"m3.medium",
		"m3.xlarge",
		"c3.2xlarge",
		"c3.4xlarge",
		"c3.8xlarge",
		"c3.large",
		"c3.xlarge",
		"t1.micro",
	}
}

func init() {
	instanceMatrix = map[string]InstanceInfo{
		"t2.nano":     {1, 0.5, "EBS Only", "Low", "Intel Xeon family", "up to 3.3", "Yes", "-", "Yes", "-", "-"},
		"t2.micro":    {1, 1, "EBS Only", "Low to Moderate", "Intel Xeon family", "Up to 3.3 ", "Yes", "-", "Yes", "-", "-"},
		"t2.small":    {1, 2, "EBS Only ", "Low to Moderate ", "Intel Xeon family ", "Up to 3.3", "Yes ", "- ", "Yes ", "- ", "- "},
		"t2.medium":   {2, 4, "EBS Only", "Low to Moderate", "Intel Xeon family ", "Up to 3.3", "Yes ", "- ", "Yes ", "- ", "- "},
		"t2.large":    {2, 8, "EBS Only", "Low to Moderate", "Intel Xeon family ", "Up to 3.0 ", "Yes ", "- ", "Yes ", "- ", "- "},
		"m4.large":    {2, 8, "EBS Only ", "Moderate", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"m4.xlarge":   {4, 16, "EBS Only", "High", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"m4.2xlarge":  {8, 32, "EBS Only", "High", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"m4.4xlarge":  {16, 64, "EBS Only", "High", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"m4.10xlarge": {40, 160, "EBS Only", "10 Gigabit ", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"m3.medium":   {1, 3.75, "1 x 4 SSD", "Moderate", "Intel Xeon E5-2670 v2*", "2.5", "Yes", "-", "Yes", "-", "-"},
		"m3.large":    {2, 7.5, "1 x 32 SSD", "Moderate", "Intel Xeon E5-2670 v2*", "2.5", "Yes", "-", "Yes", "-", "-"},
		"m3.xlarge":   {4, 15, "2 x 40 SSD", "High", "Intel Xeon E5-2670 v2*", "2.5", "Yes", "-", "Yes", "Yes", "-"},
		"m3.2xlarge":  {8, 30, "2 x 80 SSD", "High", "Intel Xeon E5-2670 v2*", "2.5", "Yes", "-", "Yes", "Yes", "-"},
		"c4.large":    {2, 3.75, "EBS Only ", "Moderate ", "Intel Xeon E5-2666 v3 ", "2.9 ", "Yes ", "Yes ", "Yes ", "Yes ", "Yes "},
		"c4.xlarge":   {4, 7.5, "EBS Only", "High ", "Intel Xeon E5-2666 v3", "2.9 ", "Yes", "Yes ", "Yes", "Yes", "Yes"},
		"c4.2xlarge":  {8, 15, "EBS Only", "High ", "Intel Xeon E5-2666 v3", "2.9 ", "Yes", "Yes ", "Yes", "Yes", "Yes"},
		"c4.4xlarge":  {16, 30, "EBS Only", "High ", "Intel Xeon E5-2666 v3", "2.9 ", "Yes", "Yes ", "Yes", "Yes", "Yes"},
		"c4.8xlarge":  {36, 60, "EBS Only", "10 Gigabit ", "Intel Xeon E5-2666 v3", "2.9 ", "Yes", "Yes ", "Yes", "Yes", "Yes"},
		"c3.large":    {2, 3.75, "2 x 16 SSD", "Moderate", "Intel Xeon E5-2680 v2", "2.8", "Yes", "-", "Yes", "-", "Yes"},
		"c3.xlarge":   {4, 7.5, "2 x 40 SSD", "Moderate", "Intel Xeon E5-2680 v2", "2.8", "Yes", "-", "Yes", "Yes", "Yes"},
		"c3.2xlarge":  {8, 15, "2 x 80 SSD", "High", "Intel Xeon E5-2680 v2", "2.8", "Yes", "-", "Yes", "Yes", "Yes"},
		"c3.4xlarge":  {16, 30, "2 x 160 SSD", "High", "Intel Xeon E5-2680 v2", "2.8", "Yes", "-", "Yes", "Yes", "Yes"},
		"c3.8xlarge":  {32, 60, "2 x 320 SSD", "10 Gigabit", "Intel Xeon E5-2680 v2", "2.8", "Yes", "-", "Yes", "-", "Yes"},
		"g2.2xlarge":  {8, 15, "1 x 60 SSD", "High", "Intel Xeon &nbsp;E5-2670 ", "2.6", "Yes ", "-", "Yes", "Yes", "-"},
		"g2.8xlarge":  {32, 60, "2 x 120 SSD", "10 Gigabit", "Intel Xeon E5-2670", "2.6", "Yes", "-", "Yes&nbsp;", "-", "-"},
		"x1.32xlarge": {128, 1952, "2 x 1,920 SSD", "20 Gigabit", "Intel Xeon E7-8880 v3", "2.3", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"r3.large":    {2, 15.25, "1 x 32 SSD", "Moderate", "Intel Xeon E5-2670 v2", "2.5", "Yes", "-", "Yes", "-", "Yes"},
		"r3.xlarge":   {4, 30.5, "1 x 80 SSD", "Moderate", "Intel Xeon E5-2670 v2", "2.5 ", "Yes ", "- ", "Yes ", "Yes", "Yes"},
		"r3.2xlarge":  {8, 61, "1 x 160 SSD", "High", "Intel Xeon E5-2670 v2", "2.5 ", "Yes ", "- ", "Yes ", "Yes", "Yes"},
		"r3.4xlarge":  {16, 122, "1 x 320 SSD", "High", "Intel Xeon E5-2670 v2", "2.5 ", "Yes ", "- ", "Yes ", "Yes", "Yes"},
		"r3.8xlarge":  {32, 244, "2 x 320 SSD", "10 Gigabit", "Intel Xeon E5-2670 v2", "2.5 ", "Yes ", "- ", "Yes ", "-", "Yes"},
		"i2.xlarge":   {4, 30.5, "1 x 800 SSD", "Moderate", "Intel Xeon E5-2670 v2", "2.5", "Yes", "-", "Yes", "Yes", "Yes"},
		"i2.2xlarge":  {8, 61, "2 x 800 SSD", "High", "Intel Xeon E5-2670 v2", "2.5", "Yes", "-", "Yes", "Yes", "Yes"},
		"i2.4xlarge":  {16, 122, "4 x 800 SSD", "High", "Intel Xeon E5-2670 v2", "2.5", "Yes", "-", "Yes", "Yes", "Yes"},
		"i2.8xlarge":  {32, 244, "8 x 800 SSD", "10 Gigabit", "Intel Xeon E5-2670 v2", "2.5", "Yes", "-", "Yes", "-", "Yes"},
		"d2.xlarge":   {4, 30.5, "3 x 2000", "Moderate", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"d2.2xlarge":  {8, 61, "6 x 2000", "High", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"d2.4xlarge":  {16, 122, "12 x 2000", "High", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
		"d2.8xlarge":  {36, 244, "24 x 2000", "10 Gigabit", "Intel Xeon E5-2676 v3", "2.4", "Yes", "Yes", "Yes", "Yes", "Yes"},
	}
}

func GetInstanceTypesHandler(w http.ResponseWriter, r *http.Request) {
	var (
		out []string
	)

	rows, err := Config.ParkingSpotDataDB().Query("select instance_type from instance_types order by instance_type desc")
	if err != nil {
		commons.RespondJson(w, r, commons.ErrorResponse{
			Message: string(err.Error()),
			Code:    416,
		})
		return
	}

	for rows.Next() {
		var instanceType string
		rows.Scan(&instanceType)

		out = append(out, instanceType)
	}

	commons.RespondJson(w, r, out)
}
