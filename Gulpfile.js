'use strict';

/**
 * This example:
 *  Shows how to plug in the details of your server.
 *  Watches & injects CSS files
 */
var gulp         = require('gulp');
var browserSync  = require('browser-sync');
var reload       = browserSync.reload;
var sass         = require('gulp-sass');
var bourbon      = require('node-bourbon');
var autoprefixer = require('gulp-autoprefixer');
var vulcanize    = require('gulp-vulcanize');
var replace      = require('gulp-replace');

// Base target directory
base_dir = 'scout/static'

// Browser-sync task, only cares about compiled CSS
gulp.task('browser-sync', function() {
  browserSync({
    files: base_dir + '/css/*.css',
    proxy: {
      port: 5000,
    },
  });
});

// Copy static assets
gulp.task('bs-reload', function () {
  gulp.src('assets/*.html')
    .pipe(gulp.dest(base_dir))
    .pipe(reload({stream: true}))
});

// Sass task, will run when any SCSS files change.
gulp.task('sass', function () {
  gulp.src('assets/scss/styles.scss')
    .pipe(sass({ errLogToConsole: true }))
    .pipe(autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }))
    .pipe(gulp.dest(base_dir + '/css/'))
    .pipe(reload({stream: true}));
});

// Vulcanize Polymer elements
gulp.task('vulcanize', function () {
  return gulp.src('assets/elements.html')
    .pipe(vulcanize({
        dest: 'scout/templates',
        strip: true,  // Remove comments and empty text nodes
        inline: true,
    }))
    .pipe(replace(/<html><head>/, '{% raw %}'))
    .pipe(replace(/<\/body><\/html>/, '{% endraw %}'))
    .pipe(replace(/<\/head><body>/, ''))
    .pipe(gulp.dest('scout/templates'));
});

// Default task to be run with `gulp`
gulp.task('default', ['sass', 'browser-sync'], function () {
  gulp.watch('assets/scss/**/*.scss', ['sass']);
  gulp.watch('assets/*.html', ['bs-reload']);
});
