package main

import (
	"net/http"

	"github.com/acksin/fugue/commons"
)

func GetAZsHandler(w http.ResponseWriter, r *http.Request) {
	var (
		out []string
	)

	rows, err := Config.ParkingSpotDataDB().Query("select availability_zone from availability_zones order by availability_zone desc")
	if err != nil {
		commons.RespondJson(w, r, commons.ErrorResponse{
			Message: string(err.Error()),
			Code:    416,
		})
		return
	}

	for rows.Next() {
		var az string
		rows.Scan(&az)

		out = append(out, az)
	}

	commons.RespondJson(w, r, out)
}
