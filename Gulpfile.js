/* gulpfile.js */

'use strict';

// Load some modules which are installed through NPM.
var gulp         = require('gulp');
var browserify   = require('browserify');  // Bundles JS.
var reactify     = require('reactify');  // Transforms React JSX to JS.
var source       = require('vinyl-source-stream');
var transform    = require('vinyl-transform');
var sass         = require('gulp-sass');  // To compile Stylus CSS.
var browserSync  = require('browser-sync');
var reload       = browserSync.reload;
var autoprefixer = require('gulp-autoprefixer');
var uglify       = require('gulp-uglify');
var concat       = require('gulp-concat');

// Define some paths.
var paths = {
  app_scss: ['./assets/scss/styles.scss'],
  scss: ['./assets/scss/**/*.scss'],
  app_js: ['./assets/js/app.jsx'],
  js: ['./assets/js/*.js', './assets/js/app.jsx'],
};

// Browser-sync task, only cares about compiled CSS
gulp.task('browser-sync', function() {
  browserSync({
    files: ['scout/static/css/*.css', 'scout/static/js/*.js'],
    proxy: { port: 5000 },
  });
});

// Our CSS task. It finds all our Stylus files and compiles them.
gulp.task('css', function() {
  return gulp.src(paths.app_scss)
    .pipe(sass({ errLogToConsole: true }))
    .pipe(autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }))
    .pipe(gulp.dest('./scout/static/css/'))
    .pipe(reload({ stream: true }));
});

// Our JS task. It will Browserify our code and compile React JSX files.
gulp.task('js', function() {

  var browserified = transform(function(filename) {
    var b = browserify(filename);
    b.transform(reactify);
    return b.bundle();
  });

  // Browserify/bundle the JS.
  return gulp.src(paths.app_js)
    .pipe(browserified)
    .pipe(concat('bundle.js'))
    .pipe(gulp.dest('./scout/static/js/'))
    .pipe(reload({ stream: true }));
});

// Rerun tasks whenever a file changes.
gulp.task('watch', function() {
  gulp.watch(paths.scss, ['css']);
  gulp.watch(paths.js, ['js']);
});

// The default task (called when we run `gulp` from cli)
gulp.task('default', ['watch', 'css', 'js', 'browser-sync']);
