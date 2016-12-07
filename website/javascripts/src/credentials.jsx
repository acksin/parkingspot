var ParkingSpotCredentials = React.createClass({
  render: function() {
    return (
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="header">
              <h4 className="title">Credentials</h4>
            </div>

            <div className="content">
              <p>PARKINGSPOT_API_KEY</p>
              <AcksinCredentials />
            </div>
          </div>
        </div>
      </div>
    );
  }
});
