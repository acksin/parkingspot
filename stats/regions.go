package stats

import (
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/ec2"
)

func GetRegions() (a []string) {
	sess, err := session.NewSession()
	if err != nil {
		return
	}

	svc := ec2.New(sess)

	resp, err := svc.DescribeRegions(&ec2.DescribeRegionsInput{})
	if err != nil {
		return
	}

	for _, i := range resp.Regions {
		a = append(a, *i.RegionName)
	}

	return
}

// func GetAZs() (a []string) {
// 	for i := range GetRegions() {
// 		sess := session.Must(session.NewSession())

// 		svc := ec2.New(sess)

// 		params := &ec2.DescribeAvailabilityZonesInput{
// 	v		DryRun: aws.Bool(true),
// 			Filters: []*ec2.Filter{
// 				{ // Required
// 					Name: aws.String("String"),
// 					Values: []*string{
// 						aws.String("String"), // Required
// 						// More values...
// 					},
// 				},
// 				// More values...
// 			},
// 			ZoneNames: []*string{
// 				aws.String("String"), // Required
// 				// More values...
// 			},
// 		}

// 		resp, err := svc.DescribeAvailabilityZones(params)

// 		if err != nil {
// 			return
// 		}

// 		// Pretty-print the response data.
// 		fmt.Println(resp)
// 	}

// 	return
// }
