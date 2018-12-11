var ParkingSpotDashboard = React.createClass({
  getInitialState: function() {
    return {
      user: {
        Username: ""
      }
    }
  },
  componentDidMount: function() {
    $.get("/v1/user", function(result) {
      this.setState({
        user: result
      });
    }.bind(this)).fail(function() {
      document.location = "https://www.parkingspot.bid/login/#auth";
    });

    $.get("/v1/subscription", function(result) {
      if(result == null) {
        $.notify({
          icon: 'ti-gift',
          message: "Hey! Thanks for checking out ParkingSpot. Just to let you know this version of ParkingSpot only has the Previous Generation of EC2 Machines as well as M3 and C3 instance types. Consider <a href='/billing'>subscribing</a> to get all the instances. Otherwise, enjoy cutting the costs of your infrastructure!"
        },{
          type: 'success',
          timer: 4000
        });
      }
    }.bind(this));

  },
  render: function() {
    return (
      <div className="wrapper">
        <Sidebar />

        <div className="main-panel">
          <TopNav user={this.state.user} />
          <div className="content">
            <div className="container-fluid">
              {this.props.children}
            </div>
          </div>

          <ParkingSpotFooter />
        </div>
      </div>
    );
  }
});
