"""Private read-only JVM Code inspection. Never imports or runs legacy audit main."""
import ast
import datetime
import hashlib
import json
import pathlib
import re
import struct
import zipfile

ROOT = pathlib.Path('/Users/a15356015027/Desktop/dynasty')
PRIVATE = ROOT / 'docs/cod4/audit-20261022/program-feedback-review-20261101'
PARSER = ROOT / 'tools/cod4/legacy-migration-acceptance/check_private_srg.py'
NATIVE = ROOT / 'build/cod4-main-mekanism-version-binding-20261110'
OUTPUT = PRIVATE / 'batch-120-official-native-save-contract-code-20261110.json'


def descriptor(p):
    b = p.read_bytes()
    return {'path': str(p), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}


def inspect_class(payload, selected):
    # Reuse only the fully inspected local Reader/parse definitions. No import,
    # linkage-audit main, legacy receipt checks, Java or class initialization.
    tree = ast.parse(PARSER.read_text())
    definitions = [x for x in tree.body if isinstance(x, (ast.ClassDef, ast.FunctionDef))
                   and x.name in {'Reader', 'parse'}]
    assert len(definitions) == 2
    ns = {'struct': struct, 're': re}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(PARSER), 'exec'), ns)
    Reader = ns['Reader']
    parsed = ns['parse'](payload)
    r = Reader(payload)
    assert r.u4() == 0xCAFEBABE
    r.u2()
    assert r.u2() == 69
    cp = [None] * r.u2()
    i = 1
    while i < len(cp):
        tag = r.u1()
        if tag == 1:
            value = r.take(r.u2()).decode('utf-8', errors='replace')
        elif tag in (3, 4):
            value = r.take(4).hex()
        elif tag in (5, 6):
            value = r.take(8).hex()
        elif tag in (7, 8, 16, 19, 20):
            value = r.u2()
        elif tag in (9, 10, 11, 12, 17, 18):
            value = (r.u2(), r.u2())
        elif tag == 15:
            value = (r.u1(), r.u2())
        else:
            raise ValueError(('Unknown constant tag', tag))
        cp[i] = (tag, value)
        i += 2 if tag in (5, 6) else 1
    bootstraps = []
    if 'BootstrapMethods' in parsed['attributes']:
        b = Reader(parsed['attributes']['BootstrapMethods'])
        for _ in range(b.u2()):
            handle = b.u2()
            bootstraps.append((handle, [b.u2() for _ in range(b.u2())]))
        assert b.pos == len(b.data)

    def resolve(index):
        tag, value = cp[index]
        if tag in (1, 3, 4, 5, 6):
            return value
        if tag in (7, 8, 16, 19, 20):
            return resolve(value)
        if tag == 12:
            return {'name': resolve(value[0]), 'descriptor': resolve(value[1])}
        if tag in (9, 10, 11):
            return {'owner': resolve(value[0]), **resolve(value[1]), 'kind': tag}
        if tag == 15:
            return {'handle_kind': value[0], 'target': resolve(value[1])}
        if tag in (17, 18):
            handle, args = bootstraps[value[0]]
            return {'dynamic': resolve(value[1]), 'bootstrap_index': value[0],
                    'bootstrap_handle': resolve(handle),
                    'bootstrap_args': [resolve(x) for x in args]}
        raise ValueError(('Unresolved tag', tag))

    names = ("nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 "
             "lconst_0 lconst_1 fconst_0 fconst_1 fconst_2 dconst_0 dconst_1 bipush sipush ldc ldc_w ldc2_w "
             "iload lload fload dload aload iload_0 iload_1 iload_2 iload_3 lload_0 lload_1 lload_2 lload_3 "
             "fload_0 fload_1 fload_2 fload_3 dload_0 dload_1 dload_2 dload_3 aload_0 aload_1 aload_2 aload_3 "
             "iaload laload faload daload aaload baload caload saload istore lstore fstore dstore astore "
             "istore_0 istore_1 istore_2 istore_3 lstore_0 lstore_1 lstore_2 lstore_3 fstore_0 fstore_1 fstore_2 fstore_3 "
             "dstore_0 dstore_1 dstore_2 dstore_3 astore_0 astore_1 astore_2 astore_3 iastore lastore fastore dastore "
             "aastore bastore castore sastore pop pop2 dup dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap "
             "iadd ladd fadd dadd isub lsub fsub dsub imul lmul fmul dmul idiv ldiv fdiv ddiv irem lrem frem drem "
             "ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand land ior lor ixor lxor iinc "
             "i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg "
             "ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple "
             "if_acmpeq if_acmpne goto jsr ret tableswitch lookupswitch ireturn lreturn freturn dreturn areturn return "
             "getstatic putstatic getfield putfield invokevirtual invokespecial invokestatic invokeinterface invokedynamic "
             "new newarray anewarray arraylength athrow checkcast instanceof monitorenter monitorexit wide multianewarray "
             "ifnull ifnonnull goto_w jsr_w breakpoint").split()
    assert len(names) == 203 and names[180] == 'getfield' and names[186] == 'invokedynamic'
    one = {16, 18, *range(21, 26), *range(54, 59), 169, 188}
    two = {17, 19, 20, 132, *range(153, 169), *range(178, 185), 187, 189, 192, 193, 198, 199}
    cp2 = {*range(178, 187), 187, 189, 192, 193, 197}
    methods = []
    for (name, desc), member in parsed['methods'].items():
        if name not in selected:
            continue
        raw = member['attributes']['Code']
        c = Reader(raw)
        stack, locals_count, size = c.u2(), c.u2(), c.u4()
        code = c.take(size)
        exceptions = []
        for _ in range(c.u2()):
            lo, hi, handler, catch = c.u2(), c.u2(), c.u2(), c.u2()
            exceptions.append({'start': lo, 'end': hi, 'handler': handler,
                               'catch': resolve(catch) if catch else 'any'})
        for _ in range(c.u2()):
            c.u2()
            c.take(c.u4())
        assert c.pos == len(raw)
        instructions = []
        pc = 0
        while pc < len(code):
            start = pc
            op = code[pc]
            assert op < 203
            pc += 1
            if op in (170, 171, 196):
                raise ValueError(('Unsupported variable instruction', op))
            count = 1 if op in one else 2 if op in two else 4 if op in (185, 186, 200, 201) else 3 if op == 197 else 0
            arg = code[pc:pc + count]
            assert len(arg) == count
            pc += count
            row = {'pc': start, 'opcode': names[op], 'bytes': code[start:pc].hex()}
            if op == 18 or op in (19, 20) or op in cp2:
                index = arg[0] if op == 18 else int.from_bytes(arg[:2], 'big')
                row['constant_index'] = index
                row['resolved'] = resolve(index)
            if 153 <= op <= 168 or op in (198, 199, 200, 201):
                row['target'] = start + int.from_bytes(arg, 'big', signed=True)
            instructions.append(row)
        targets = {x['pc'] for x in instructions}
        assert all(x['target'] in targets for x in instructions if 'target' in x)
        methods.append({'name': name, 'descriptor': desc, 'access': member['access'],
                        'Code_attribute_sha256': hashlib.sha256(raw).hexdigest(),
                        'Code_attribute_hex': raw.hex(), 'code_hex': code.hex(),
                        'max_stack': stack, 'max_locals': locals_count,
                        'exceptions': exceptions, 'instructions': instructions})
    assert {m['name'] for m in methods} == set(selected)
    return {'class_name': parsed['name'], 'parent': parsed['parent'], 'major': parsed['major'],
            'fields': [{'name': n, 'descriptor': d} for n, d in parsed['fields']],
            'selected_methods': methods, 'whole_class_semantic_read': False}


def main():
    assert not OUTPUT.exists()
    receipt = PRIVATE / 'coordinator-program120-fixed-version-native-class-binding-20261110.json'
    assert descriptor(receipt)['sha256'] == 'c648bb8b13122a0d1f93e579ecd09fcaa755576711411e850ba922fdbb6b85fe'
    evidence = json.loads(receipt.read_bytes())
    archive = pathlib.Path(evidence['native_client_archive']['path'])
    assert descriptor(archive) == evidence['native_client_archive']
    results = []
    with zipfile.ZipFile(archive) as z:
        for entry in evidence['native_classes']:
            p = pathlib.Path(entry['raw']['path'])
            assert descriptor(p) == entry['raw']
            payload = p.read_bytes()
            assert payload == z.read(entry['archive_member'])
            selected = {'<init>', 'setDirty', 'isDirty'} if p.name == 'SavedData.class' else {
                'computeIfAbsent', 'get', 'readSavedData', 'set', 'scheduleSave',
                'collectDirtyTagsToSave', 'encodeUnchecked', 'tryWrite', 'saveAndJoin', 'close',
                'lambda$collectDirtyTagsToSave$0', 'lambda$collectDirtyTagsToSave$1'}
            results.append({'binding': entry, **inspect_class(payload, selected)})
    result = {'status': 'exact_official26.3_class_static_Code_extraction_for_actual_review',
              'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'reader': descriptor(pathlib.Path(__file__)), 'trusted_parser': descriptor(PARSER),
              'parser_definitions_only': ['Reader', 'parse'], 'legacy_audit_main_executed': False,
              'Main_version_binding': descriptor(receipt), 'native_archive': descriptor(archive),
              'classes': results, 'not_runtime_or_NeoForge_patched_acceptance': True,
              'semantic_credit': 0, 'game_starts': 0, 'network_requests': 0}
    with OUTPUT.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps(descriptor(OUTPUT)))
    for cls in results:
        print(cls['class_name'])
        for method in cls['selected_methods']:
            print(method['name'], method['descriptor'])
            for row in method['instructions']:
                # Human-readable display of all selected method instructions.
                detail = row.get('resolved', row.get('target', ''))
                print(row['pc'], row['opcode'], json.dumps(detail, ensure_ascii=False, separators=(',', ':')))
            if method['exceptions']:
                print('EXCEPTIONS', method['exceptions'])


if __name__ == '__main__':
    main()
