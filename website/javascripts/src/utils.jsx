var ParkingSpotOnDemand  = React.createClass({
  render: function() {
    if(this.props.price == "-1" || this.props.price == "") {
      return (
        <span data-toggle="tooltip" title="No OnDemand price. This instance type is likely not a current generation type and hence is not available.">N/A</span>
      );
    }

    return (
      <span>${this.props.price}</span>
    );
  }
});

var ParkingSpotRecommendedBid  = React.createClass({
  showChart: function(e) {
    e.preventDefault();

    $.get("/v1/spot/hourly/" + this.props.az + "/" + this.props.instanceType, function(result) {
      var labels = [], price = [], ondemand = [], recommended = [];

      for(var i = 0; i < result.length; i++) {
        labels.push(i + ":00");
        price.push({ meta: 'Average Spot Price', value: result[i].Mean });
        ondemand.push({
          meta: 'On-Demand Price',
          value: Number(result[i].OnDemandPrice == -1 ? undefined : result[i].OnDemandPrice)
        });
        recommended.push({
          meta: 'Recommended Bid',
          value: Number(result[i].RecommendedBid)
        });
      }

      var data = {
        labels: labels,
        series: [price, ondemand, recommended]
      }

      new Chartist.Line('#chart_div', data, {
        plugins: [
          Chartist.plugins.tooltip(),
          Chartist.plugins.ctAxisTitle({
            axisX: {
              axisTitle: 'Hour',
              axisClass: 'ct-axis-title',
              offset: {
                x: 0,
                y: 50
              },
              textAnchor: 'middle'
            },
            axisY: {
              axisTitle: 'Price',
              axisClass: 'ct-axis-title',
              offset: {
                x: 0,
                y: 0
              },
              textAnchor: 'middle',
              flipTitle: false
            }
          })
        ]
      });
    }.bind(this))
  },
  render: function() {
    if(this.props.price == "nan" || this.props.price == "") {
      return (
        <span data-toggle="tooltip" title="We were unable to calculate an appropriate bid for this instance.">N/A</span>
      );
    }

    return (
      <a href="#" onClick={this.showChart}>${this.props.price}</a>
    );
  }
});

var ParkingSpotSavings = React.createClass({
  render: function() {
    if(this.props.percent == "-1" || this.props.percent == "NaN") {
      return (
        <span data-toggle="tooltip" title="Savings are the savings over the OnDemand price.">N/A</span>
      );
    }

    return (
      <span>{Math.round(this.props.percent) + '%'}</span>
    );
  }
});


var ParkingSpotLaunch = React.createClass({
  render: function() {
    var region = this.props.az.substring(0, this.props.az.length-1);

    return (
      <a target="_blank" href={"https://" + region + ".console.aws.amazon.com/ec2sp/v1/spot/launch-wizard?region=" + region}>Launch</a>
    );
  }
});
