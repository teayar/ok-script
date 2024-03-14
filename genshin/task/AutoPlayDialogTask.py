from typing_extensions import override

from autohelper.task.FindFeatureTask import FindFeatureTask
from genshin.scene.BlackDialogScene import BlackDialogScene
from genshin.scene.DialogCloseButtonScene import DialogCloseButtonScene
from genshin.scene.DialogPlayingScene import DialogPlayingScene


class AutoPlayDialogTask(FindFeatureTask):
    dialog_vertical_distance = 0

    @override
    def run_frame(self):
        # Check if the scene is an instance of DialogPlayingScene or BlackDialogScene
        if self.is_scene((DialogPlayingScene, BlackDialogScene, DialogCloseButtonScene)):
            # For DialogPlayingScene, check if the button_play is present
            if self.is_scene(DialogPlayingScene) and self.scene.button_play:
                self.logger.info("turn on auto play")
                self.click_box(self.scene.button_play)
            elif self.is_scene(DialogCloseButtonScene):
                self.logger.info("click dialog close button")
                self.click_box(self.scene.close_button)
            else:
                self.logger.info("click center of the screen, fast forward dialog")
                self.click_relative(0.5, 0.5)
            self.sleep(1)
            return True
