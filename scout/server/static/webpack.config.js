const webpack = require('webpack');
const config = {
	entry:  __dirname + '/scripts/index.js',
	output: {
		path: __dirname + '/dist',
		filename: 'bundle.js',
	},
	resolve: {
		extensions: ['.js', '.jsx', '.css']
	},
	module: {
		rules: [
			{
			test: /\.(js|jsx)?/,
				exclude: /node_modules/,
				use: 'babel-loader'
			},
			{
				test: /\.(png|svg|jpg|gif)$/,
				use: 'file-loader'
			}
		]
	}
};
module.exports = config;
