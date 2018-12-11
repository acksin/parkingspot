package main

type Regions map[string][]string

var (
	regions Regions
)

func AllAZs() (a []string) {
	for _, v := range regions {
		a = append(a, v...)
	}

	return a
}

func AZs(r string) []string {
	return regions[r]
}

func NewRegions() Regions {
	regions := make(Regions)

	regions["ap-northeast-1"] = []string{"ap-northeast-1a", "ap-northeast-1c"}
	regions["ap-northeast"] = []string{"ap-northeast-2a", "ap-northeast-2c"}
	regions["ap-southeast-1"] = []string{"ap-southeast-1a", "ap-soutoeast-1b"}
	regions["ap-southeast-2"] = []string{"ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"}
	regions["eu-central-1"] = []string{"eu-central-1a", "eu-central-1b"}
	regions["eu-west-1"] = []string{"eu-west-1a", "eu-west-1b", "eu-west-1c"}
	regions["sa-east-1"] = []string{"sa-east-1a", "sa-east-1c"}
	regions["us-east-1"] = []string{"us-east-1a", "us-east-1b", "us-east-1d", "us-east-1e"}
	regions["us-west-1"] = []string{"us-west-1a", "us-west-1c"}
	regions["us-west-2"] = []string{"us-west-2a", "us-west-2b", "us-west-2c"}

	return regions
}

func init() {
	regions = NewRegions()
}
