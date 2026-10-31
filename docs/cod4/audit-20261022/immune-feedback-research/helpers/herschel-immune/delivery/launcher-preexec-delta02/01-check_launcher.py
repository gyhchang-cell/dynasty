"""Python-only negative/boundary tests; controller/platform hooks are mocked.

Never writes a readiness file or touches prepared inputs. Synthetic markers and
files live only in TemporaryDirectory. Popen is patched to fail every test.
"""
from pathlib import Path
import contextlib
import copy
import importlib.util
import io
import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.dont_write_bytecode = True
P=Path(__file__).resolve().parents[1]/'launch_pair.py'
spec=importlib.util.spec_from_file_location('sweep_launcher_under_test', P)
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
R=L.BASE/'sweep01'
PREP=L.read(R/'prepared-inputs.json')
A=PREP['argv']['host']


class LauncherChecks(unittest.TestCase):
    def setUp(self):
        self.no_child=patch('subprocess.Popen', side_effect=AssertionError('NO CHILD PROCESS ALLOWED'))
        self.no_child.start();self.addCleanup(self.no_child.stop)

    def refused(self, fn, *args):
        with self.assertRaises((ValueError,OSError,KeyError)):
            fn(*args)

    def test_wrong_initial_dependency_pin_never_executes_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();source=root/'unapproved.py';side_effect=root/'should-not-exist'
            source.write_text('from pathlib import Path\nPath('+repr(str(side_effect))+').write_text("executed")\n')
            self.refused(L.load_tool,'unapproved',source,'0'*64)
            self.assertFalse(side_effect.exists())
            self.assertNotIn(str(source),L.LOADED_TOOL_SHA)

    def test_exact_approved_bytes_and_changed_payload_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();source=root/'approved.py';side_effect=root/'should-not-exist'
            source.write_text('value=41\n');digest=hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(L.load_tool('approved',source,digest).value,41)
            source.write_text('from pathlib import Path\nPath('+repr(str(side_effect))+').write_text("executed")\n')
            self.refused(L.load_tool,'changed',source,digest)
            self.assertFalse(side_effect.exists())

    def test_fixed_metadata_pins_match_independently_reviewed_sources(self):
        self.assertEqual(set(L.REVIEWED_METADATA_SHA),{'prepare_inputs.py','lint_mixin_boundary.py','watchdog.py','launch_once.py'})
        for leaf,digest in L.REVIEWED_METADATA_SHA.items():
            self.assertEqual(L.sha(L.ROOT/'tools/cod4/ecology-native-acceptance'/leaf),digest)

    def test_real_argv_and_identities(self):
        for role in ('host','peer'):
            props=L.check_argv(PREP['argv'][role],R,role)
            self.assertEqual(props['dynasty.sweepdriver.role'],role)
        self.assertEqual(L.identity('host'),'6c3ab68c-2707-3e49-bca5-7e82a37ca29f')
        self.assertEqual(L.identity('peer'),'ca2fb277-2f95-3b5d-a212-139f545d2321')

    def test_duplicate_properties(self):
        for value in ('-Ddynasty.sweepdriver.enabled=true','-Ddynasty.sweepdriver.enabled=false',
                      '-Decology.nativeqa.enabled=false','-Decology.nativeqa.enabled=true',
                      '-Dapple.awt.UIElement=true','-Djava.library.path=/tmp'):
            with self.subTest(value=value):self.refused(L.check_argv,A[:2]+[value]+A[2:],R,'host')

    def test_extra_ecology_and_jvm_overrides(self):
        for value in ('-Decology.nativeqa.driveScenes=false','-Decology.nativeqa.output=/tmp',
                      '-Ddynasty.anything=true','-Djava.system.class.loader=Arbitrary',
                      '-javaagent:/tmp/e.jar','@/tmp/opts','-XX:Flags=/tmp/opts','--enable-preview'):
            with self.subTest(value=value):self.refused(L.check_argv,A[:1]+[value]+A[1:],R,'host')

    def test_mutated_required_bindings(self):
        for flag in ('-Ddynasty.sweepdriver.role=host','-Ddynasty.sweepqa.output='+str(R/'host-evidence'),
                     '-Decology.bounded.observe=false','-Dfml.earlyWindowControl=false'):
            a=A.copy();a[a.index(flag)]=flag.split('=')[0]+'=BAD'
            with self.subTest(flag=flag):self.refused(L.check_argv,a,R,'host')
        for flag in ('--uuid','--gameDir','--username','--launchTarget','--assetsDir'):
            a=A.copy();a[a.index(flag)+1]='BAD'
            with self.subTest(flag=flag):self.refused(L.check_argv,a,R,'host')

    def test_late_property_and_duplicate_native_flags(self):
        self.refused(L.check_argv,A+['-Dunknown=true'],R,'host')
        self.refused(L.check_argv,A+['--uuid',L.identity('host')],R,'host')
        a=A.copy();i=a.index('cpw.mods.bootstraplauncher.BootstrapLauncher');a[i:i]=['-cp','/tmp/a.jar']
        self.refused(L.check_argv,a,R,'host')

    def test_environment_presence_even_empty(self):
        L.clean_environment({})
        for key in L.ENV_FORBIDDEN:
            for value in ('','-javaagent:x'):
                with self.subTest(key=key,value=value):self.refused(L.clean_environment,{key:value})

    def test_root_labels_and_symlinks(self):
        for label in ('../sweep01','sweep1','sweep'+'1'*26,'sweep01/host','/tmp/sweep01','sweep01\n'):
            with self.subTest(label=label):self.refused(L.root_for,label)
        self.assertEqual(L.root_for('sweep01'),R)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve();(p/'file').write_text('fixed');(p/'alias').symlink_to(p/'file')
            self.refused(L.sha,p/'alias');self.refused(L.manifest,p)

    def test_manifest_missing_empty_exact_and_added_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d).resolve();self.assertIsNone(L.manifest(p/'absent'))
            self.assertEqual(L.manifest(p),{})
            (p/'x').write_bytes(b'original\r\n')
            old=L.manifest(p);self.assertEqual(old,{'x':L.sha(p/'x')})
            (p/'x').write_bytes(b'changed\n');self.assertNotEqual(L.manifest(p),old)
            (p/'extra').write_text('x');self.assertEqual(set(L.manifest(p)),{'extra','x'})

    def test_json_duplicate_keys_and_canonical_digest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{"k":1,"k":2}')
            self.refused(L.read,p)
        self.assertEqual(L.digest_json({'a':1,'b':2}),L.digest_json({'b':2,'a':1}))
        self.assertNotEqual(L.digest_json({'a':1}),L.digest_json({'a':2}))

    def test_process_inventory_games_unknown_and_gradle(self):
        for line in [
            '1 /jdk/bin/java /jdk/bin/java cpw.mods.bootstraplauncher.BootstrapLauncher --launchTarget forgeclient',
            '2 java java -jar server.jar nogui',
            '3 java java net.fabricmc.loader.Main',
            '4 java java unknown.Main',
            '5 /Library/Java Custom/bin/java /Library/Java Custom/bin/java net.minecraft.client.main.Main',
            '6 java java org.gradle.launcher.daemon.bootstrap.GradleDaemon forgeclient',
        ]:
            with self.subTest(line=line):self.assertTrue(L.concurrent_java(line))
        self.assertEqual(L.concurrent_java('7 java java org.gradle.launcher.daemon.bootstrap.GradleDaemon /project/build/cod4-private'),[])
        self.assertEqual(L.concurrent_java('8 python3 python3 check_launcher.py java descriptions'),[])
        self.assertEqual(L.concurrent_java('9 java java org.gradle.wrapper.GradleWrapperMain'),[])

    def test_missing_ready_before_any_snapshot_or_platform_or_controller(self):
        with tempfile.TemporaryDirectory() as d, patch.object(L,'root_for',return_value=Path(d)), \
                patch.object(L,'snapshot',side_effect=AssertionError('snapshot called')), \
                patch.object(L,'require_awake',side_effect=AssertionError('display called')), \
                patch.object(L,'load_tool',side_effect=AssertionError('controller loaded')):
            self.refused(L.execute,'sweep01')
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_ready_validation_mock_only_no_approval_file(self):
        observed={'synthetic':'not a real readiness plan'}
        good={'status':L.READY_STATUS,'run':'sweep01','one_attempt_only':True,
              'snapshot_sha256':L.digest_json(observed),'reviewer':'synthetic offline checker',
              'review_report':'docs/cod4/audit-20261022/sweep-native-acceptance/driver/preparation-boundary-delta02.json',
              'review_report_sha256':'mockhash'}
        with patch.object(L,'canonical',side_effect=lambda p:Path(p)),patch.object(L,'sha',return_value='mockhash'):
            with patch.object(L,'read',return_value=good):self.assertEqual(L.reviewed(R,observed),'mockhash')
            for key,val in [('status','PREPARED_ONLY'),('run','sweep02'),('one_attempt_only',False),
                            ('snapshot_sha256','stale'),('reviewer',''),('review_report','../elsewhere'),
                            ('review_report_sha256','stale')]:
                bad={**good,key:val}
                with self.subTest(key=key),patch.object(L,'read',return_value=bad):self.refused(L.reviewed,R,observed)

    @contextlib.contextmanager
    def synthetic_run(self,root,observations):
        class Controller:
            calls=0
            def run_owned_pair(self,commands,**kwargs):
                self.calls+=1
                return {'mock_controller_only':True,'game_started':False}
        controller=Controller()
        def loader(name,path,expected_sha):
            self.assertEqual(expected_sha,'synthetic-watchdog')
            L.LOADED_TOOL_SHA[str(path)]='synthetic-watchdog'
            return controller
        with patch.object(L,'root_for',return_value=root),patch.object(L,'canonical',side_effect=lambda p:Path(p)), \
             patch.object(L,'snapshot',side_effect=observations),patch.object(L,'reviewed',return_value='mock-ready-sha'), \
             patch.object(L,'require_awake'),patch.object(L,'require_no_game'),patch.object(L,'load_tool',side_effect=loader):
            yield controller

    def sample(self):
        return {'argv':{'host':['NO-PROCESS'],'peer':['NO-PROCESS']},
                'tool_sources_sha256':{str(L.TOOLS/'pair_watchdog.py'):'synthetic-watchdog'}}

    def test_once_marker_and_exact_watchdog_wiring_mock_only(self):
        obs=self.sample()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve()
            with self.synthetic_run(root,[obs,obs,obs,obs]) as controller:
                result=L.execute('sweep01');self.assertTrue(result['mock_controller_only'])
                self.assertEqual(controller.calls,1)
                self.refused(L.execute,'sweep01');self.assertEqual(controller.calls,1)
            self.assertEqual({p.name for p in root.iterdir()},{'execution-started.json'})
            self.assertTrue(json.loads((root/'execution-started.json').read_text())['one_attempt_only'])

    def test_race_and_asleep_no_marker_mock_only(self):
        obs=self.sample();changed={**obs,'changed':True}
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve()
            with self.synthetic_run(root,[obs,changed]) as controller:
                self.refused(L.execute,'sweep01');self.assertEqual(controller.calls,0)
            self.assertEqual(list(root.iterdir()),[])
            with self.synthetic_run(root,[obs,obs]) as controller,patch.object(L,'require_awake',side_effect=ValueError('asleep')):
                self.refused(L.execute,'sweep01');self.assertEqual(controller.calls,0)
            self.assertEqual(list(root.iterdir()),[])

    def test_default_check_never_execute(self):
        with tempfile.TemporaryDirectory() as d,patch.object(L,'root_for',return_value=Path(d).resolve()),patch.object(L,'snapshot',return_value={'synthetic':True}),patch.object(L,'execute',side_effect=AssertionError('execute called')),contextlib.redirect_stdout(io.StringIO()) as output:
            L.main(['sweep01'])
        self.assertFalse(json.loads(output.getvalue())['independent_ready_present_and_matches'])


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LauncherChecks))
    raise SystemExit(not result.wasSuccessful())
