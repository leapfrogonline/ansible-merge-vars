ansible-merge-vars Change Log

All notable changes to this project will be documented in this file.

The format is (loosely) based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## 4.0.0

Big thanks again to @vladimir-mencl-eresearch for this improvement!

Potentially breaking change:
- Merge order is now deterministic (alphabetical by fact name).  Hopefully you
  weren't depending on the order in which your facts were merged, but if you
  were, this may change that order.  At least from now on it will be the same
  every time.

## 3.0.0

This plugin is now installable from PyPI, which will make it easier to keep
updated with bug fixes and new features.  As a result, the installation process
is different.  The README has the updated installation process.  If you are
currently using this plugin, you will want to install this version using the
new installation process.

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
