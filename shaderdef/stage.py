from ast import fix_missing_locations

from shaderdef.ast_util import (get_function_parameters,
                                make_assign,
                                make_self_attr_load,
                                make_self_attr_store,
                                parse_class,
                                remove_function_parameters,
                                rename_function)
from shaderdef.attr_rename import rename_attributes
from shaderdef.find_deps import find_deps
from shaderdef.find_function import find_function
from shaderdef.unselfify import unselfify
from shaderdef.py_to_glsl import py_to_glsl


def make_prefix(name):
    parts = name.split('_')
    return ''.join(part[0] for part in parts) + '_'


class Stage(object):
    def __init__(self, obj, func_name):
        self.name = func_name
        root = parse_class(obj)
        self.ast_root = find_function(root, func_name)
        self.input_prefix = ''
        self.output_prefix = make_prefix(self.name)
        self.parameters = get_function_parameters(self.ast_root,
                                                  include_self=False)

    def find_deps(self):
        return find_deps(self.ast_root)

    def provide_deps(self, next_stage):
        for dep in next_stage.find_deps().inputs:
            if dep not in self.find_deps().outputs:
                dst = make_self_attr_store(dep)
                src = make_self_attr_load(dep)
                assign = make_assign(dst, src)
                self.ast_root.body.append(assign)

        fix_missing_locations(self.ast_root)

    def required_uniforms(self, all_uniforms):
        for link in self.find_deps().inputs:
            unif = all_uniforms.get(link)
            if unif is not None:
                yield link, unif

    def load_names(self, external_links):
        names = {}
        for link in self.find_deps().inputs:
            if link not in external_links.uniforms:
                names[link] = self.input_prefix + link
        return names

    # TODO(nicholasbishop): de-dup
    def store_names(self, external_links):
        names = {}
        for link in self.find_deps().outputs:
            # Don't prefix uniforms, external outputs, or builtins
            if link not in external_links.uniforms and \
               link not in external_links.frag_outputs and \
               not link.startswith('gl_'):
                names[link] = self.output_prefix + link
        return names

    def declare_uniforms(self, lines, external_links):
        for link, unif in self.required_uniforms(external_links.uniforms):
            lines.append(unif.glsl_decl(link))

    def declare_attributes(self, lines, external_links):
        # TODO
        if self.name != 'vert_shader':
            return
        for index, (link, attr) in enumerate(external_links.attributes.items()):
            lines.append(attr.glsl_decl(link, location=index))

    def declare_frag_outputs(self, lines, external_links):
        # TODO
        if self.name != 'frag_shader':
            return
        for link, fout in external_links.frag_outputs.items():
            lines.append(fout.glsl_decl(link))

    def declare_inputs(self, lines):
        # TODO
        for pname, ptype in self.parameters:
            lines.append('in {} {};'.format(ptype, pname))

    def define_aux_functions(self, lines, library):
        # TODO
        for func_name in self.find_deps().calls:
            if func_name == 'emit_vertex':
                continue
            auxfunc = find_function(library, func_name)
            lines += py_to_glsl(auxfunc)

    def rename_gl_attributes(self, ast_root, external_links):
        return rename_attributes(
            ast_root,
            load_names=self.load_names(external_links),
            store_names=self.store_names(external_links))

    @staticmethod
    def rename_gl_builtins(ast_root):
        store_names = {
            'gl_position': 'gl_Position',
        }
        call_names = {
            'emit_vert': 'EmitVertex',
        }
        return rename_attributes(
            ast_root,
            store_names=store_names,
            call_names=call_names)

    def to_glsl(self, external_links, library):
        lines = []
        lines.append('#version 330 core')

        self.declare_uniforms(lines, external_links)
        self.declare_attributes(lines, external_links)
        self.declare_frag_outputs(lines, external_links)
        self.declare_inputs(lines)
        self.define_aux_functions(lines, library)

        ast_root = self.ast_root

        # The main shader function must always be "void main()"
        rename_function(ast_root, 'main')
        remove_function_parameters(ast_root)

        ast_root = self.rename_gl_attributes(ast_root, external_links)
        ast_root = self.rename_gl_builtins(ast_root)

        ast_root = unselfify(ast_root)
        lines += py_to_glsl(ast_root)
        return '\n'.join(lines)
