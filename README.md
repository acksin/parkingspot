# ParkingSpot

The ParkingSpot CLI tool allows you to integrate AWS EC2 Spot Pricing
with other services that you may use. Check out
the [integrations page](https://www.parkingspot.bid/integrations) for
some ways that you can use ParkingSpot. Current integrations include
Docker Machine, Docker Compose, Kubernetes, Terraform, Packer and
anything that can use `ENV` variables.

## Usage

Example usage where we want to find machiens with at least 6 cpus in the eu-west-1 region.

```
PARKINGSPOT_API_KEY=wKHxyfeayimNEs-v3B80a_VC1VXgDKdp_w== ./parkingspot -cpu 6 -region eu-west-1
```

Example output:

```
PARKINGSPOT_REGION=us-west-2
PARKINGSPOT_AZ=us-west-2c
PARKINGSPOT_BID=0.068674
PARKINGSPOT_INSTANCE_TYPE=r3.xlarge
```

## Flags

```
Usage of ./parkingspot:
  -api-key string
        Set the ParkingSpot API Key. If not set it will look at PARKINGSPOT_API_KEY environment variable.
  -cpu int
        Set the minimum number of CPU cores you want. (default 1)
  -duration int
        Max duration of time that this machie is going to run. Set it to -1 if it is to run forever. (default 2)
  -max-bid float
        Set the maximum amount you want to bid. (default 0.1)
  -memory float
        Set the minimum number of memory you want in GB. (default 0.5)
  -region string
        What region do you want the machines from. If empty will get the lowest priced machine
```


## License

   Copyright 2016 Acksin LLC

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
