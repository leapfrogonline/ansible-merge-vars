ansible-merge-vars Change Log

All notable changes to this project will be documented in this file.

The format is (loosely) based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## 2.0.1

Thanks again to @vladimir-mencl-eresearch for fixing a bug where dicts or lists definied in Jinja wouldn't be recursively merged.

## 2.0.0

Big thanks to @vladimir-mencl-eresearch for these additions and improvements!

Potentially breaking change (but you were very likely not depending on this):
- Merged variables are no longer being stored in the fact cache by default

New Features:
- Safety checks for the merged_var_name parameter
- Recursive dict merging
- Documentation updates

## 1.0.0

- Initial version with all functionality and documentation
