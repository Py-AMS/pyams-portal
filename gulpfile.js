
const { src, dest, task, watch, parallel } = require('gulp');

const clean = require('gulp-clean-css');
const rename = require('gulp-rename');
const sass = require('gulp-sass')(require('node-sass'));


task('sass_dev', function() {
    return src('src/pyams_portal/zmi/resources/sass/layout.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(dest('src/pyams_portal/zmi/resources/css/'));
});

task('sass', function() {
    return src('src/pyams_portal/zmi/resources/sass/layout.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(clean())
        .pipe(rename('layout.min.css'))
        .pipe(dest('src/pyams_portal/zmi/resources/css/'));
});


exports.sass_dev = task('sass_dev');
exports.sass_prod = task('sass');


exports.default = function() {
	watch('src/pyams_portal/zmi/resources/sass/*.scss',
		parallel('sass_dev', 'sass'));
};
