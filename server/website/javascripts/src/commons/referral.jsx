var AcksinReferral = React.createClass({
  getInitialState: function() {
    return {};
  },
  componentDidMount: function() {
    $.get(BridgeAPI + "/v1/user", function(result) {
      this.setState(result);
    }.bind(this));
  },
  render: function() {
    return (
      <div>
        <p>
          Send this link to your friends: <strong>{"https://www.acksin.com/referral/?u=" + this.state.Username}</strong>.
          If they signup and purchase Acksin you get a <strong>$29 dollar credit</strong> to your account.
        </p>
      </div>
    );

  }
});
