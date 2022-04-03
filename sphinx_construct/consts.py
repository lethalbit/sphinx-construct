# SPDX-License-Identifier: BSD-3-Clause

from enum import IntEnum, Enum, auto, unique

__all__ = (
	'DOMAIN',
	'FIELD_ENDAIN',
	'FIELD_SPEC',
	'Signedness',
	'Endian',
	'Size',
	'Alignment',
)

DOMAIN = 'sphinx-construct'

@unique
class Signedness(Enum):
	UNDEFINED = auto()
	SIGNED    = auto()
	UNSIGNED  = auto()

	def __str__(self):
		if self == Signedness.SIGNED:
			return 'signed'
		elif self == Signedness.UNSIGNED:
			return 'unsigned'
		else:
			return '<undefined>'


class Endian(Enum):
	UNDEFINED = auto()
	NATIVE    = auto()
	BIG       = auto()
	LITTLE    = auto()
	NETWORK   = BIG

	def __str__(self):
		if self == Endian.NATIVE:
			return 'native'
		elif self == Endian.BIG:
			return 'big'
		elif self == Endian.LITTLE:
			return 'little'
		else:
			return '<undefined>'

@unique
class Size(Enum):
	NATIVE   = auto()
	STANDARD = auto()

	def __str__(self):
		if self == Size.NATIVE:
			return 'native'
		elif self == Size.STANDARD:
			return 'standard'
		else:
			return '<undefined>'

@unique
class Alignment(IntEnum):
	UNDEFINED = auto()
	NATIVE    = auto()

	def __str__(self):
		if self == Alignment.NATIVE:
			return 'native'
		else:
			return '<undefined>'

# `@` and `!` are unused in construct for the moment,
# but add them just in case:tm:
FIELD_ENDAIN = {
	'@': {
		'endian': Endian.NATIVE,
		'size': Size.NATIVE,
		'align': Alignment.NATIVE,
	},
	'=': {
		'endian': Endian.NATIVE,
		'size': Size.STANDARD,
		'align': Alignment.UNDEFINED,
	},
	'<': {
		'endian': Endian.LITTLE,
		'size': Size.STANDARD,
		'align': Alignment.UNDEFINED,
	},
	'>': {
		'endian': Endian.BIG,
		'size': Size.STANDARD,
		'align': Alignment.UNDEFINED,
	},
	'!': {
		'endian': Endian.NETWORK,
		'size': Size.STANDARD,
		'align': Alignment.UNDEFINED,
	},
}
# only B H L Q b h l q e f d and ? are used in construct
# but for completeness sake we've defined all of them
FIELD_SPEC = {
	'x': {
		'ctype': 'pad',
		'ptype': 'none',
		'std_size': None,
		'signed': Signedness.UNDEFINED,
	},
	'c': {
		'ctype': 'char',
		'ptype': 'bytes',
		'std_size': 1,
		'signed': Signedness.UNDEFINED,
	},
	'b': {
		'ctype': 'char',
		'ptype': 'int',
		'std_size': 1,
		'signed': Signedness.SIGNED,
	},
	'B': {
		'ctype': 'unsigned char',
		'ptype': 'int',
		'std_size': 1,
		'signed': Signedness.UNSIGNED,
	},
	'?': {
		'ctype': 'bool',
		'ptype': 'bool',
		'std_size': 1,
		'signed': Signedness.UNDEFINED,
	},
	'h': {
		'ctype': 'short',
		'ptype': 'int',
		'std_size': 2,
		'signed': Signedness.SIGNED,
	},
	'H': {
		'ctype': 'unsigned short',
		'ptype': 'int',
		'std_size': 2,
		'signed': Signedness.UNSIGNED,
	},
	'i': {
		'ctype': 'int',
		'ptype': 'int',
		'std_size': 4,
		'signed': Signedness.SIGNED,
	},
	'I': {
		'ctype': 'unsigned int',
		'ptype': 'int',
		'std_size': 4,
		'signed': Signedness.UNSIGNED,
	},
	'l': {
		'ctype': 'long',
		'ptype': 'int',
		'std_size': 4,
		'signed': Signedness.SIGNED,
	},
	'L': {
		'ctype': 'unsigned long',
		'ptype': 'int',
		'std_size': 4,
		'signed': Signedness.UNSIGNED,
	},
	'q': {
		'ctype': 'long long',
		'ptype': 'int',
		'std_size': 8,
		'signed': Signedness.SIGNED,
	},
	'Q': {
		'ctype': 'unsigned long long',
		'ptype': 'int',
		'std_size': 8,
		'signed': Signedness.SIGNED,
	},
	'n': {
		'ctype': 'ssize_t',
		'ptype': 'int',
		'std_size': None,
		'signed': Signedness.SIGNED,
	},
	'N': {
		'ctype': 'size_t',
		'ptype': 'int',
		'std_size': None,
		'signed': Signedness.UNSIGNED,
	},
	'e': {
		'ctype': None,
		'ptype': 'float',
		'std_size': 2,
		'signed': Signedness.UNDEFINED,
	},
	'f': {
		'ctype': 'float',
		'ptype': 'float',
		'std_size': 4,
		'signed': Signedness.UNDEFINED,
	},
	'd': {
		'ctype': 'double',
		'ptype': 'float',
		'std_size': 8,
		'signed': Signedness.UNDEFINED,
	},
	's': {
		'ctype': 'char[]',
		'ptype': 'bytes',
		'std_size': None,
		'signed': Signedness.UNDEFINED,
	},
	'p': {
		'ctype': 'char[]',
		'ptype': 'bytes',
		'std_size': None,
		'signed': Signedness.UNDEFINED,
	},
	'P': {
		'ctype': 'void*',
		'ptype': 'int',
		'std_size': None,
		'signed': Signedness.UNDEFINED,
	},
}
