var Card = React.createClass({
  render: function() {
    return (
      <div className={this.props.className}>
        <div className="card">
          <div className="header">
            <h4 className="title">{this.props.title}</h4>
            <p className="category">{this.props.category}</p>
          </div>

          <div className="content">
            {this.props.content}
          </div>
        </div>
      </div>
    );
  }
});
