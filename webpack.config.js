const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const path = require('path')

const HTMLWebpackPluginConfig = new HtmlWebpackPlugin({
  template: __dirname + '/src/index.html',
  filename: 'index.html',
  inject: 'body',
})

const config = {
  entry: './src/index.tsx',
  target: 'web',
  mode: 'development',
  output: {
    path: path.resolve(__dirname, './dist'),
    filename: 'bundle.js',
    publicPath: '/',
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
        loader: 'css-loader',
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
    extensions: ['.js', '.jsx', '.json', '.ts', '.tsx'],
  },
  plugins: [
    HTMLWebpackPluginConfig,
    new MiniCssExtractPlugin({
      filename: '[name].css',
    }),
  ],
}

module.exports = config
