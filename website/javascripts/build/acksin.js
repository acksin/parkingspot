'use strict';

var BillingSubscribe = React.createClass({
  displayName: 'BillingSubscribe',

  getInitialState: function getInitialState() {
    return {
      redirectTo: "",
      plans: this.props.plans
    };
  },
  subscribe: function subscribe(e) {
    e.preventDefault();

    ga('send', 'event', 'Purchase', this.props.product, 'Purchase');

    var $form = $('#payment-form');
    console.log($form);
    $form.find('.submit').prop('disabled', true);

    Stripe.card.createToken($form, function (status, response) {
      // Grab the form:
      var $form = $('#payment-form');

      console.log(response);
      if (response.error) {
        // Problem!

        // Show the errors on the form:
        $form.find('.payment-errors').text(response.error.message);
        $form.find('.submit').prop('disabled', false); // Re-enable submission
      } else {
        // Token was created!

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
  render: function render() {
    if (this.props.subscription != null) {
      return React.createElement(
        'div',
        { className: 'row' },
        React.createElement(
          'div',
          { className: 'col-xs-12 cancel-link' },
          React.createElement(
            'p',
            null,
            'You are subscribed to ',
            React.createElement(
              'span',
              { className: 'text-capitalize' },
              this.props.subscription.Plan
            ),
            '.'
          )
        )
      );
    }

    return React.createElement(
      'div',
      { className: 'row' },
      React.createElement(
        'div',
        { className: 'col-xs-12 cancel-link' },
        React.createElement(
          'form',
          { action: '/v1/subscribe', method: 'POST', id: 'payment-form', onSubmit: this.subscribe },
          React.createElement('input', { name: 'redirectTo', type: 'hidden', value: this.state.redirectTo }),
          React.createElement(
            'div',
            { className: 'col-xs-12' },
            React.createElement(
              'div',
              { className: 'form-group' },
              this.state.plans
            )
          ),
          React.createElement(
            'div',
            { className: 'col-xs-12' },
            React.createElement(
              'div',
              { className: 'form-group' },
              React.createElement(
                'label',
                { 'for': 'cardNumber' },
                'Card Number'
              ),
              React.createElement(
                'div',
                { className: 'input-group' },
                React.createElement('input', {
                  'data-stripe': 'number',
                  type: 'tel',
                  className: 'form-control',
                  name: 'cardNumber',
                  placeholder: 'Card Number',
                  autocomplete: 'cc-number',
                  required: true, autofocus: true
                }),
                React.createElement(
                  'span',
                  { className: 'input-group-addon' },
                  React.createElement('i', { className: 'fa fa-credit-card' })
                )
              )
            )
          ),
          React.createElement(
            'div',
            { className: 'col-xs-8' },
            React.createElement(
              'div',
              { className: 'form-group' },
              React.createElement(
                'label',
                { 'for': 'cardExpiry' },
                React.createElement(
                  'span',
                  { className: 'hidden-xs' },
                  'Expiration'
                ),
                React.createElement(
                  'span',
                  { className: 'visible-xs-inline' },
                  'Exp'
                ),
                ' Date'
              ),
              React.createElement(
                'div',
                { className: '' },
                React.createElement('input', { type: 'text', size: '2', 'data-stripe': 'exp-month', name: 'expMonth', placeholder: 'MM', className: 'form-control pull-left', style: { width: '5em' } }),
                React.createElement(
                  'span',
                  { className: 'pull-left' },
                  ' '
                ),
                React.createElement('input', { type: 'text', size: '4', 'data-stripe': 'exp-year', name: 'expYear', placeholder: 'YYYY', className: 'form-control pull-left', style: { width: '5em' } })
              )
            )
          ),
          React.createElement(
            'div',
            { className: 'col-xs-4' },
            React.createElement(
              'div',
              { className: 'form-group' },
              React.createElement(
                'label',
                { 'for': 'cardCVC' },
                'CVC Code'
              ),
              React.createElement('input', {
                type: 'tel',
                className: 'form-control',
                name: 'cardCVC',
                'data-stripe': 'cvc',
                placeholder: 'CVC',
                autocomplete: 'cc-csc',
                required: true
              })
            )
          ),
          React.createElement(
            'div',
            { className: 'col-xs-12' },
            React.createElement(
              'button',
              { className: 'subscribe btn btn-success btn-lg btn-block', type: 'submit' },
              'Start Subscription'
            )
          ),
          React.createElement(
            'div',
            { className: 'row', style: { display: "none" } },
            React.createElement(
              'div',
              { className: 'col-xs-12' },
              React.createElement('p', { className: 'payment-errors' })
            )
          )
        )
      )
    );
  }
});

var BillingUnsubscribe = React.createClass({
  displayName: 'BillingUnsubscribe',

  unsubscribe: function unsubscribe() {
    /* if(!confirm("Are you sure?")) {
     *   return false;
     * }*/
  },
  render: function render() {
    if (this.props.subscription == null) {
      return null;
    }

    return React.createElement(
      'div',
      { className: 'row' },
      React.createElement(
        'div',
        { className: 'col-xs-12 cancel-link' },
        React.createElement(
          'a',
          { className: 'cancel-link', href: '/v1/unsubscribe', onClick: this.unsubscribe },
          'Cancel Subscription'
        )
      )
    );
  }
});

var Billing = React.createClass({
  displayName: 'Billing',

  products: [{
    plan: "parkingspot",
    name: "parkingspot",
    amount: "99",
    frequency: "month"
  }],
  getInitialState: function getInitialState() {
    return {
      alert: null,
      subscription: null
    };
  },
  productList: function productList() {
    if (this.products.length > 1) {
      var indents = [];

      for (var i in this.products) {
        indents.push(React.createElement(
          'li',
          { key: i },
          React.createElement('input', { type: 'radio', name: 'plan', value: this.products[i].plan }),
          ' ',
          this.products[i].name,
          ' - $',
          this.products[i].amount,
          ' / ',
          this.products[i].frequency,
          ' + 30 day free trial'
        ));
      }

      return React.createElement(
        'ul',
        null,
        indents
      );
    } else {
      var product = this.products[0];
      return React.createElement(
        'div',
        null,
        React.createElement('input', { type: 'hidden', name: 'plan', value: product.plan }),
        React.createElement(
          'p',
          null,
          'Subscribe to ParkingSpot for $',
          product.amount,
          ' and get 7 days free.'
        )
      );
    }
  },
  componentDidMount: function componentDidMount() {
    $.get("/v1/subscription", function (result) {
      this.setState({
        subscription: result
      });
    }.bind(this));
  },
  render: function render() {
    var content = React.createElement(
      'div',
      null,
      this.state.alert,
      React.createElement(BillingSubscribe, { plans: this.productList(), subscription: this.state.subscription }),
      React.createElement(BillingUnsubscribe, { subscription: this.state.subscription })
    );

    return React.createElement(Card, { title: 'Subscription', category: '', className: 'col-md-6', content: content });
  }
});

$(document).ready(function () {
  if (location.hostname.match(/parkingspot.bid/) || location.hostname.match(/acksin.com/) || location.hostname.match(/opszero.com/)) {
    Stripe.setPublishableKey('pk_live_sNFft4hL5z7OnCpVZAxgU9SO');
  } else {
    console.log("Set Test");
    Stripe.setPublishableKey('pk_test_fFv4UKwCwpxjdZBy56a5TylI');
  }
});
"use strict";

var Card = React.createClass({
  displayName: "Card",

  render: function render() {
    return React.createElement(
      "div",
      { className: this.props.className },
      React.createElement(
        "div",
        { className: "card" },
        React.createElement(
          "div",
          { className: "header" },
          React.createElement(
            "h4",
            { className: "title" },
            this.props.title
          ),
          React.createElement(
            "p",
            { className: "category" },
            this.props.category
          )
        ),
        React.createElement(
          "div",
          { className: "content" },
          this.props.content
        )
      )
    );
  }
});
"use strict";

var AcksinCredentials = React.createClass({
  displayName: "AcksinCredentials",

  getInitialState: function getInitialState() {
    return {
      apiKey: ''
    };
  },
  resetAPIKey: function resetAPIKey(event) {
    if (confirm("Are you sure you want to update your API key?")) {
      $.post(BridgeAPI + "/v1/credentials", function (result) {
        document.location.reload();
      });
    }
  },
  componentDidMount: function componentDidMount() {
    this.serverRequest = $.get(BridgeAPI + "/v1/user", function (result) {
      console.log(JSON.stringify(result));
      this.setState({
        apiKey: result.APIKey
      });
    }.bind(this)).fail(function (result) {
      console.log(JSON.stringify(result));
    }.bind(this));
  },

  componentWillUnmount: function componentWillUnmount() {
    this.serverRequest.abort();
  },
  render: function render() {
    return React.createElement(
      "div",
      null,
      React.createElement(
        "p",
        null,
        React.createElement(
          "code",
          null,
          this.state.apiKey
        )
      ),
      React.createElement(
        "button",
        { className: "btn btn-danger", onClick: this.resetAPIKey },
        "Reset Key"
      )
    );
  }
});
"use strict";

var AcksinPage = React.createClass({
  displayName: "AcksinPage",

  getInitialState: function getInitialState() {
    return {
      content: {
        __html: ""
      }
    };
  },
  componentDidMount: function componentDidMount() {
    $.get(this.props.page, function (response) {
      this.setState({
        content: {
          __html: response
        }
      });
    }.bind(this));
  },
  render: function render() {
    return React.createElement("div", { dangerouslySetInnerHTML: this.state.content });
  }
});

var AcksinOrgPage = React.createClass({
  displayName: "AcksinOrgPage",

  getInitialState: function getInitialState() {
    return {
      content: {
        __html: ""
      }
    };
  },
  componentDidMount: function componentDidMount() {
    $.get(this.props.page, function (response) {

      var parser = new Org.Parser();
      var orgDocument = parser.parse(response);
      var orgHTMLDocument = orgDocument.convert(Org.ConverterHTML, {
        headerOffset: 1,
        exportFromLineNumber: false,
        suppressSubScriptHandling: false,
        suppressAutoLink: false
      });

      this.setState({
        content: {
          __html: orgHTMLDocument.toString()
        }
      });
    }.bind(this));
  },
  render: function render() {
    return React.createElement("div", { dangerouslySetInnerHTML: this.state.content });
  }
});

var AcksinPrivacyPage = React.createClass({
  displayName: "AcksinPrivacyPage",

  render: function render() {
    return React.createElement(AcksinPage, { page: "/a/privacy.html" });
  }
});

var AcksinTOSPage = React.createClass({
  displayName: "AcksinTOSPage",

  render: function render() {
    return React.createElement(AcksinPage, { page: "/a/tos.html" });
  }
});
"use strict";

var BridgeAPI = document.location.origin;
/* var TrackedLink = React.createClass({
 *   sendGAEvent: function(e) {
 *     ga('send', 'event', 'Validation', 'ParkingSpot ' + e, 'Validation ParkingSpot ' + e);
 *   },
 *   render: function() {
 *     return (
 *
 *     );
 *   }
 * });*/
"use strict";
"use strict";

var AcksinReferral = React.createClass({
  displayName: "AcksinReferral",

  getInitialState: function getInitialState() {
    return {};
  },
  componentDidMount: function componentDidMount() {
    $.get(BridgeAPI + "/v1/user", function (result) {
      this.setState(result);
    }.bind(this));
  },
  render: function render() {
    return React.createElement(
      "div",
      null,
      React.createElement(
        "p",
        null,
        "Send this link to your friends: ",
        React.createElement(
          "strong",
          null,
          "https://www.acksin.com/referral/?u=" + this.state.Username
        ),
        ". If they signup and purchase Acksin you get a ",
        React.createElement(
          "strong",
          null,
          "$29 dollar credit"
        ),
        " to your account."
      )
    );
  }
});
"use strict";

var ParkingSpotConsole = React.createClass({
  displayName: "ParkingSpotConsole",

  getInitialState: function getInitialState() {
    return {
      azs: [],
      az: QueryString.az == undefined ? 'us-west-2a' : QueryString.az,
      duration: QueryString.duration == undefined ? 2 : QueryString.duration,
      instanceTypes: []
    };
  },
  subscriptionLink: function subscriptionLink(name, link) {
    return React.createElement(
      "a",
      { href: link },
      name
    );
  },
  getAZs: function getAZs(az) {
    $.get("/v1/instance_types", function (result) {
      var its = [];

      for (var i = 0; i < result.length; i++) {
        its.push(React.createElement(ParkingSpotRow, { key: i, name: result[i], az: az, duration: this.state.duration }));
      }

      this.setState({
        instanceTypes: its
      });
    }.bind(this));

    $.get("/v1/availability_zones", function (result) {
      this.setState({
        azs: result
      });
    }.bind(this));
  },
  componentDidMount: function componentDidMount() {
    this.getAZs(this.state.az);

    $('#console-table').stupidtable();
  },
  render: function render() {
    return React.createElement(
      "div",
      { className: "row" },
      React.createElement(
        "div",
        { className: "col-md-12" },
        React.createElement(
          "div",
          { className: "card" },
          React.createElement(
            "div",
            { className: "header" },
            React.createElement(
              "h4",
              { className: "title" },
              this.state.az
            ),
            React.createElement(
              "form",
              { className: "form-inline" },
              React.createElement(
                "div",
                { className: "form-group" },
                React.createElement(
                  "label",
                  { "for": "az" },
                  "Availability Zone: "
                ),
                React.createElement(
                  "select",
                  { className: "form-control", id: "az", name: "az", defaultValue: this.state.az },
                  this.state.azs.map(function (name, index) {
                    return React.createElement(
                      "option",
                      { key: name },
                      name
                    );
                  })
                )
              ),
              React.createElement(
                "div",
                { className: "form-group" },
                React.createElement(
                  "label",
                  { "for": "duration" },
                  "Duration: "
                ),
                React.createElement("input", { className: "form-control", name: "duration", type: "text", defaultValue: this.state.duration }),
                " hours"
              ),
              React.createElement(
                "div",
                { className: "form-group" },
                React.createElement(
                  "button",
                  { name: "submit", type: "submit", className: "btn btn-primary" },
                  "Go"
                )
              )
            )
          ),
          React.createElement(
            "div",
            { className: "content table-responsive table-full-width" },
            React.createElement("div", { id: "chart_div" }),
            React.createElement(
              "table",
              { className: "table table-striped", id: "console-table" },
              React.createElement(
                "thead",
                null,
                React.createElement(
                  "tr",
                  null,
                  React.createElement(
                    "th",
                    null,
                    "Instance Type"
                  ),
                  React.createElement(
                    "th",
                    { "data-sort": "float" },
                    "OnDemand"
                  ),
                  React.createElement(
                    "th",
                    { "data-sort": "float" },
                    "Recommended Bid"
                  ),
                  React.createElement(
                    "th",
                    { "data-sort": "float" },
                    "Savings"
                  ),
                  React.createElement(
                    "th",
                    null,
                    "Launch"
                  )
                )
              ),
              React.createElement(
                "tbody",
                null,
                this.state.instanceTypes
              )
            )
          )
        )
      )
    );
  }
});
"use strict";

var ParkingSpotRow = React.createClass({
  displayName: "ParkingSpotRow",

  getInitialState: function getInitialState() {
    return {
      content: null
    };
  },
  roundPenny: function roundPenny(x) {
    return parseFloat(Math.round(x * 100) / 100);
  },
  getRow: function getRow() {
    this.serverRequest = $.get("/v1/spot/" + this.props.az + "/" + this.props.name + "/" + this.props.duration, function (result) {
      console.log(result);

      var content = React.createElement(
        "tr",
        null,
        React.createElement(
          "td",
          null,
          React.createElement(
            ReactRouter.Link,
            { to: "/instance/" + this.props.name },
            React.createElement(
              "b",
              null,
              this.props.name
            )
          )
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.OnDemandPrice },
          React.createElement(ParkingSpotOnDemand, { price: result.OnDemandPrice })
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.RecommendedBid },
          React.createElement(ParkingSpotRecommendedBid, { az: this.props.az, instanceType: this.props.name, price: this.roundPenny(result.RecommendedBid) })
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.Savings },
          React.createElement(ParkingSpotSavings, { percent: result.Savings })
        ),
        React.createElement(
          "td",
          null,
          React.createElement(ParkingSpotLaunch, { az: this.props.az, instanceType: this.props.name })
        )
      );

      this.setState({
        content: content
      });
    }.bind(this)).fail(function (e) {
      this.setState({
        content: null
      });
    }.bind(this));
  },
  componentDidMount: function componentDidMount() {
    this.getRow();
  },
  render: function render() {
    return this.state.content;
  }
});
"use strict";

var ParkingSpotCredentials = React.createClass({
  displayName: "ParkingSpotCredentials",

  render: function render() {
    return React.createElement(
      "div",
      { className: "row" },
      React.createElement(
        "div",
        { className: "col-md-12" },
        React.createElement(
          "div",
          { className: "card" },
          React.createElement(
            "div",
            { className: "header" },
            React.createElement(
              "h4",
              { className: "title" },
              "Credentials"
            )
          ),
          React.createElement(
            "div",
            { className: "content" },
            React.createElement(
              "p",
              null,
              "PARKINGSPOT_API_KEY"
            ),
            React.createElement(AcksinCredentials, null)
          )
        )
      )
    );
  }
});
"use strict";

var ParkingSpotDashboard = React.createClass({
  displayName: "ParkingSpotDashboard",

  getInitialState: function getInitialState() {
    return {
      user: {
        Username: ""
      }
    };
  },
  componentDidMount: function componentDidMount() {
    $.get("/v1/user", function (result) {
      this.setState({
        user: result
      });
    }.bind(this)).fail(function () {
      document.location = "https://www.parkingspot.bid/login/#auth";
    });

    $.get("/v1/subscription", function (result) {
      if (result == null) {
        $.notify({
          icon: 'ti-gift',
          message: "Hey! Thanks for checking out ParkingSpot. Just to let you know this version of ParkingSpot only has the Previous Generation of EC2 Machines as well as M3 and C3 instance types. Consider <a href='/billing'>subscribing</a> to get all the instances. Otherwise, enjoy cutting the costs of your infrastructure!"
        }, {
          type: 'success',
          timer: 4000
        });
      }
    }.bind(this));
  },
  render: function render() {
    return React.createElement(
      "div",
      { className: "wrapper" },
      React.createElement(Sidebar, null),
      React.createElement(
        "div",
        { className: "main-panel" },
        React.createElement(TopNav, { user: this.state.user }),
        React.createElement(
          "div",
          { className: "content" },
          React.createElement(
            "div",
            { className: "container-fluid" },
            this.props.children
          )
        ),
        React.createElement(ParkingSpotFooter, null)
      )
    );
  }
});
"use strict";

var ParkingSpotFooter = React.createClass({
  displayName: "ParkingSpotFooter",

  render: function render() {
    return React.createElement(
      "footer",
      { className: "footer" },
      React.createElement(
        "div",
        { className: "container-fluid" },
        React.createElement(
          "nav",
          { className: "pull-left" },
          React.createElement(
            "ul",
            null,
            React.createElement(
              "li",
              null,
              React.createElement(
                "a",
                { href: "https://www.acksin.com" },
                "Acksin"
              )
            ),
            React.createElement(
              "li",
              null,
              React.createElement(
                "a",
                { href: "https://blog.acksin.com", target: "_blank" },
                "Blog"
              )
            ),
            React.createElement(
              "li",
              null,
              React.createElement(
                "a",
                { href: "https://www.parkingspot.bid/#integrations", target: "_blank" },
                "Integrations"
              )
            )
          )
        ),
        React.createElement(
          "div",
          { className: "copyright pull-right" },
          "© 2016 ",
          React.createElement(
            "a",
            { href: "https://www.acksin.com" },
            "Acksin LLC"
          )
        )
      )
    );
  }
});
'use strict';

var ParkingSpotInstance = React.createClass({
  displayName: 'ParkingSpotInstance',

  getInitialState: function getInitialState() {
    return {
      azs: [],
      instanceType: this.props.params.instanceType,
      dataTable: [['Availability Zone', 'OnDemand', 'Price']]
    };
  },
  getAZs: function getAZs() {
    $.get("/v1/availability_zones", function (result) {
      var azs = [];
      this.getChartData(result);

      for (var i = 0; i < result.length; i++) {
        azs.push(React.createElement(ParkingSpotInstanceRow, { key: "parkingspot-instance-row" + i, instanceType: this.state.instanceType, az: result[i], duration: '1' }));
      }

      this.setState({
        azNames: result,
        azs: azs
      });
    }.bind(this));
  },
  componentDidMount: function componentDidMount() {
    this.getAZs();

    $('#instance-table').stupidtable();
  },
  getChartData: function getChartData(azNames) {
    for (var i = 0; i < azNames.length; i++) {
      $.get("/v1/spot/" + azNames[i] + "/" + this.state.instanceType + "/1", function (result) {
        console.log(result);
        this.state.dataTable.push([result.AZ, Number(result.OnDemandPrice == -1 ? 0 : result.OnDemandPrice), Number(result.Mean)]);
      }.bind(this));
    }
    /* google.charts.setOnLoadCallback(function() {
     *   var data = google.visualization.arrayToDataTable(this.state.dataTable);
     *   var options = {
     *     height: 400,
     *     chart: {
     *       title: 'OnDemand vs Average Price',
     *     }
     *   };
      *   var chart = new google.charts.Bar(document.getElementById('chart_div'));
     *   chart.draw(data, options);
     * }.bind(this));
     */
  },
  render: function render() {
    return React.createElement(
      'div',
      { className: 'row' },
      React.createElement(
        'div',
        { className: 'col-md-12' },
        React.createElement(
          'div',
          { className: 'card' },
          React.createElement(
            'div',
            { className: 'header' },
            React.createElement(
              'h4',
              { className: 'title' },
              this.state.instanceType
            )
          ),
          React.createElement(
            'div',
            { className: 'content table-responsive table-full-width' },
            React.createElement('div', { id: 'chart_div' }),
            React.createElement(
              'table',
              { className: 'table table-striped', id: 'instance-table' },
              React.createElement(
                'thead',
                null,
                React.createElement(
                  'tr',
                  null,
                  React.createElement(
                    'th',
                    null,
                    'Availability Zone'
                  ),
                  React.createElement(
                    'th',
                    { 'data-sort': 'float' },
                    'OnDemand'
                  ),
                  React.createElement(
                    'th',
                    { 'data-sort': 'float' },
                    'Recommended Bid'
                  ),
                  React.createElement(
                    'th',
                    { 'data-sort': 'float' },
                    'Savings'
                  ),
                  React.createElement(
                    'th',
                    null,
                    'Launch'
                  )
                )
              ),
              React.createElement(
                'tbody',
                null,
                this.state.azs
              )
            )
          )
        )
      )
    );
  }
});
"use strict";

var ParkingSpotInstanceRow = React.createClass({
  displayName: "ParkingSpotInstanceRow",

  getInitialState: function getInitialState() {
    return {
      content: null
    };
  },
  roundPenny: function roundPenny(x) {
    return parseFloat(Math.round(x * 100) / 100);
  },
  getRow: function getRow() {
    $.get("/v1/spot/" + this.props.az + "/" + this.props.instanceType + "/" + this.props.duration, function (result) {
      var content = React.createElement(
        "tr",
        null,
        React.createElement(
          "td",
          null,
          React.createElement(
            "a",
            { href: "#", onClick: this.updateChart },
            React.createElement(
              "b",
              null,
              this.props.az
            )
          )
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.OnDemandPrice },
          React.createElement(ParkingSpotOnDemand, { price: result.OnDemandPrice })
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.RecommendedBid },
          React.createElement(ParkingSpotRecommendedBid, { price: this.roundPenny(result.RecommendedBid) })
        ),
        React.createElement(
          "td",
          { "data-sort-value": result.Savings },
          React.createElement(ParkingSpotSavings, { percent: result.Savings })
        ),
        React.createElement(
          "td",
          null,
          React.createElement(ParkingSpotLaunch, { az: this.props.az, instanceType: this.props.instanceType })
        )
      );

      this.setState({
        content: content
      });
    }.bind(this));
  },
  componentDidMount: function componentDidMount() {
    this.getRow();
  },
  render: function render() {
    return this.state.content;
  }
});
'use strict';

function gaRouterUpdated() {
  window.ga('send', 'pageview', location.pathname);
}

var LoginFailed = React.createClass({
  displayName: 'LoginFailed',

  componentDidMount: function componentDidMount() {
    document.location = "https://www.parkingspot.bid/login/?failed=1";
  },
  render: function render() {
    return null;
  }
});

$(document).ready(function () {
  ReactDOM.render(React.createElement(
    ReactRouter.Router,
    { onUpdate: gaRouterUpdated, history: ReactRouter.browserHistory },
    React.createElement(
      ReactRouter.Route,
      { path: '/', component: ParkingSpotDashboard },
      React.createElement(ReactRouter.IndexRoute, { component: ParkingSpotConsole }),
      React.createElement(ReactRouter.Route, { path: 'instance/:instanceType', component: ParkingSpotInstance }),
      React.createElement(ReactRouter.Route, { path: 'billing', component: Billing }),
      React.createElement(ReactRouter.Route, { path: 'credentials', component: ParkingSpotCredentials })
    ),
    React.createElement(ReactRouter.Route, { path: '/auth', component: LoginFailed }),
    React.createElement(ReactRouter.Redirect, { from: '/console', to: '/' })
  ), document.getElementById("app"));
});
"use strict";

var Sidebar = React.createClass({
  displayName: "Sidebar",

  render: function render() {
    return React.createElement(
      "div",
      { className: "sidebar", "data-background-color": "white", "data-active-color": "danger" },
      React.createElement(
        "div",
        { className: "sidebar-wrapper" },
        React.createElement(
          "div",
          { className: "logo" },
          React.createElement(
            ReactRouter.Link,
            { to: "/", className: "simple-text" },
            "ParkingSpot"
          )
        ),
        React.createElement(
          "ul",
          { className: "nav" },
          React.createElement(
            "li",
            { className: "active" },
            React.createElement(
              ReactRouter.Link,
              { to: "/" },
              React.createElement("i", { className: "ti-panel" }),
              React.createElement(
                "p",
                null,
                "Console"
              )
            )
          ),
          React.createElement(
            "li",
            null,
            React.createElement(
              ReactRouter.Link,
              { to: "/credentials" },
              React.createElement("i", { className: "ti-view-list-alt" }),
              React.createElement(
                "p",
                null,
                "Credentials"
              )
            )
          )
        )
      )
    );
  }
});
"use strict";

var TopNav = React.createClass({
  displayName: "TopNav",


  render: function render() {
    return React.createElement(
      "nav",
      { className: "navbar navbar-default" },
      React.createElement(
        "div",
        { className: "container-fluid" },
        React.createElement(
          "div",
          { className: "navbar-header" },
          React.createElement(
            "button",
            { type: "button", className: "navbar-toggle" },
            React.createElement(
              "span",
              { className: "sr-only" },
              "Toggle navigation"
            ),
            React.createElement("span", { className: "icon-bar bar1" }),
            React.createElement("span", { className: "icon-bar bar2" }),
            React.createElement("span", { className: "icon-bar bar3" })
          ),
          React.createElement(
            "a",
            { className: "navbar-brand", href: "/" },
            "Dashboard"
          )
        ),
        React.createElement(
          "div",
          { className: "collapse navbar-collapse" },
          React.createElement(
            "ul",
            { className: "nav navbar-nav navbar-right" },
            React.createElement(
              "li",
              null,
              React.createElement(
                ReactRouter.Link,
                { to: "/billing" },
                React.createElement("i", { className: "ti-settings" }),
                " Settings"
              )
            ),
            React.createElement(
              "li",
              null,
              React.createElement(
                "a",
                { href: "/v1/logout" },
                React.createElement("i", { className: "ti-shift-right" }),
                " Logout"
              )
            )
          )
        )
      )
    );
  }
});
"use strict";

var ParkingSpotOnDemand = React.createClass({
  displayName: "ParkingSpotOnDemand",

  render: function render() {
    if (this.props.price == "-1" || this.props.price == "") {
      return React.createElement(
        "span",
        { "data-toggle": "tooltip", title: "No OnDemand price. This instance type is likely not a current generation type and hence is not available." },
        "N/A"
      );
    }

    return React.createElement(
      "span",
      null,
      "$",
      this.props.price
    );
  }
});

var ParkingSpotRecommendedBid = React.createClass({
  displayName: "ParkingSpotRecommendedBid",

  showChart: function showChart(e) {
    e.preventDefault();

    $.get("/v1/spot/hourly/" + this.props.az + "/" + this.props.instanceType, function (result) {
      var labels = [],
          price = [],
          ondemand = [],
          recommended = [];

      for (var i = 0; i < result.length; i++) {
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
      };

      new Chartist.Line('#chart_div', data, {
        plugins: [Chartist.plugins.tooltip(), Chartist.plugins.ctAxisTitle({
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
        })]
      });
    }.bind(this));
  },
  render: function render() {
    if (this.props.price == "nan" || this.props.price == "") {
      return React.createElement(
        "span",
        { "data-toggle": "tooltip", title: "We were unable to calculate an appropriate bid for this instance." },
        "N/A"
      );
    }

    return React.createElement(
      "a",
      { href: "#", onClick: this.showChart },
      "$",
      this.props.price
    );
  }
});

var ParkingSpotSavings = React.createClass({
  displayName: "ParkingSpotSavings",

  render: function render() {
    if (this.props.percent == "-1" || this.props.percent == "NaN") {
      return React.createElement(
        "span",
        { "data-toggle": "tooltip", title: "Savings are the savings over the OnDemand price." },
        "N/A"
      );
    }

    return React.createElement(
      "span",
      null,
      Math.round(this.props.percent) + '%'
    );
  }
});

var ParkingSpotLaunch = React.createClass({
  displayName: "ParkingSpotLaunch",

  render: function render() {
    var region = this.props.az.substring(0, this.props.az.length - 1);

    return React.createElement(
      "a",
      { target: "_blank", href: "https://" + region + ".console.aws.amazon.com/ec2sp/v1/spot/launch-wizard?region=" + region },
      "Launch"
    );
  }
});
