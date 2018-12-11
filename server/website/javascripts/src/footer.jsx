var ParkingSpotFooter = React.createClass({
  render: function() {
    return (
      <footer className="footer">
        <div className="container-fluid">
          <nav className="pull-left">
            <ul>
              <li>
                <a href="https://www.acksin.com">
                  Acksin
                </a>
              </li>
              <li>
                <a href="https://blog.acksin.com" target="_blank">
                  Blog
                </a>
              </li>
              <li>
                <a href="https://www.parkingspot.bid/#integrations" target="_blank">
                  Integrations
                </a>
              </li>
            </ul>
          </nav>
          <div className="copyright pull-right">
            &copy; 2016 <a href="https://www.acksin.com">Acksin LLC</a>
          </div>
        </div>
      </footer>
    );
  }
});
