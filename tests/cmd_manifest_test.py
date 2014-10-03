from xd.tool.main import main
import xd.tool.log

from nose.tools import raises, with_setup
import unittest
import os
import tempfile
import shutil
from redirect import stdchannel_redirected
from xd.tool.shell import call

class tests(unittest.case.TestCase):

    def setUp(self):
        self.oldcwd = os.getcwd()
        self.oldpwd = os.environ['PWD'] or None
        self.testdir = tempfile.mkdtemp(prefix='nose-')
        os.chdir(self.testdir)
        os.environ['PWD']=self.testdir
        with stdchannel_redirected(1):
            with stdchannel_redirected(2):
                #create test git repos
                call("git init foomodule",quiet=True)
                os.chdir("foomodule")
                #repo used as submodule must contain something to be added
                call("touch foo && git add foo && git commit -am 'add foo'",quiet=True)
                os.chdir(self.testdir)
                for g in ["mf-empty", "mf-unit-subm", "mf-subm"]:
                    os.mkdir(g)
                    os.chdir(g)
                    self.assertEqual(main(['xd', 'init']), None)
                    if("subm" in g):
                        call('git submodule add ../foomodule meta/foo')
                        call("git add *.* && git commit -am 'bar'")
                    os.chdir(self.testdir)
                
    def tearDown(self):
        os.chdir(self.oldcwd)
        if self.oldpwd:
            os.environ['PWD'] = self.oldpwd
        shutil.rmtree(self.testdir)
        xd.tool.log.deinit()

    def test_manifest(self):
        with stdchannel_redirected(2):
            os.chdir(self.testdir)
            os.chdir("mf-empty")
            os.environ['PWD']=os.getcwd()
            self.assertEqual(main(['xd', 'manifest']), None)

    def test_manifest_submodule(self):
        with stdchannel_redirected(2):
            os.chdir(self.testdir)
            os.chdir("mf-unit-subm")
            os.environ['PWD']=os.getcwd()
            self.assertEqual(main(['xd', 'manifest']), None)

    def test_manifest_unitialized_submodule(self):
        os.chdir(self.testdir)
        with stdchannel_redirected(1):
            with stdchannel_redirected(2):
                #user clones manually without -recursive
                call("git clone mf-unit-subm foo")
                os.chdir("foo")
                os.environ['PWD']=os.getcwd()
                self.assertEqual(main(['xd', 'manifest']), None)
                l = call("git submodule status meta/foo",quiet=True)
                self.assertEqual(l.split()[-1],"(heads/master)")
