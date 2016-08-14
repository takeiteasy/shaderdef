from typing import (Generic, SupportsAbs, SupportsInt, SupportsFloat,
                    TypeVar)
from shaderdef.equality import EqualityMixin


class FragOutput(EqualityMixin):
    def __init__(self, gtype):
        self.gtype = gtype

    def __repr__(self):
        return 'FragOutput({})'.format(self.gtype)

    def glsl_decl(self, name):
        return 'out {} {};'.format(self.gtype.__name__, name)


class BuiltinType(object):
    def __init__(self, *args):
        pass


class GlslType(SupportsAbs, SupportsInt, SupportsFloat):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, name) -> 'GlslType':
        return GlslType(self, name)

    def __getitem__(self, index) -> 'GlslType':
        return GlslType(self, index)

    def __setitem__(self, index, val) -> 'GlslType':
        return GlslType(self, index, val)

    def __abs__(self) -> 'GlslType':
        return GlslType(self)

    def __add__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __sub__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __mul__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __truediv__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __int__(self):
        pass

    def __float__(self):
        pass


class ShaderInterface(object):
    def __init__(self, **kwargs):
        pass


def decl_uniform(name, gtype):
    return 'uniform {} {};'.format(gtype, name)


# TODO(nicholasbishop): location
def decl_attribute(name, gtype, location):
    return 'in {} {};'.format(gtype, name)


# pylint: disable=invalid-name
mat2 = GlslType
mat3 = GlslType
mat4 = GlslType
vec2 = GlslType
vec3 = GlslType
vec4 = GlslType

class void(object):
    pass

# TODO
GlslArrayElem = TypeVar('GlslArrayElem')
class GlslArray(Generic[GlslArrayElem]):
    def __init__(self, gtype):
        pass

    def __getitem__(self, index):
        return GlslType(self, index)

    def __setitem__(self, index, val):
        return GlslType(self, index, val)


# TODO(nicholasbishop): this is obviously really ugly, and requires
# users to define their own type alias for larger arrays. But at least
# for now it seems that numbers aren't allowed as type parameters in
# the style that C++ allows (e.g. std::array<float, 3>)
Array1 = GlslArray
Array2 = GlslArray
Array3 = GlslArray
Array4 = GlslArray
Array5 = GlslArray
Array6 = GlslArray
Array7 = GlslArray
Array8 = GlslArray
Array9 = GlslArray
Array10 = GlslArray
Array11 = GlslArray
Array12 = GlslArray
Array13 = GlslArray
Array14 = GlslArray
Array15 = GlslArray
Array16 = GlslArray


# TODO
gl_triangles = 'gl_triangles'
gl_triangle_strip = 'gl_triangle_strip'


# TODO
class noperspective(object):
    pass
