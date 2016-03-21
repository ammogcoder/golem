import os
import re

from mock import MagicMock

from golem.tools.assertlogs import LogTestCase
from golem.tools.testdirfixture import TestDirFixture

from gnr.application import GNRGui
from gnr.ui.dialog import ConfigurationDialog
from gnr.customizers.configurationdialogcustomizer import ConfigurationDialogCustomizer, logger
from gnr.ui.administrationmainwindow import AdministrationMainWindow


class TestDu(TestDirFixture):

    def test_du(self):
        files_ = self.additional_dir_content([1, [1]])
        testdir = self.path
        testdir2 = os.path.dirname(files_[1])
        testfile1 = files_[0]
        testfile2 = files_[1]
        res = ConfigurationDialogCustomizer.du("notexisting")
        self.assertEqual(res, "-1")
        res = ConfigurationDialogCustomizer.du(testdir)
        try:
            size = float(res)
        except ValueError:
            size, sym = re.split("[ kKmMgGbB]", res)[:2]
        self.assertGreaterEqual(float(size), 0.0)
        with open(os.path.join(testdir, testfile1), 'w') as f:
            f.write("a" * 10000)
        res = ConfigurationDialogCustomizer.du(testdir)
        size1, sym = re.split("[ kKmMgGbB]", res)[:2]
        self.assertGreater(float(size1), float(size))
        if not os.path.exists(testdir2):
            os.makedirs(testdir2)
        with open(os.path.join(testdir2, testfile2), 'w') as f:
            f.write("123" * 10000)
        res = ConfigurationDialogCustomizer.du(testdir)
        size2, sym = re.split("[ kKmMgGbB]", res)[:2]
        self.assertGreater(float(size2), float(size1))
        res = ConfigurationDialogCustomizer.du(".")
        try:
            size = float(res)
        except ValueError:
            size, sym = re.split("[ kKmMgGbB]", res)[:2]
        self.assertGreater(size, 0)


class TestConfigurationDialogCustomizer(LogTestCase):
    def test_min_max_price(self):
        logic_mock = MagicMock()
        gnrgui = GNRGui(MagicMock(), AdministrationMainWindow)
        logic_mock.get_res_dirs.return_value = {'computing': os.getcwd(),
                                                'distributed': os.getcwd(),
                                                'received': os.getcwd()}
        logic_mock.get_config.return_value.max_price = 10.2
        logic_mock.get_config.return_value.min_price = 2.3
        cd = ConfigurationDialog(gnrgui.main_window.window)
        customizer = ConfigurationDialogCustomizer(cd, logic_mock)
        self.assertIsInstance(customizer, ConfigurationDialogCustomizer)
        self.assertEqual(float(customizer.gui.ui.maxPriceLineEdit.text()), 10.2)
        self.assertEqual(float(customizer.gui.ui.minPriceLineEdit.text()), 2.3)
        customizer.gui.ui.maxPriceLineEdit.setText(u"{}".format(11.5))
        customizer.gui.ui.minPriceLineEdit.setText(u"{}".format(1.1))
        customizer.gui.ui.buttonBox.accepted.emit()
        ccd = logic_mock.change_config.call_args_list[0][0][0]
        self.assertEqual(ccd.min_price, 1.1)
        self.assertEqual(ccd.max_price, 11.5)
        customizer.gui.ui.maxPriceLineEdit.setText(u"ABCDEF")
        with self.assertLogs(logger, level=1):
            customizer.gui.ui.buttonBox.accepted.emit()
        customizer.gui.ui.maxPriceLineEdit.setText(u"{}".format(0.3))
        customizer.gui.ui.minPriceLineEdit.setText(u"XYZ")
        with self.assertLogs(logger, level=1):
            customizer.gui.ui.buttonBox.accepted.emit()