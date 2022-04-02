# SPDX-License-Identifier: BSD-3-Clause
from pathlib              import Path
from importlib            import resources

from sphinx.util.fileutil import copy_asset
__all__ = (
	'init_asstes',
)


ASSETS = [
	'sphinx_construct.css',
]

def _copy_asset(app, e):
	if e is None:
		for asset in filter(lambda a: a.split('.')[-1] == 'css', ASSETS):
			with resources.path(__name__, asset) as a:
				copy_asset(str(a), str(Path(app.outdir) / '_static'))

		for asset in filter(lambda a: a.split('.')[-1] == 'js', ASSETS):
			with resources.path(__name__, asset) as a:
				copy_asset(str(a), str(Path(app.outdir) / '_static'))


def init_asstes(app = None):
	if app is None:
		raise ValueError(f'Application must be set')

	for asset in filter(lambda a: a.split('.')[-1] == 'css', ASSETS):
		app.add_css_file(asset)

	for asset in filter(lambda a: a.split('.')[-1] == 'js', ASSETS):
		app.add_js_file(asset)

	app.connect('build-finished', _copy_asset)
