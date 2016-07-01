# REDHAWK Basic Components rh.SigGen
 
## Description

Contains the source and build script for the REDHAWK Basic Components rh.SigGen.
A signal generator that creates different output signals based on its
configuration. It contains an implementation in each of the supported languages
(Python, C++, Java) as an example of a component with multiple implementations.

## Branches and Tags

All REDHAWK core assets use the same branching and tagging policy. Upon release,
the `master` branch is rebased with the specific commit released, and that
commit is tagged with the asset version number. For example, the commit released
as version 1.0.0 is tagged with `1.0.0`.

Development branches (i.e. `develop` or `develop-X.X`, where *X.X* is an asset
version number) contain the latest unreleased development code for the specified
version. If no version is specified (i.e. `develop`), the branch contains the
latest unreleased development code for the latest released version.

## REDHAWK Version Compatibility

| Asset Version | Minimum REDHAWK Version Required |
| ------------- | -------------------------------- |
| 2.x           | 2.0                              |
| 1.x           | 1.10                             |

## Installation Instructions
To build from source, run the `build.sh` script found at the top level
directory. To install to $SDRROOT, run `build.sh install`.

## Copyrights

This work is protected by Copyright. Please refer to the
[Copyright File](COPYRIGHT) for updated copyright information.

## License

REDHAWK Basic Components rh.SigGen is licensed under the GNU Lesser General
Public License (LGPL).
