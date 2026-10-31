"""Print selected complete Java methods for manual review; never grants credit."""
from pathlib import Path
import argparse
import hashlib
import sys

assert sys.version_info[:2] == (3, 12)
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language, Parser
import tree_sitter_java

args = argparse.ArgumentParser()
args.add_argument('path')
args.add_argument('methods', nargs='+')
options = args.parse_args()
source = ROOT / options.path
raw = source.read_bytes()
parser = Parser(Language(tree_sitter_java.language()))

def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)

print(source, 'SHA256', hashlib.sha256(raw).hexdigest())
for node in walk(parser.parse(raw).root_node):
    if node.type != 'method_declaration':
        continue
    name = node.child_by_field_name('name')
    if name is None or raw[name.start_byte:name.end_byte].decode() not in options.methods:
        continue
    print(f'\nLINES {node.start_point.row + 1}-{node.end_point.row + 1}')
    print(raw[node.start_byte:node.end_byte].decode())
