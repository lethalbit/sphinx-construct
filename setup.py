# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup, find_packages

def vcs_ver():
	def scheme(version):
		if version.tag and not version.distance:
			return version.format_with("")
		else:
			return version.format_choice("+{node}", "+{node}.dirty")
	return {
		"relative_to": __file__,
		"version_scheme": "guess-next-dev",
		"local_scheme": scheme
	}

def doc_ver():
	try:
		from setuptools_scm.git import parse as parse_git
	except ImportError:
		return ""

	git = parse_git(".")
	if not git:
		return ""
	elif git.exact:
		return git.format_with("{tag}")
	else:
		return "latest"

setup(
	name = 'sphinx-construct',
	use_scm_version = vcs_ver(),
	author          = 'Aki \'lethalbit\' Van Ness',
	author_email    = 'nya@catgirl.link',
	description     = 'A sphinx extension to generate good-looking documentation from Construct objects',
	license         = 'BSD-3-Clause',
	python_requires = '~=3.10',
	zip_safe        = False,

	setup_requires  = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires = [
		'Jinja2',
		'construct>=2.10.70',
		'executing'
	],

	packages = find_packages(),
	package_data = {
		'sphinx_construct.assets': [
			'sphinx_construct.css',
		]
	},

	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: BSD License',

		'Intended Audience :: Developers',

		'Operating System :: OS Independent',

		'Programming Language :: Python',
		'Programming Language :: Python :: 3',

		'Topic :: Documentation',
		'Topic :: Utilities',

		'Framework :: Sphinx',
		'Framework :: Sphinx :: Extension',
	],

	project_urls = {
		'Documentation': 'https://github.com/lethalbit/sphinx-construct',
		'Source Code'  : 'https://github.com/lethalbit/sphinx-construct',
		'Bug Tracker'  : 'https://github.com/lethalbit/sphinx-construct/issues',
	}
)
