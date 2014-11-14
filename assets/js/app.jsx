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

var ToggleClassButton = React.createClass({
	query: '',
	toggleClass: '',

	handleClick: function() {
		var element = document.querySelector(this.props.query);
		return element.classList.toggle(this.props.toggleClass)
	},

	render: function() {
		return <div onClick={this.handleClick} className="button-menu"></div>
	}
});

// Render HelloMessage component at #name.
React.render(
  <ToggleClassButton icon="menu" query=".drawer-panel-aside" toggleClass="is-showing" />,
  document.getElementById('menu-button')
);
