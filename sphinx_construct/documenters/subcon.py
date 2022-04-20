# SPDX-License-Identifier: BSD-3-Clause
from sphinx.util        import logging
from sphinx.ext.autodoc import ModuleLevelDocumenter
from enum import IntEnum, unique, auto
from typing import Union
import construct

from ..consts           import DOMAIN, FIELD_ENDAIN, FIELD_SPEC
from ..consts           import (
	Signedness, Endian, Size, Alignment
)


log = logging.getLogger(__name__)

__all__ = (
	'SubconstructDocumenter',
)

_documented_subcon_instances = {}

@unique
class SizeMode(IntEnum):
	BYTES = auto()
	BITS = auto()

class SubconstructDocumenter(ModuleLevelDocumenter):
	# domain         = DOMAIN
	objtype          = 'subconstruct'
	directivetype    = 'attribute'
	priority         = ModuleLevelDocumenter.priority + 100
	option_spec      = dict(ModuleLevelDocumenter.option_spec)
	titles_allowed   = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.size_mode = SizeMode.BYTES
		self._subcon_handlers = {
			construct.Enum          : self._enum_handler,
			construct.FlagsEnum     : self._flags_enum_handler,
			construct.Renamed       : self._renamed_handler,
			construct.Transformed   : self._transformed_handler,
			construct.Restreamed    : self._restreamed_handler,
			construct.BitsInteger   : self._numeric_handler,
			construct.BytesInteger  : self._numeric_handler,
			construct.Flag.__class__: self._empty_handler,
			construct.FormatField   : self._formatfield_handler,
			construct.Switch        : self._switch_handler,
			construct.Struct        : self._struct_handler,
			construct.Pass.__class__: self._empty_handler,
			construct.Const         : self._const_handler,
			construct.Padded        : self._padded_handler,
			construct.Rebuild       : self._rebuild_handler,
			construct.GreedyRange   : self._greedy_range_handler,
		}

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
			construct.Restreamed,
		)

		prefix = ''
		while isinstance(obj, containers):
			if (
				(isinstance(obj, construct.Transformed) and obj.decodefunc == construct.bytes2bits) or
				(isinstance(obj, construct.Restreamed) and obj.decoder == construct.bytes2bits)
			):
				prefix = 'Bit'
			elif (
				(isinstance(obj, construct.Transformed) and obj.decodefunc == construct.bits2bytes) or
				(isinstance(obj, construct.Restreamed) and obj.decoder == construct.bits2bytes)
			):
				prefix = ''
			obj = obj.subcon

		return f'{prefix}{obj.__class__.__name__}'

	# Attempts to get the name of a value
	def _valname(self, obj : construct.Construct):
		return f'{self.name}.{obj.name}'

	def append(self, text = None):
		if text is not None:
			self.add_line(f'{self.indent}{text}', self.get_sourcename())
		else:
			self.add_line('', self.get_sourcename())

	def _recuse(self, obj, indent : bool = True):
		if obj in _documented_subcon_instances:
			name = _documented_subcon_instances[obj]
			self.append()
			self.append(f'   See: :py:attr:`{name}`')
			return

		if indent:
			old_indent = self.indent
			self.indent = f'{old_indent}   '
		if obj.name is not None:
			name = self.name
			self.name = f'{name}.{obj.name}'

		if hasattr(obj, 'subcons'):
			for sc in obj.subcons:
				self.append()
				self._subcon_handlers.get(type(sc), self._default_handler)(sc)

		elif hasattr(obj, 'subcon'):
			self._subcon_handlers.get(type(obj.subcon), self._default_handler)(obj.subcon)

		if obj.name is not None:
			self.name = name
		if indent:
			self.indent = old_indent
		_documented_subcon_instances[obj] = self.name

	# -- Type Handlers -- #

	def _enum_handler(self, obj):
		size   = obj.subcon.sizeof()
		if self.size_mode == SizeMode.BYTES:
			base = 'x'
			size = size * 2
		else:
			do_hex = (size & 3) == 0
			base   = 'x' if do_hex else 'b'
			size   = (size >> 2) if do_hex else size

		def _val_to_str(value):
			return f'0{base}{value:0{size}{base}}'

		for v, k in obj.ksymapping.items():
			self.append()
			self.append(f'.. py:attribute:: {self.name}.{k}')
			self.append(f'   :type: {self._typename(obj.subcon)}<{size}>')
			self.append(f'   :value: {_val_to_str(v)}')

		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _flags_enum_handler(self, obj):
		size   = obj.subcon.sizeof()
		if self.size_mode == SizeMode.BYTES:
			base = 'x'
			size = size * 2
		else:
			do_hex = (size & 3) == 0
			base   = 'x' if do_hex else 'b'
			size   = (size >> 2) if do_hex else size

		def _val_to_str(value):
			return f'0x{value:0{size}{base}}'

		for v, k in obj.reverseflags.items():
			self.append()
			self.append(f'.. py:attribute:: {self.name}.{k}')
			self.append(f'   :type: {self._typename(obj.subcon)}<{size}>')
			self.append(f'   :value: {_val_to_str(v)}')

		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _renamed_handler(self, obj : construct.Renamed):
		self.append()
		# self.append(f'.. _{self._mk_tgt_name(obj)}:')
		self.append(f'.. py:attribute:: {self._valname(obj)}')
		self.append(f'   :type: {self._typename(obj)}')
		if hasattr(obj.subcon, 'value'):
			self.append(f'   :value: {obj.subcon.value}')
		self._recuse(obj)

	# Unwrap the bits/bytes mode change construct.core.Transformed subcon
	def _transformed_handler(self, obj : construct.Transformed):
		size_mode = self.size_mode
		if obj.decodefunc == construct.bytes2bits:
			self.size_mode = SizeMode.BITS
		elif obj.decodefunc == construct.bits2bytes:
			self.size_mode = SizeMode.BYTES
		self._recuse(obj, indent = False)
		self.size_mode = size_mode

	# Unwrap the bits/bytes mode change construct.core.Restreamed subcon
	def _restreamed_handler(self, obj : construct.Restreamed):
		size_mode = self.size_mode
		if obj.decoder == construct.bytes2bits:
			self.size_mode = SizeMode.BITS
		elif obj.decoder == construct.bits2bytes:
			self.size_mode = SizeMode.BYTES
		self._recuse(obj, indent = False)
		self.size_mode = size_mode

	def _numeric_handler(self, obj : Union[construct.BitsInteger,construct.BytesInteger]):
		signedness = 'Signed' if obj.signed else 'Unsigned'
		if isinstance(obj, construct.BitsInteger):
			unit = 'bit'
		elif isinstance(obj, construct.BytesInteger):
			unit = 'byte'

		self.append()
		self.append(f'{signedness} {obj.sizeof()} {unit} integer.')

		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _formatfield_handler(self, obj : construct.FormatField):
		endian = FIELD_ENDAIN[obj.fmtstr[0]]['endian']
		specs  = list(map(lambda s: FIELD_SPEC[s], obj.fmtstr[1:]))

		self.append()
		self.append(f'**Endian:** {endian!s}')
		self.append()
		self.append(f'**Size:** {obj.length}')
		self.append()
		self.append(f'**Underlying Types:**')
		for s in specs:
			self.append()
			self.append(f'  Type: {s["ptype"]}')
			self.append()
			self.append(f'  Size: {s["std_size"]}')
			self.append()
			self.append(f'  Sign: {s["signed"]!s}')

		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _switch_handler(self, obj : construct.Switch):
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
			self.append()
			self.append(obj.docs)

	def _struct_handler(self, obj : construct.Struct):
		self._recuse(obj, indent = False)

		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _const_handler(self, obj : construct.Const):
		self._recuse(obj, indent = False)

	def _padded_handler(self, obj : construct.Padded):
		self.append()
		self.append(f'Data block padded to {obj.length} bytes')
		self._recuse(obj)
		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _rebuild_handler(self, obj : construct.Rebuild):
		self.append()
		self.append(f'Runtime rebuilt constant')
		self._recuse(obj, indent = False)
		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	def _greedy_range_handler(self, obj : construct.GreedyRange):
		self.append()
		self.append(f'.. py:attribute:: {self.name}.GreedyRange')
		self.append(f'   :type: {self._typename(obj.subcon)}')
		self._recuse(obj)

	# The default handler for things we miss
	def _default_handler(self, obj):
		log.warning(f'No specialized handling for {type(obj)}', color = 'yellow')
		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

		self._recuse(obj)

	# Not quite the default handler, but an empty handler
	# for type that don't have special parsing needs
	def _empty_handler(self, obj):
		if hasattr(obj, 'docs'):
			self.append()
			self.append(obj.docs)

	# -- Sphinx Documenter boilerplate bits -- #

	@classmethod
	def can_document_member(cls, member, membername, isattr, parent):
		return isinstance(member, construct.Subconstruct)

	def add_directive_header(self, sig):
		super().add_directive_header(sig)
		self.append(f'   :type: {self._typename(self.object)}')

	def add_content(self, content, no_docstring = False):
		super().add_content(content, no_docstring)
		self._recuse(self.object, indent = False)

	def get_doc(self, ignore: int = None):
		pass
