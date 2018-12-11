var TopNav = React.createClass({

  render: function() {
    return (
      <nav className="navbar navbar-default">
        <div className="container-fluid">
          <div className="navbar-header">
            <button type="button" className="navbar-toggle">
              <span className="sr-only">Toggle navigation</span>
              <span className="icon-bar bar1"></span>
              <span className="icon-bar bar2"></span>
              <span className="icon-bar bar3"></span>
            </button>
            <a className="navbar-brand" href="/">Dashboard</a>
          </div>
          <div className="collapse navbar-collapse">
            <ul className="nav navbar-nav navbar-right">
              <li>
                <ReactRouter.Link to="/billing">
                  <i className="ti-settings"></i> Settings
                </ReactRouter.Link>
              </li>
              <li>
                <a href="/v1/logout">
                  <i className="ti-shift-right"></i> Logout
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    );
  }
});
