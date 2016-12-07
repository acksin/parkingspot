var BillingSubscribe = React.createClass({
  getInitialState: function() {
    return {
      redirectTo: "",
      plans: this.props.plans,
    };
  },
  subscribe: function(e) {
    e.preventDefault();

    ga('send', 'event', 'Purchase', this.props.product, 'Purchase');

    var $form = $('#payment-form');
    console.log($form);
    $form.find('.submit').prop('disabled', true);

    Stripe.card.createToken($form, function(status, response) {
      // Grab the form:
      var $form = $('#payment-form');

      console.log(response);
      if (response.error) { // Problem!

        // Show the errors on the form:
        $form.find('.payment-errors').text(response.error.message);
        $form.find('.submit').prop('disabled', false); // Re-enable submission

      } else { // Token was created!

        // Get the token ID:
        var token = response.id;

        // Insert the token ID into the form so it gets submitted to the server:
        $form.append($('<input type="hidden" name="stripeToken">').val(token));

        // Submit the form:
        $form.get(0).submit();
      }
    });

    return false;
  },
  render: function() {
    if(this.props.subscription != null) {
      return (
        <div className="row">
          <div className="col-xs-12 cancel-link">
            <p>You are subscribed to <span className="text-capitalize">{this.props.subscription.Plan}</span>.</p>
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col-xs-12 cancel-link">

          <form action="/v1/subscribe" method="POST" id="payment-form" onSubmit={this.subscribe}>
            <input name="redirectTo" type="hidden" value={this.state.redirectTo} />
            <div className="col-xs-12">
              <div className="form-group">
                {this.state.plans}
              </div>
            </div>

            <div className="col-xs-12">
              <div className="form-group">
                <label for="cardNumber">Card Number</label>
                <div className="input-group">
                  <input
                      data-stripe="number"
                      type="tel"
                      className="form-control"
                      name="cardNumber"
                      placeholder="Card Number"
                      autocomplete="cc-number"
                      required autofocus
                  />
                  <span className="input-group-addon"><i className="fa fa-credit-card"></i></span>
                </div>
              </div>
            </div>
            <div className="col-xs-8">
              <div className="form-group">
                <label for="cardExpiry"><span className="hidden-xs">Expiration</span><span className="visible-xs-inline">Exp</span> Date</label>
                <div className="">
                  <input type="text" size="2" data-stripe="exp-month" name="expMonth" placeholder="MM" className="form-control pull-left" style={{width: '5em'}} />
                  <span className="pull-left">&nbsp;</span>
                  <input type="text" size="4" data-stripe="exp-year" name="expYear" placeholder="YYYY" className="form-control pull-left" style={{width: '5em'}} />
                </div>
              </div>
            </div>

            <div className="col-xs-4">
              <div className="form-group">
                <label for="cardCVC">CVC Code</label>
                <input
                    type="tel"
                    className="form-control"
                    name="cardCVC"
                    data-stripe="cvc"
                    placeholder="CVC"
                    autocomplete="cc-csc"
                    required
                />
              </div>
            </div>
            <div className="col-xs-12">
              <button className="subscribe btn btn-success btn-lg btn-block" type="submit">Start Subscription</button>
            </div>
            <div className="row" style={{display: "none"}}>
              <div className="col-xs-12">
                <p className="payment-errors"></p>
              </div>
            </div>
          </form>
        </div>
      </div>
    );
  }
});

var BillingUnsubscribe = React.createClass({
  unsubscribe: function() {
    /* if(!confirm("Are you sure?")) {
     *   return false;
     * }*/
  },
  render: function() {
    if(this.props.subscription == null) {
      return null;
    }

    return (
      <div className="row">
        <div className="col-xs-12 cancel-link">
          <a className="cancel-link" href="/v1/unsubscribe" onClick={this.unsubscribe} >Cancel Subscription</a>
        </div>
      </div>
    );
  }
});


var Billing = React.createClass({
  products: [
    {
      plan: "parkingspot",
      name: "parkingspot",
      amount: "99",
      frequency: "month",
    }
  ],
  getInitialState: function() {
    return {
      alert: null,
      subscription: null,
    };
  },
  productList: function() {
    if(this.products.length > 1) {
      var indents = [];

      for(var i in this.products) {
        indents.push(
          <li key={i} >
            <input type="radio" name="plan" value={this.products[i].plan} /> {this.products[i].name} - ${this.products[i].amount} / {this.products[i].frequency} + 30 day free trial
          </li>
        );
      }

      return <ul>{indents}</ul>;
    } else {
      let product = this.products[0];
      return (
        <div>
          <input type="hidden" name="plan" value={product.plan} />
          <p>Subscribe to ParkingSpot for ${product.amount} and get 7 days free.</p>
        </div>
      );
    }
  },
  componentDidMount: function() {
    $.get("/v1/subscription", function(result) {
      this.setState({
        subscription: result
      });
    }.bind(this));
  },
  render: function() {
    let content = (
      <div>
        {this.state.alert}

        <BillingSubscribe plans={this.productList()} subscription={this.state.subscription} />
        <BillingUnsubscribe subscription={this.state.subscription} />
      </div>
    );

    return (
      <Card title="Subscription" category="" className="col-md-6" content={content} />
    );
  }
});

$(document).ready(function() {
  if(location.hostname.match(/parkingspot.bid/) || location.hostname.match(/acksin.com/) || location.hostname.match(/opszero.com/)) {
    Stripe.setPublishableKey('pk_live_sNFft4hL5z7OnCpVZAxgU9SO');
  } else {
    console.log("Set Test");
    Stripe.setPublishableKey('pk_test_fFv4UKwCwpxjdZBy56a5TylI');
  }
});
