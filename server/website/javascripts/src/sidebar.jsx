var Sidebar = React.createClass({
  render: function() {
    return (
      <div className="sidebar" data-background-color="white" data-active-color="danger">
        <div className="sidebar-wrapper">
          <div className="logo">
            <ReactRouter.Link to="/" className="simple-text">
              ParkingSpot
            </ReactRouter.Link>
          </div>

          <ul className="nav">
            <li className="active">
              <ReactRouter.Link to="/">
                <i className="ti-panel"></i>
                <p>Console</p>
              </ReactRouter.Link>
            </li>
            <li>
              <ReactRouter.Link to="/credentials">
                <i className="ti-view-list-alt"></i>
                <p>Credentials</p>
              </ReactRouter.Link>
            </li>
          </ul>
        </div>
      </div>
    );
  }
});
