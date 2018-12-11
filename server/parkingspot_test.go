package main

import (
	"fmt"
	"testing"
	"time"
)

// func TestDownloadSpotPricing(t *testing.T) {
// 	//	t.Errorf("foo")
// 	for i := 0; i < 90; i++ {
// 		fmt.Println("Day", i)
// 		if len(GetDownloadPricing(i)) == 0 {
// 			t.Errorf("Nope")
// 		}
// 	}
// }

func TestGetSpotPricing(t *testing.T) {
	a := GetSpotPricing("i2.xlarge", "us-west-2", time.Now().UTC(), time.Now().UTC())

	if a.Mean == 0 || a.StdDev == 0 {
		t.Errorf("Nope")
	}

	fmt.Println(a)
}
