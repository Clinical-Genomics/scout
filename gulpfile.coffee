gulp = require 'gulp'
sass = require 'gulp-sass'
autoprefixer = require 'gulp-autoprefixer'
browserSync = require 'browser-sync'
reload = browserSync.reload
webpack = require 'gulp-webpack'
webpackConfig = require './webpack.config.js'
minify = require 'gulp-minify-css'
uglify = require 'gulp-uglify'
gulpif = require 'gulp-if'
argv = require('yargs').argv


# browser-sync task, only cares about compiled CSS
gulp.task 'browser-sync', ->
	browserSync
		files: ['build/*.css', 'build/*.js']
		proxy:
			port: 5000


# CSS task - finds and compiles all SCSS files
gulp.task 'css', ->
	return gulp.src './assets/scss/style.scss'
		.pipe sass { errLogToConsole: yes }
		.pipe autoprefixer
			browsers: ['last 2 versions']
			cascade: no
		.pipe gulpif argv.production, minify()
		.pipe gulp.dest 'build/'
		.pipe reload { stream: yes }


# bundle Vue.js template and scripts
gulp.task 'webpack', ->
	myConfig = Object.create webpackConfig

	return gulp.src 'assets/coffee/main.js'
		.pipe webpack myConfig
		.pipe gulpif argv.production, uglify()
		.pipe gulp.dest 'build/'
		.pipe reload { stream: yes }


# rerun tasks whenever a file changes.
gulp.task 'watch', ->
	gulp.watch 'assets/scss/**/*.scss', ['css']
	gulp.watch 'assets/coffee/**/*.{coffee,vue,js}', ['webpack']


# default task (called when we run `gulp` from cli)
gulp.task 'default', ['watch', 'css', 'webpack', 'browser-sync']
gulp.task 'build', ['css', 'webpack']
