/*global module:false*/
module.exports = function (grunt) {

	// Project configuration.
	grunt.initConfig({
		// Task configuration.
		jshint: {
			options: {
				curly: true,
				eqeqeq: true,
				immed: true,
				latedef: true,
				newcap: true,
				noarg: true,
				sub: true,
				undef: true,
				unused: true,
				boss: true,
				eqnull: true,
				browser: true,
				globals: {
					jQuery: true
				}
			},
			gruntfile: {
				src: 'Gruntfile.js'
			},
			lib_test: {
				src: ['lib/**/*.js', 'test/**/*.js']
			}
		},
		qunit: {
			files: ['test/**/*.html']
		},
		ngrok: {
			options: {
				authToken: process.env.NGROK_AUTH_TOKEN
			},
			server: {
				port:8080,
				subdomain: process.env.NGROK_SUBDOMAIN,
				onConnected: function (url) {
					grunt.log.writeln('Local server exposed to %s!', url);
				}
			}
		},
		watch: {
			gruntfile: {
				files: '<%= jshint.gruntfile.src %>',
				tasks: ['jshint:gruntfile']
			},
			lib_test: {
				files: '<%= jshint.lib_test.src %>',
				tasks: ['jshint:lib_test', 'qunit']
			},
			frontend: {
				options: {
					livereload: true
				},
				files: ['css/**/*.css', 'js/**/*.js', '*.html']
			}
		}
	});

	// These plugins provide necessary tasks.
	grunt.loadNpmTasks('grunt-contrib-qunit');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-watch');
	grunt.loadNpmTasks('grunt-ngrok');

	// Default task.
	grunt.registerTask('default', ['jshint', 'qunit']);

	// Watch task.
	grunt.registerTask('build', ['ngrok', 'watch']);

};
