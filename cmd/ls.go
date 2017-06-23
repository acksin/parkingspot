// Copyright © 2017 Abhi Yerra <abhi@opszero.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package cmd

import (
	"github.com/spf13/cobra"

	"github.com/opszero/parkingspot/stats"
)

var (
	newSpotMeRequest stats.SpotMeRequest
)

// newCmd represents the new command
var newCmd = &cobra.Command{
	Use:   "ls",
	Short: "Find Spot Machines Fulfilling Your Criteria",
	Long: `Find Spot Machines filling various criteria
such as region, bid, cpu and memory.`,
	Run: func(cmd *cobra.Command, args []string) {
		s := &stats.Stats{}
		s.LoadDB()
		s.SpotMe(newSpotMeRequest)
	},
}

func init() {
	RootCmd.AddCommand(newCmd)

	newCmd.Flags().StringVarP(&newSpotMeRequest.Region, "region", "r", "", "Specify Region")
	newCmd.Flags().Float64VarP(&newSpotMeRequest.MaxBid, "max-bid", "b", -1, "Specify the Max Price you want to pay.")
	newCmd.Flags().IntVarP(&newSpotMeRequest.MinCPU, "min-cpu", "c", -1, "Specify the min number of CPUs.")
	newCmd.Flags().Float64VarP(&newSpotMeRequest.MinMemory, "min-memory", "m", -1, "Specify the min number of memorys.")
}
