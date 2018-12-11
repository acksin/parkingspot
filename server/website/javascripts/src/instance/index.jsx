var ParkingSpotInstance = React.createClass({
  getInitialState: function() {
    return {
      azs: [],
      instanceType: this.props.params.instanceType,
      dataTable: [
        ['Availability Zone', 'OnDemand', 'Price'],
      ],
    }
  },
  getAZs: function() {
    $.get("/v1/availability_zones", function(result) {
      var azs= [];
      this.getChartData(result);

      for(var i = 0; i < result.length; i++) {
        azs.push(
          <ParkingSpotInstanceRow key={"parkingspot-instance-row" + i} instanceType={this.state.instanceType} az={result[i]} duration="1" />
        );
      }

      this.setState({
        azNames: result,
        azs: azs
      });
    }.bind(this));
  },
  componentDidMount: function() {
    this.getAZs();

    $('#instance-table').stupidtable();
  },
  getChartData: function(azNames) {
    for(var i = 0; i < azNames.length; i++) {
      $.get("/v1/spot/" + azNames[i] + "/" + this.state.instanceType + "/1", function(result) {
        console.log(result)
        this.state.dataTable.push([
          result.AZ,
          Number(result.OnDemandPrice == -1 ? 0 : result.OnDemandPrice),
          Number(result.Mean),
        ]);
      }.bind(this));
    }
    /* google.charts.setOnLoadCallback(function() {
     *   var data = google.visualization.arrayToDataTable(this.state.dataTable);
     *   var options = {
     *     height: 400,
     *     chart: {
     *       title: 'OnDemand vs Average Price',
     *     }
     *   };

     *   var chart = new google.charts.Bar(document.getElementById('chart_div'));
     *   chart.draw(data, options);
     * }.bind(this));
     */

  },
  render: function() {
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="header">
              <h4 className="title">{this.state.instanceType}</h4>
            </div>

            <div className="content table-responsive table-full-width">
              <div id="chart_div">
              </div>

              <table className="table table-striped" id="instance-table">
                <thead>
                  <tr>
                    <th>Availability Zone</th>
                    <th data-sort="float">OnDemand</th>
                    <th data-sort="float">Recommended Bid</th>
                    <th data-sort="float">Savings</th>
                    <th>Launch</th>
                  </tr>
                </thead>
                <tbody>
                  {this.state.azs}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }
});
