Scott's Jekyll Build System
===========================

This is Scott Severance's build system for Jekyll websites. It supports the
following features:

* Development and production targets
* Deployment using Octopress
* Minifies HTML and JavaScript in production, deployment, or when not watching
  or generating incremental builds. CSS minification can be handled by Jekyll
  itself. Configure this through the configuration file.
* Uses Jekyll's --incremental and --watch options by default, but these can be
  turned off. Can optionally run the Jekyll server.
* Automatically or manually generates ctags, ignoring the `_site` directory.
* Handles Git pushing to multiple remotes.
* On Windows, will launch XAMPP's Apache server

I'm releasing it publicly in case anyone finds it useful. However, its features
are primarily motivated by my own needs. Pull requests are welcome if you want
to improve it. Otherwise, feel free to fork it if you need to modify it for your
own purposes.

I run this build system on both Linux (primarily) and Windows (occasionally). It
works in both places. In theory, it should run on any system which supports the
dependencies. However, I haven't tested this theory. In particular, I don't know
whether it will run on MacOS. (I'll accept a donated Mac in order to ensure
compatibility. 😊

Dependencies
------------

* Python 3.6 or newer
* The Python module `htmlmin` (you can install it with `pip`)
* Bash. On Windows, Git Bash has been tested, and it is unknown whether other
  ways of installing/using Bash will work. On other OSes, the default Bash
  ought to work.
* A properly set up Jekyll site which can be called using `bundle exec jekyll`
* Octopress (for deployments)

The following Gemfile is known to work:

    # A sample Gemfile
    source "https://rubygems.org"

    gem "jekyll", '= 3.8.4'
    gem 'octopress', '~> 3.0'
    gem 'wdm', '>= 0.1.0' if Gem.win_platform?

Installation
------------

1. Clone this respository anywhere you like. You can place it in a central
   location and refer to it from all your Jekyll projects, or you can add it to
   your project as a Git submodule.

2. Copy `build_config_sample.json` to your project's base directory and call it
   `_build_config.json`. Feel free to check this file into your project's source
   control.

3. Edit `_build_config.json` to set the appropriate configuration options. for
   documentation on the "minify_options" key, run `minify_html_js.py --help`.

4. **Optional:** Symlink `build` into your project's root directory. _Important:_
   Symlink it; don't copy it. Otherwise, the build script won't be able to find
   its support files.

Usage
-----

For normal development, run `./build` with no arguments. To deploy, run
`./build --deploy`. For more detailed documentation, run `./build --help`.
