var ParkingSpotConsole = React.createClass({
  getInitialState: function() {
    return {
      azs: [],
      az: QueryString.az == undefined ? 'us-west-2a' : QueryString.az,
      duration: QueryString.duration  == undefined ? 2 : QueryString.duration,
      instanceTypes: []
    }
  },
  subscriptionLink: function(name, link) {
    return (
      <a href={link}>{name}</a>
    );
  },
  getAZs: function(az) {
    $.get("/v1/instance_types", function(result) {
      var its = [];

      for(var i = 0; i < result.length; i++) {
        its.push(<ParkingSpotRow key={i} name={result[i]} az={az} duration={this.state.duration} />);
      }

      this.setState({
        instanceTypes: its,
      });
    }.bind(this));

    $.get("/v1/availability_zones", function(result) {
      this.setState({
        azs: result
      });
    }.bind(this));
  },
  componentDidMount: function(){
    this.getAZs(this.state.az);

    $('#console-table').stupidtable();
  },
  render: function() {
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="header">
              <h4 className="title">{this.state.az}</h4>

              <form className="form-inline">
                <div className="form-group">
                  <label for="az">Availability Zone: </label>
                  <select className="form-control" id="az" name="az" defaultValue={this.state.az}>
                    {this.state.azs.map(function(name, index) {
                       return (
                         <option key={name}>{name}</option>
                       );
                     })}
                  </select>
                </div>

                <div className="form-group">
                  <label for="duration">Duration: </label>
                  <input className="form-control" name="duration" type="text" defaultValue={this.state.duration} /> hours
                </div>

                <div className="form-group">
                  <button name="submit" type="submit" className="btn btn-primary">Go</button>
                </div>
              </form>
            </div>

            <div className="content table-responsive table-full-width">
              <div id="chart_div"></div>

              <table className="table table-striped" id="console-table">
                <thead>
                  <tr>
                    <th>Instance Type</th>
                    <th data-sort="float">OnDemand</th>
                    <th data-sort="float">Recommended Bid</th>
                    <th data-sort="float">Savings</th>
                    <th>Launch</th>
                  </tr>
                </thead>
                <tbody>
                  {this.state.instanceTypes}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }
});
