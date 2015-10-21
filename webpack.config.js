module.exports = {
  output: {
    filename: 'bundle.js',
  },
  module: {
    loaders: [{
      test: /\.vue$/,
      loader: 'vue'
    }]
  },
}
