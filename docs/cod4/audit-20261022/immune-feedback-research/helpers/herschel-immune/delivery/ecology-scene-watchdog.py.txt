"""External bound for one child created here; never attaches to an existing PID.

The future private-instance launcher must validate its paths, hashes and Java args
before calling run_owned. This module performs no game setup or world loading.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def _fresh(path: Path, value: str) -> None:
    with path.open('x', encoding='utf-8') as out:
        out.write(value)


def run_owned(argv: list[str], *, instance: Path, evidence: Path,
              startup_seconds: float = 240, runtime_seconds: float = 300,
              absolute_seconds: float = 600, save_grace_seconds: float = 60,
              term_grace_seconds: float = 15, poll_seconds: float = .25) -> dict:
    """Launch exactly one fresh process group and bound even a blocked game tick.

    Evidence must be a fresh leaf created by the validated caller. Normal exit is
    recorded separately from native-save proof, which the later verifier checks.
    """
    instance = instance.resolve(strict=True)
    evidence = evidence.resolve(strict=True)
    if not argv or not all(x > 0 for x in (startup_seconds, runtime_seconds,
                                           absolute_seconds, save_grace_seconds,
                                           term_grace_seconds, poll_seconds)):
        raise ValueError('Positive finite budgets and an explicit command required')
    import math
    if not all(math.isfinite(x) for x in (startup_seconds, runtime_seconds,
                                         absolute_seconds, save_grace_seconds,
                                         term_grace_seconds, poll_seconds)):
        raise ValueError('Finite budgets required')
    for name in ('watchdog-start.json', 'watchdog-result.json', 'external-stop-request.txt',
                 'stop-client.txt', 'controller-start.json', 'watchdog-client.log'):
        if (evidence / name).exists() or (evidence / name).is_symlink():
            raise FileExistsError(f'Fresh evidence required: {name}')
    start = time.monotonic()
    ready_at = requested_at = term_at = None
    forced = False
    reason = None
    with (evidence / 'watchdog-client.log').open('xb') as log:
        child = subprocess.Popen(argv, cwd=instance, stdout=log, stderr=subprocess.STDOUT,
                                 stdin=subprocess.DEVNULL, start_new_session=True)
        # start_new_session makes this owned child the new process-group leader.
        # Never accept an external PID, scan processes, or signal user instances.
        def signal_owned(sig: int) -> None:
            if child.poll() is None:
                try:
                    if os.getpgid(child.pid) != child.pid:
                        raise RuntimeError('Owned child group identity changed')
                    os.killpg(child.pid, sig)
                except ProcessLookupError:
                    pass  # The owned child can exit between poll and signal.
        try:
            _fresh(evidence / 'watchdog-start.json', json.dumps({
                'pid': child.pid, 'instance': str(instance), 'startup_seconds': startup_seconds,
                'runtime_seconds': runtime_seconds, 'absolute_seconds': absolute_seconds,
                'save_grace_seconds': save_grace_seconds, 'term_grace_seconds': term_grace_seconds,
                'existing_process_attached': False}) + '\n')
            while child.poll() is None:
                now = time.monotonic()
                if ready_at is None and (evidence / 'controller-start.json').is_file():
                    # Marker is readiness only, never a gameplay or save assertion.
                    try:
                        marker = json.loads((evidence / 'controller-start.json').read_text())
                    except (json.JSONDecodeError, FileNotFoundError):
                        marker = None  # Creation can precede the writer finishing its JSON.
                    if isinstance(marker, dict) and marker.get('instance') == str(instance):
                        ready_at = now
                if requested_at is None:
                    if now - start >= absolute_seconds:
                        reason = 'absolute_deadline'
                    elif ready_at is None and now - start >= startup_seconds:
                        reason = 'startup_deadline'
                    elif ready_at is not None and now - ready_at >= runtime_seconds:
                        reason = 'runtime_deadline'
                    elif (evidence / 'stop-client.txt').exists():
                        reason = 'internal_controller_stop'
                    if reason:
                        requested_at = now
                        if not (evidence / 'external-stop-request.txt').exists():
                            _fresh(evidence / 'external-stop-request.txt', reason + '\n')
                        if not (evidence / 'stop-client.txt').exists():
                            try:
                                _fresh(evidence / 'stop-client.txt', 'External normal shutdown request\n')
                            except FileExistsError:
                                pass  # Private controller may create it concurrently.
                elif term_at is None and now - requested_at >= save_grace_seconds:
                    signal_owned(signal.SIGTERM)
                    term_at = now
                    forced = True
                elif term_at is not None and now - term_at >= term_grace_seconds:
                    signal_owned(signal.SIGKILL)
                    forced = True
                    break
                time.sleep(poll_seconds)
            code = child.wait(timeout=max(5, term_grace_seconds))
        except BaseException:
            # Never abandon a child because a marker is malformed or disk I/O fails.
            signal_owned(signal.SIGTERM)
            try:
                child.wait(timeout=term_grace_seconds)
            except subprocess.TimeoutExpired:
                signal_owned(signal.SIGKILL)
                child.wait(timeout=5)
            raise
    result = {'pid': child.pid, 'exit_code': code, 'elapsed_seconds': time.monotonic() - start,
              'stop_reason': reason, 'forced_signal_used': forced,
              'controller_ready_observed': ready_at is not None,
              'normal_exit_without_forced_signal': code == 0 and not forced,
              'native_save_verified': False, 'gameplay_acceptance': False}
    _fresh(evidence / 'watchdog-result.json', json.dumps(result, indent=2) + '\n')
    return result
