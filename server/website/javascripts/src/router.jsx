function gaRouterUpdated() {
  window.ga('send', 'pageview', location.pathname);
}

var LoginFailed = React.createClass({
  componentDidMount: function() {
    document.location = "https://www.parkingspot.bid/login/?failed=1"
  },
  render: function() {
    return null;
  }
});

$(document).ready(function() {
  ReactDOM.render((
    <ReactRouter.Router onUpdate={gaRouterUpdated} history={ReactRouter.browserHistory}>
      <ReactRouter.Route path="/" component={ParkingSpotDashboard} >
        <ReactRouter.IndexRoute component={ParkingSpotConsole}/>
        <ReactRouter.Route path="instance/:instanceType" component={ParkingSpotInstance}/>
        <ReactRouter.Route path="billing" component={Billing}/>
        <ReactRouter.Route path="credentials" component={ParkingSpotCredentials}/>
      </ReactRouter.Route>
      <ReactRouter.Route path="/auth" component={LoginFailed} />
      <ReactRouter.Redirect from="/console" to="/" />
    </ReactRouter.Router>
  ), document.getElementById("app"));
});
