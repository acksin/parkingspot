var ParkingSpotInstanceRow = React.createClass({
  getInitialState: function() {
    return {
      content: null
    };
  },
  roundPenny: function(x) {
    return parseFloat(Math.round(x * 100) / 100);
  },
  getRow: function() {
    $.get("/v1/spot/" + this.props.az + "/" + this.props.instanceType + "/" + this.props.duration, function(result) {
      let content = (
        <tr>
          <td><a href="#" onClick={this.updateChart}><b>{this.props.az}</b></a></td>
          <td data-sort-value={result.OnDemandPrice}><ParkingSpotOnDemand price={result.OnDemandPrice} /></td>
          <td data-sort-value={result.RecommendedBid}><ParkingSpotRecommendedBid price={this.roundPenny(result.RecommendedBid)} /></td>
          <td data-sort-value={result.Savings}><ParkingSpotSavings percent={result.Savings} /></td>
          <td><ParkingSpotLaunch az={this.props.az} instanceType={this.props.instanceType} /></td>
        </tr>
      );

      this.setState({
        content: content
      });
    }.bind(this))
  },
  componentDidMount: function() {
    this.getRow();
  },
  render: function() {
    return this.state.content;
  }
});
