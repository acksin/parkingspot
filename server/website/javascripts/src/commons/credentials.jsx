var AcksinCredentials = React.createClass({
  getInitialState: function() {
    return {
      apiKey: ''
    };
  },
  resetAPIKey: function(event) {
    if(confirm("Are you sure you want to update your API key?")) {
      $.post(BridgeAPI + "/v1/credentials", function(result) {
        document.location.reload();
      });
    }
  },
  componentDidMount: function() {
    this.serverRequest = $.get(BridgeAPI + "/v1/user", function(result) {
      console.log(JSON.stringify(result));
      this.setState({
        apiKey: result.APIKey,
      });
    }.bind(this)).fail(function(result) {
      console.log(JSON.stringify(result));
    }.bind(this));
  },

  componentWillUnmount: function() {
    this.serverRequest.abort();
  },
  render: function() {
    return (
      <div>
        <p>
          <code>
            {this.state.apiKey}
          </code>

        </p>
        <button className="btn btn-danger" onClick={this.resetAPIKey}>Reset Key</button>
      </div>
    );
  }
});
