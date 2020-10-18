import os.path
from typing import Optional

from thonny import ui_utils, get_shell, get_workbench
from thonny.misc_utils import list_volumes
from thonny.plugins.micropython import (
    BareMetalMicroPythonProxy,
    add_micropython_backend,
    BareMetalMicroPythonConfigPage,
)
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
from thonny.ui_utils import show_dialog


class RaspberryPiPicoBackendProxy(BareMetalMicroPythonProxy):
    @property
    def consider_unknown_devices(self):
        return False

    @classmethod
    def should_consider_unknown_devices(cls):
        return False

    @property
    def known_usb_vids_pids(self):
        # TODO: get rid of this
        return {(0xF055, 0x9802)}

    @classmethod
    def get_known_usb_vids_pids(cls):
        return {(0xF055, 0x9802)}

    @classmethod
    def device_is_present_in_bootloader_mode(cls):
        return bool(PicoFlashingDialog.get_possible_targets())

    def _propose_install_firmware(self):
        dlg = PicoFlashingDialog(get_workbench())
        show_dialog(dlg)
        return dlg.success


class RaspberryPiPicoBackendConfigPage(BareMetalMicroPythonConfigPage):
    def _has_flashing_dialog(self):
        return True

    def _open_flashing_dialog(self):
        dlg = PicoFlashingDialog(self.winfo_toplevel())
        ui_utils.show_dialog(dlg)

class PicoFlashingDialog(Uf2FlashingDialog):
    def get_instructions(self) -> Optional[str]:
        return (
            "This dialog allows you to install or update MicroPython firmware on your Pico.\n"
            "\n"
            "1. Plug in your Pico while holding the BOOTSEL button.\n"
            "2. Wait until device information appears.\n"
            "3. Click 'Install' and wait for some seconds until done.\n"
            "4. Close the dialog and start programming!"
        )

    def _get_release_info_url(self):
        return "https://api.github.com/repos/raspberrypi/micropython/releases/latest"

    def _get_fallback_release_info_url(self):
        return "https://thonny.org/45624345807/index.json"

    def _is_suitable_asset(self, asset, model_id):
        if not asset["name"].endswith(".uf2") or "micropython" not in asset["name"].lower():
            return False

        return True

    @classmethod
    def _is_relevant_board_id(cls, board_id):
        return "RPI" in board_id

    def get_title(self):
        return "Install MicroPython firmware for Raspberry Pi Pico"

    def _get_vid_pids_to_wait_for(self):
        return RaspberryPiPicoBackendProxy.get_known_usb_vids_pids()

def load_plugin():
    add_micropython_backend(
        "RPiPico",
        RaspberryPiPicoBackendProxy,
        "MicroPython (Raspberry Pi Pico)",
        RaspberryPiPicoBackendConfigPage,
        bare_metal=True,
        sort_key="32",
    )
