# SPDX-License-Identifier: BSD-3-Clause
from sphinx.ext.autodoc import (
	Documenter, ModuleDocumenter,
	ModuleLevelDocumenter, ClassLevelDocumenter
)

__all__ = (
	'register_documenters',
	'SubconAutodoc',
	'StructAutodoc',
	'EnumAutodoc',

)

_DOMAIN = 'sphinx-construct'

class ConstructAutodoc(Documenter):
	domain = _DOMAIN


class SubconAutodoc(ConstructAutodoc, ClassLevelDocumenter):
	objtype = 'subcon'

class StructAutodoc(ConstructAutodoc, ModuleLevelDocumenter):
	objtype = 'struct'

class ModuleAutodoc(ConstructAutodoc, ModuleDocumenter):
	pass



def register_documenters(app = None):
	if app is None:
		raise ValueError(f'Application must be set')

	app.add_autodocumenter(ModuleAutodoc)
	app.add_autodocumenter(StructAutodoc)
	app.add_autodocumenter(SubconAutodoc)


