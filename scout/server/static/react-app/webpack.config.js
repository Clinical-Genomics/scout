const webpack = require('webpack');
const config = {
	entry: {
      phenotypes: '/app/phenotypes/index.js',
      home: '/app/home/index.js'
    },
	output: {
		path: __dirname + '/dist',
		filename: '[name].js',
	},
	resolve: {
		extensions: ['.js', '.jsx', '.css']
	},

	module: {
		rules: [
			{
				test: /\.(js|jsx)?/,
				exclude: /node_modules/,
				loader: 'babel-loader',
				options: {
					presets: ['@babel/preset-env',
						'@babel/react']
				}
			},
			{
				test: /\.(png|svg|gif|jpg)$/,
				exclude: /node_modules/,
				use: ['file-loader']
			},
			{
				test: /\.css$/i,
				use: ['style-loader', 'css-loader'],
			},
			{
				test: /\.s[ac]ss$/i,
				use: [
					// Creates `style` nodes from JS strings
					'style-loader',
					// Translates CSS into CommonJS
					'css-loader',
					// Compiles Sass to CSS
					'sass-loader',
				],
			}
		]
	}
};
module.exports = config;
