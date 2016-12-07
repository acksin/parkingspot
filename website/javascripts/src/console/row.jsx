var ParkingSpotRow = React.createClass({
  getInitialState: function() {
    return {
      content: null
    };
  },
  roundPenny: function(x) {
    return parseFloat(Math.round(x * 100) / 100);
  },
  getRow: function() {
    this.serverRequest = $.get("/v1/spot/" + this.props.az + "/" + this.props.name + "/" + this.props.duration, function(result) {
      console.log(result);

      let content = (
        <tr>
          <td>
            <ReactRouter.Link to={`/instance/${this.props.name}`}>
              <b>{this.props.name}</b>
            </ReactRouter.Link>
          </td>
          <td data-sort-value={result.OnDemandPrice}><ParkingSpotOnDemand price={result.OnDemandPrice} /></td>
          <td data-sort-value={result.RecommendedBid}><ParkingSpotRecommendedBid az={this.props.az} instanceType={this.props.name} price={this.roundPenny(result.RecommendedBid)} /></td>
          <td data-sort-value={result.Savings}><ParkingSpotSavings percent={result.Savings} /></td>
          <td><ParkingSpotLaunch az={this.props.az} instanceType={this.props.name} /></td>
        </tr>
      );

      this.setState({
        content: content,
      });
    }.bind(this)).fail(function(e) {
      this.setState({
        content: null,
      });
    }.bind(this));
  },
  componentDidMount: function() {
    this.getRow();
  },
  render: function() {
    return this.state.content;
  }
});
