"""Bound two newly created private processes; caller must validate final launch inputs.

No CLI, discovery, game setup or existing-PID attachment is provided here.
Exit codes and driver markers are lifecycle evidence, never gameplay acceptance.
"""
from pathlib import Path
import json
import math
import os
import signal
import subprocess
import time


def fresh(path, data):
    with path.open('x') as stream:
        stream.write(data)


def run_owned_pair(commands, *, root, startup_seconds=240, absolute_seconds=900,
                   save_seconds=60, term_seconds=15, poll_seconds=.25):
    """Only call after independent review and exact readiness validation.

    Each command is an argv list for its role's private working directory.
    All signals target process groups created inside this invocation.
    """
    budgets = (startup_seconds, absolute_seconds, save_seconds, term_seconds, poll_seconds)
    if not all(math.isfinite(v) and v > 0 for v in budgets):
        raise ValueError('Positive finite budgets required')
    if set(commands) != {'host', 'peer'}:
        raise ValueError('Exactly two explicit role commands required')
    root = Path(root).resolve(strict=True)
    bridge = root / 'bridge'
    if bridge.resolve(strict=True) != bridge:
        raise ValueError('Internal bridge required')
    for role, argv in commands.items():
        if not argv or not all(isinstance(v, str) and v for v in argv):
            raise ValueError('Explicit argv strings required')
        instance = root / role
        if instance.resolve(strict=True) != instance:
            raise ValueError('Internal role directory required')
    for path in [root / 'pair-watchdog-start.json', root / 'pair-watchdog-result.json',
                 bridge / 'external-stop-request.txt'] + [
                     root / (role + '-watchdog.log') for role in commands]:
        if path.exists() or path.is_symlink():
            raise FileExistsError('Fresh invocation required: ' + str(path))
    # Existing sessions must not be inherited accidentally by a fresh controller.
    if any(p.name != 'plan.json' for p in bridge.iterdir()):
        raise FileExistsError('Only an unconsumed plan may exist in the bridge')
    started = time.monotonic()
    children, streams, forced, signals = {}, {}, {}, []
    requested = term_at = None
    reason = None
    ready = False

    def signal_child(role, sig):
        child = children[role]
        if child.poll() is not None:
            return
        try:
            if os.getpgid(child.pid) != child.pid:
                raise RuntimeError('Owned child group identity changed')
            os.killpg(child.pid, sig)
            forced[role] = True
            signals.append({'role': role, 'pid': child.pid, 'signal': int(sig)})
        except ProcessLookupError:
            pass

    def normal_stop(cause):
        try:
            fresh(bridge / 'external-stop-request.txt', cause + '\n')
        except FileExistsError:
            pass

    try:
        for role in ('host', 'peer'):
            streams[role] = (root / (role + '-watchdog.log')).open('xb')
            children[role] = subprocess.Popen(
                commands[role], cwd=root / role, stdout=streams[role],
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                start_new_session=True)
            forced[role] = False
        fresh(root / 'pair-watchdog-start.json', json.dumps({
            'pids': {k: p.pid for k, p in children.items()},
            'budgets_seconds': dict(zip(('startup', 'absolute', 'save', 'term', 'poll'), budgets)),
            'existing_pid_attached': False}) + '\n')
        while any(child.poll() is None for child in children.values()):
            now = time.monotonic()
            # Driver publishes connections only after checking both real players/TCP.
            # Full provenance/mechanical verification remains a separate operation.
            ready = ready or (bridge / 'connections.json').is_file()
            if requested is None:
                if now - started >= absolute_seconds:
                    reason = 'absolute_deadline'
                elif not ready and now - started >= startup_seconds:
                    reason = 'startup_deadline'
                elif (bridge / 'abort.json').exists():
                    reason = 'driver_abort'
                elif any(child.poll() is not None for child in children.values()):
                    reason = 'one_child_exited_stop_remaining'
                elif (bridge / 'external-stop-request.txt').exists():
                    reason = 'external_normal_stop'
                if reason:
                    normal_stop(reason)
                    requested = now
            elif term_at is None and now - requested >= save_seconds:
                for role in children:
                    signal_child(role, signal.SIGTERM)
                term_at = now
            elif term_at is not None and now - term_at >= term_seconds:
                for role in children:
                    signal_child(role, signal.SIGKILL)
                break
            time.sleep(poll_seconds)
        for child in children.values():
            child.wait(timeout=5)
    except BaseException:
        # Includes failure to create the second process or write a receipt.
        # Never abandon the first successfully created group.
        for role in children:
            signal_child(role, signal.SIGTERM)
        until = time.monotonic() + term_seconds
        for child in children.values():
            try:
                child.wait(timeout=max(.01, until - time.monotonic()))
            except subprocess.TimeoutExpired:
                pass
        for role in children:
            signal_child(role, signal.SIGKILL)
        for child in children.values():
            child.wait(timeout=5)
        raise
    finally:
        for stream in streams.values():
            stream.close()
    result = {'elapsed_seconds': time.monotonic() - started, 'stop_reason': reason,
              'roles': {role: {'pid': child.pid, 'exit_code': child.returncode,
                               'forced_signal_used': forced[role]}
                        for role, child in children.items()},
              'signals': signals, 'connections_marker_observed': ready,
              'native_save_verified': False, 'gameplay_acceptance': False}
    fresh(root / 'pair-watchdog-result.json', json.dumps(result, indent=2) + '\n')
    return result
