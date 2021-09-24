const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const path = require('path')
const webpack = require('webpack')

const HTMLWebpackPluginConfig = new HtmlWebpackPlugin({
	template: __dirname + '/src/index.html',
	filename: 'index.html',
	inject: 'body',
})

const config = {
	entry: {
		home: '/src/modules/Home/index.tsx',
		phenotypesPage: '/src/modules/PhenotypesPage/index.tsx',
		appShell: './src/index.tsx',
	},
	target: 'web',
	mode: 'development',
	output: {
		path: path.resolve(__dirname, './build'),
		filename: '[name].js',
		publicPath: '/',
	},
	devServer: {
		port: 3000,
		host: '0.0.0.0',
		allowedHosts: ['all'],
		disableHostCheck: true,
		historyApiFallback: true,
		contentBase: './',
		hot: true,
	},
	module: {
		rules: [
			{
				test: /\.(js|jsx)$/,
				use: 'babel-loader',
				exclude: /node_modules/,
			},
			{
				test: /\.(ts|tsx)$/,
				loader: 'awesome-typescript-loader',
			},
			{
				test: /\.css$/,
				use: [
					MiniCssExtractPlugin.loader, // instead of style-loader
					'css-loader',
				],
			},
			{
				test: /\.(png|jpe?g|gif)$/i,
				use: [
					{
						loader: 'file-loader',
					},
				],
			},
		],
	},
	resolve: {
		modules: [path.resolve(__dirname, './src'), 'node_modules'],
		extensions: ['.js', '.jsx', '.json', '.ts', '.tsx'],
		alias: {
			process: 'process/browser',
			stream: 'stream-browserify',
			zlib: 'browserify-zlib',
		},
	},
	plugins: [
		HTMLWebpackPluginConfig,
		new MiniCssExtractPlugin({
			filename: '[name].css',
		}),
		new webpack.DefinePlugin({
			'process.env.GOOGLE_OAUTH_CLIENT_ID': JSON.stringify(process.env.GOOGLE_OAUTH_CLIENT_ID),
			'process.env.BACKEND_URL': JSON.stringify(process.env.BACKEND_URL),
			'process.env.MOCK': JSON.stringify(process.env.MOCK),
		}),
		new webpack.EnvironmentPlugin(['GOOGLE_OAUTH_CLIENT_ID', 'BACKEND_URL', 'MOCK']),
		new webpack.ProvidePlugin({
			process: 'process/browser',
			Buffer: ['buffer', 'Buffer'],
		}),
	],
}

module.exports = config
