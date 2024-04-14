import sys
import threading
import time
from typing import Dict, Any

from PySide6.QtWidgets import QApplication

import ok
from ok.feature.FeatureSet import FeatureSet
from ok.gui.App import App
from ok.gui.Communicate import communicate
from ok.gui.overlay.OverlayWindow import OverlayWindow
from ok.gui.util.InitWorker import InitWorker
from ok.logging.Logger import get_logger, config_logger
from ok.task.TaskExecutor import TaskExecutor

logger = get_logger(__name__)


class OK:
    executor: TaskExecutor
    adb = None
    adb_device = None
    feature_set = None
    hwnd = None
    device_manager = None
    ocr = None
    overlay_window = None
    app = None

    def __init__(self, config: Dict[str, Any]):
        print(f"AutoHelper init, config: {config}")
        self.debug = config.get("debug", False)
        self.exit_event = threading.Event()
        self.config = config
        self.init_device_manager()
        if config.get("use_gui"):
            self.app = App(self.config.get('gui_icon'), self.debug, self.config.get('gui_title'),
                           self.config['tasks'], self.config.get('about'), self.exit_event)
            ok.gui.app = self.app
        else:
            self.device_manager.set_preferred_device()
            self.device_manager.start()
            self.do_init()

    def start(self):
        if self.config.get("use_gui"):
            self.app.show_loading()
            self.worker = InitWorker(self.do_init)
            self.worker.start()
            self.app.exec()
        else:
            self.task_executor.start()
            if self.config.get("debug"):
                self.app = QApplication(sys.argv)
                self.overlay_window = OverlayWindow(ok.gui.device_manager.hwnd)
                self.app.exec()
            else:
                try:
                    # Starting the task in a separate thread (optional)
                    # This allows the main thread to remain responsive to keyboard interrupts
                    task_thread = threading.Thread(target=self.wait_task())
                    task_thread.start()

                    # Wait for the task thread to end (which it won't, in this case, without an interrupt)
                    task_thread.join()
                except KeyboardInterrupt:
                    self.exit_event.set()
                    logger.info("Keyboard interrupt received, exiting script.")
                finally:
                    # Clean-up code goes here (if any)
                    # This block ensures that the script terminates gracefully,
                    # releasing resources or performing necessary clean-up operations.
                    logger.info("Script has terminated.")

    def init_message(self, message: str, done=False):
        communicate.init.emit(done, message)
        if self.exit_event.is_set():
            self.worker.quit()

    def do_init(self):
        logger.info(f"initializing {self.__class__.__name__}, config: {self.config}")
        if self.config.get('ocr'):
            self.init_message("RapidOCR init Start")
            from rapidocr_onnxruntime import RapidOCR
            self.ocr = RapidOCR()
            self.init_message("RapidOCR init Complete")

        config_logger(self.config)

        if self.config.get('coco_feature_folder') is not None:
            self.init_message("FeatureSet init Start")
            coco_feature_folder = self.config.get('coco_feature_folder')
            self.feature_set = FeatureSet(coco_feature_folder,
                                          default_horizontal_variance=self.config.get('default_horizontal_variance', 0),
                                          default_vertical_variance=self.config.get('default_vertical_variance', 0),
                                          default_threshold=self.config.get('default_threshold', 0))
            self.init_message("FeatureSet init Complete")

        self.init_message("TaskExecutor init Start")
        self.task_executor = TaskExecutor(self.device_manager, exit_event=self.exit_event,
                                          tasks=self.config['tasks'], scenes=self.config['scenes'],
                                          feature_set=self.feature_set,
                                          ocr=self.ocr, config_folder=self.config.get("config_folder") or "config")
        self.init_message("TaskExecutor init Done")

        if self.app:
            ok.gui.executor = self.task_executor

    def wait_task(self):
        while not self.exit_event.is_set():
            time.sleep(1)

    def init_device_manager(self):
        if self.device_manager is None:
            from ok.capture.adb.DeviceManager import DeviceManager
            self.device_manager = DeviceManager(self.config.get("config_folder") or "config",
                                                self.config.get('capture_window_title'), self.config.get("debug"),
                                                self.exit_event)
            ok.gui.device_manager = self.device_manager
