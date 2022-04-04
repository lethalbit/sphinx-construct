# SPDX-License-Identifier: BSD-3-Clause
from sphinx.util        import logging
from sphinx.ext.autodoc import Documenter
import construct

from ..consts           import DOMAIN, FIELD_ENDAIN, FIELD_SPEC
from ..consts           import (
	Signedness, Endian, Size, Alignment
)


log = logging.getLogger(__name__)

__all__ = (
	'SubconstructDocumenter',
)

_documented_subcon_instances = []

class SubconstructDocumenter(Documenter):
	# domain         = DOMAIN
	objtype          = 'subconstruct'
	directivetype    = Documenter.objtype
	directivetype    = 'attribute'
	priority         = Documenter.priority + 100
	option_spec      = dict(Documenter.option_spec)
	titles_allowed   = True
	_subcon_handlers = {}

	def add_line(self, l, s, *ln):
		super().add_line(l, s, *ln)

		self._rst.append(l)

	def __init__(self, *args, **kwargs):
		self._rst = []
		super().__init__(*args, **kwargs)

		self._subcon_handlers = {
			construct.Enum          : self._enum_handler,
			construct.Renamed       : self._renamed_handler,
			construct.Transformed   : self._transformed_handler,
			construct.BitsInteger   : self._numeric_handler,
			construct.BytesInteger  : self._numeric_handler,
			construct.Flag.__class__: self._empty_handler,
			construct.FormatField   : self._formatfield_handler,
			construct.Switch        : self._switch_handler,
			construct.Struct        : self._struct_handler,
			construct.Pass.__class__: self._empty_handler,
		}

	def __del__(self):
		with open(f'{self.object.name}_rst_dump.rst'.replace('/', '_').replace(' ', '_'), 'w') as f:
			f.write('\n'.join(self._rst))

	def _documented_instance(self, obj):
		if obj in _documented_subcon_instances:
			return obj
		return None

	def _sanitize_name(self, txt):
		tgt_chars = (' ', '.', '<', '>', ':')
		return ''.join(map(lambda c: c if c not in tgt_chars else '_', list(txt))).lower()

	def _mk_tgt_name(self, obj):
		return f'{self._sanitize_name(self.modname)}_{self._sanitize_name(obj.name)}'

	# Unwraps one-level container names
	def _typename(self, obj):
		containers = (
			construct.Renamed,
			construct.Transformed,
		)

		if isinstance(obj, containers):
			obj = obj.subcon

		return obj.__class__.__name__

	# Attempts to get the name of a value
	def _valname(self, obj):
		containers = (
			construct.Renamed,
		)

		if isinstance(obj, containers):
			return obj.name

		return obj.name

	def append(self, text = None):
		if text is not None:
			self.add_line(f'{self.indent}{text}', self.get_sourcename())
		else:
			self.add_line('', self.get_sourcename())

	def _recuse(self, obj):
		if obj in _documented_subcon_instances:
			return

		old_indent = self.indent
		self.indent = f'{old_indent}   '
		if hasattr(obj, 'subcons'):
			for sc in obj.subcons:
				self._subcon_handlers.get(type(sc), self._default_handler)(sc)

		elif hasattr(obj, 'subcon'):
			self._subcon_handlers.get(type(obj.subcon), self._default_handler)(obj.subcon)

		self.indent = old_indent
		_documented_subcon_instances.append(obj)

	# -- Type Handlers -- #

	def _enum_handler(self, obj, _ = None):
		size   = obj.subcon.sizeof()
		do_hex = (size & 3) == 0
		base   = 'x' if do_hex else 'b'
		size   = (size >> 2) if do_hex else size

		def _val_to_str(value):
			return f'0{base}{value:0{size}{base}}'


		for v, k in obj.ksymapping.items():
			self.append(f'.. py:attribute:: {str(self.name).replace("::", ".")}.{k}')
			self.append(f'   :type: {obj.subcon.__class__.__name__}<{size}>')
			self.append(f'   :value: {_val_to_str(v)}')
			self.append()

		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

	def _renamed_handler(self, obj, is_header = False):
		if is_header:
			# self.append(f'.. py:attribute:: {obj.name}')
			# self.append(f'   :module: {self.modname}')
			self.append(f'   :type: {self._typename(obj.subcon)}')
		else:
			di = self._documented_instance(obj)
			if di is None:
				# self.append(f'.. _{self._mk_tgt_name(obj)}:')
				self.append()
				self.append(f'.. py:attribute:: {obj.name}')
				self.append(f'   :type: {self._typename(obj.subcon)}')
				self.append( '   :noindex:')
				self.append()
				self._recuse(obj)
			else:
				self.append(f'`See: "{obj.name}" <{self._mk_tgt_name(obj)}>`_')
				self.append()


	# Unwrap the construct.core.Transformed subcon
	def _transformed_handler(self, obj, _ = None):
		self._recuse(obj.subcon)

	def _numeric_handler(self, obj, _ = None):
		signedness = 'Signed' if obj.signed else 'Unsigned'
		if isinstance(obj, construct.BitsInteger):
			unit = 'bit'
		elif isinstance(obj, construct.BytesInteger):
			unit = 'byte'

		self.append(f'{signedness} {obj.sizeof()} {unit} integer.')
		self.append()

		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

	def _formatfield_handler(self, obj, _ = None):
		endian = FIELD_ENDAIN[obj.fmtstr[0]]['endian']
		specs  = list(map(lambda s: FIELD_SPEC[s], obj.fmtstr[1:]))

		self.append(f'**Endian:** {endian!s}')
		self.append()
		self.append(f'**Size:** {obj.length}')
		self.append()
		self.append(f'**Underlying Types:**')
		self.append()
		for s in specs:
			self.append(f'  Type: {s["ptype"]}')
			self.append()
			self.append(f'  Size: {s["std_size"]}')
			self.append()
			self.append(f'  Sign: {s["signed"]!s}')
			self.append()

		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

	def _switch_handler(self, obj, _ = None):
		def _recompose_keyfunc(func):
			return func

		key = _recompose_keyfunc(obj.keyfunc)

		for k, v in obj.cases.items():
			self.append(f'.. py:attribute:: {self._typename(v)}')
			self.append(f'   :type: {self._valname(v)}')
			self.append(f'   :value: {k}')
			self.append( '   :noindex:')
			self.append()
			self._recuse(v)


		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

	def _struct_handler(self, obj, _ = None):
			for s in obj.subcons:
				self.append(f'.. py:attribute:: {self._typename(s)}')
				self.append(f'   :type: {self._valname(s)}')
				self.append( '   :noindex:')
				self.append()
				self._recuse(s)

			if hasattr(obj, 'docs'):
				self.append(obj.docs)
				self.append()


	# The default handler for things we miss
	def _default_handler(self, obj, _ = None):
		log.warning(f'No specialized handling for {type(obj)}', color = 'yellow')
		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

		self._recuse(obj)

	# Not quite the default handler, but an empty handler
	# for type that don't have special parsing needs
	def _empty_handler(self, obj, _ = None):
		if hasattr(obj, 'docs'):
			self.append(obj.docs)
			self.append()

		# self._recuse(obj)


	# -- Sphinx Documenter boilerplate bits -- #

	@classmethod
	def can_document_member(cls, member, membername, isattr, parent):
		return isinstance(member, construct.Subconstruct)

	def add_directive_header(self, sig):
		super().add_directive_header(sig)
		self._subcon_handlers.get(type(self.object), self._default_handler)(self.object, True)

	def add_content(self, content, no_docstring = False):
		super().add_content(content, no_docstring)
		self._subcon_handlers.get(type(self.object), self._default_handler)(self.object)

	def resolve_name(self, modname, parents, path, base):
		return modname, parents + [base]


