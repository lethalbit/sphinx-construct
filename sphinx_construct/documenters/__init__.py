# SPDX-License-Identifier: BSD-3-Clause

from .subcon  import SubconstructDocumenter

__all__ = (
	'register_documenters',
)

def register_documenters(app = None):
	if app is None:
		raise ValueError(f'Application must be set')

	app.add_autodocumenter(SubconstructDocumenter)


