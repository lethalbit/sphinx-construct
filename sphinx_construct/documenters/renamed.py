# SPDX-License-Identifier: BSD-3-Clause

from sphinx.ext.autodoc import ClassDocumenter
import construct

from ..consts            import DOMAIN

__all__ = (
	'RenamedAutodoc',
)

class RenamedAutodoc(ClassDocumenter):
	objtype       = 'renamed'
	directivetype = ClassDocumenter.objtype
	priority      = ClassDocumenter.priority + 100
	option_spec   = dict(ClassDocumenter.option_spec)

	@classmethod
	def can_document_member(cls, member, membername, isattr, parent):
		return isinstance(member, construct.Renamed)

	def add_directive_header(self, sig):
		super().add_directive_header(sig)
		obj = self.object
		self.add_line(f'   :type: AKA: "{obj.name}"', self.get_sourcename())




