# +--------------------------------------------------------------------+
# | gulp.js config to compile frontend assets
# +--------------------------------------------------------------------+
gulp = require 'gulp'
sass = require 'gulp-sass'
autoprefixer = require 'gulp-autoprefixer'
browserSync = require 'browser-sync'
reload = browserSync.reload
minify = require 'gulp-minify-css'
gulpif = require 'gulp-if'
argv = require('yargs').argv


# browser-sync task, only cares about compiled CSS
gulp.task 'browser-sync', ->
    browserSync
        files: ['build/*.css', 'build/*.js']
        proxy: 'localhost:5023'


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


# rerun tasks whenever a file changes.
gulp.task 'watch', ->
	gulp.watch 'assets/scss/**/*.scss', ['css']


# default task (called when we run `gulp` from cli)
gulp.task 'default', ['watch', 'css', 'webpack', 'browser-sync']
gulp.task 'build', ['css']
