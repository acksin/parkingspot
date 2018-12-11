var AcksinPage = React.createClass({
  getInitialState: function() {
    return {
      content: {
        __html: ""
      }
    };
  },
  componentDidMount: function() {
    $.get(this.props.page, function(response) {
      this.setState({
        content: {
          __html: response
        }
      });
    }.bind(this));
  },
  render: function() {
    return (
      <div dangerouslySetInnerHTML={this.state.content}></div>
    );
  }
});

var AcksinOrgPage = React.createClass({
  getInitialState: function() {
    return {
      content: {
        __html: ""
      }
    };
  },
  componentDidMount: function() {
    $.get(this.props.page, function(response) {

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
  render: function() {
    return (
      <div dangerouslySetInnerHTML={this.state.content}></div>
    );
  }
});


var AcksinPrivacyPage = React.createClass({
  render: function() {
    return <AcksinPage page="/a/privacy.html" />;
  }
});

var AcksinTOSPage = React.createClass({
  render: function() {
    return <AcksinPage page="/a/tos.html" />;
  }
});
