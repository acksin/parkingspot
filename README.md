# ParkingSpot

The ParkingSpot CLI tool allows you to integrate AWS EC2 Spot Pricing
with other services that you may use. Check out
the [integrations page](https://www.parkingspot.bid/integrations) for
some ways that you can use ParkingSpot. Current integrations include
Docker Machine, Docker Compose, Kubernetes, Terraform, Packer and
anything that can use `ENV` variables.

## Usage

### Generate Stats

```
parkingspot stats --update
```

Example usage where we want to find instances with at least 6 cpus in
the eu-west-1 region.

```
parkingspot new --cpu 6 -region eu-west-1 kubernetes-kops
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

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
