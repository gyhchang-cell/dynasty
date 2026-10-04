#!/usr/bin/env python3
"""Run a supplied DOM action in the user's already-open Dynasty Modrinth tab.

Requires Chrome's explicit Allow JavaScript from Apple Events setting. This
helper neither retrieves authentication credentials nor bypasses permissions.
"""
import base64
import json
from pathlib import Path
import subprocess
import sys

def run_js(javascript):
    apple = '\n'.join([
        'tell application "Google Chrome"',
        'repeat with w in windows',
        'repeat with t in tabs of w',
        'if URL of t contains "modrinth.com/project/dynasty-gyhchang" or URL of t contains "modrinth.com/modpack/dynasty-gyhchang" then',
        'return execute t javascript ' + json.dumps(javascript, ensure_ascii=False),
        'end if', 'end repeat', 'end repeat',
        'error "The Dynasty Modrinth tab is not open."', 'end tell',
    ])
    result = subprocess.run(['osascript', '-e', apple], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.rstrip()


def upload_local_file(path, selector, suffix, mime):
    path = Path(path)
    if path.suffix != suffix:
        raise ValueError('Unexpected file extension: ' + path.suffix)
    print(run_js("(() => { if(!document.querySelector(" + json.dumps(selector) + ")) throw Error('Expected upload control is missing'); window.__dynastyPackChunks=[]; return 'Preparing local file'; })()"), flush=True)
    data = path.read_bytes()
    chunk_size = 48 * 1024
    for offset in range(0, len(data), chunk_size):
        encoded = base64.b64encode(data[offset:offset + chunk_size]).decode('ascii')
        run_js('window.__dynastyPackChunks.push(' + json.dumps(encoded) + '); "ok"')
        if offset % (64 * chunk_size) == 0:
            print(f'File transfer: {offset}/{len(data)} bytes', flush=True)
    action = """(() => {
      const input=document.querySelector(SELECTOR);
      if(!input) throw Error('Page changed; no upload was performed');
      const bytes=window.__dynastyPackChunks.map(c=>Uint8Array.from(atob(c),v=>v.charCodeAt(0)));
      const file=new File(bytes, FILENAME, {type:MIME});
      const dt=new DataTransfer(); dt.items.add(file); input.files=dt.files;
      input.dispatchEvent(new Event('change',{bubbles:true}));
      delete window.__dynastyPackChunks;
      return JSON.stringify({selected:file.name,size:file.size});
    })()""".replace('FILENAME', json.dumps(path.name)).replace('SELECTOR', json.dumps(selector)).replace('MIME', json.dumps(mime))
    print(run_js(action), flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) == 3 and sys.argv[1] == '--upload':
            upload_local_file(sys.argv[2], '[aria-label="Change primary file"] input[type=file]', '.mrpack', 'application/x-modrinth-modpack+zip')
        elif len(sys.argv) == 3 and sys.argv[1] == '--upload-icon':
            extension = Path(sys.argv[2]).suffix.lower()
            if extension not in ('.png', '.jpg', '.jpeg'):
                raise ValueError('Only a supplied PNG or JPEG icon is accepted.')
            mime = 'image/png' if extension == '.png' else 'image/jpeg'
            upload_local_file(sys.argv[2], 'input[type=file][accept="image/png,image/jpeg,image/gif,image/webp"]', extension, mime)
        else:
            javascript = sys.stdin.read()
            if not javascript.strip():
                raise ValueError('Provide JavaScript on stdin, or --upload path.mrpack.')
            print(run_js(javascript))
    except (RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
