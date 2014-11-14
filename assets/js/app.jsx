/** @jsx React.DOM */

// Browserify!
var React = require('react');
 
// Create a component, HelloMessage.
var HelloMessage = React.createClass({
  render: function() {
  	// Display a property.
    return <div>Hello {this.props.name}</div>;
  }
});

// Render HelloMessage component at #name.
React.render(
  <HelloMessage name="Robin" />,
  document.getElementById('name')
);
