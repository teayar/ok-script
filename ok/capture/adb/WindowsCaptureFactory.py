from ok.logging.Logger import get_logger

logger = get_logger(__name__)


def update_capture_method(config, capture_method, hwnd, require_bg=False, use_bit_blt_only=False):
    try:
        if config.get('can_bit_blt'):
            logger.debug(
                f"try BitBlt method {config} {hwnd} current_type:{type(capture_method)}")
            from ok.capture.windows.BitBltCaptureMethod import BitBltCaptureMethod
            if config.get('bit_blt_render_full'):
                BitBltCaptureMethod.render_full = True
            target_method = BitBltCaptureMethod
            capture_method = get_capture(capture_method, target_method, hwnd)
            if capture_method.test_is_not_pure_color():
                return capture_method
            else:
                logger.info("test_is_not_pure_color failed, can't use BitBlt")
        if use_bit_blt_only:
            return None
        from ok.capture.windows.WindowsGraphicsCaptureMethod import windows_graphics_available
        if windows_graphics_available():
            from ok.capture.windows.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
            target_method = WindowsGraphicsCaptureMethod
            capture_method = get_capture(capture_method, target_method, hwnd)
            return capture_method

        if not require_bg:
            from ok.capture.windows.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
            target_method = DesktopDuplicationCaptureMethod
            capture_method = get_capture(capture_method, target_method, hwnd)
            return capture_method
    except Exception as e:
        logger.error(f'update_capture_method exception, return None: ', e)


def get_capture(capture_method, target_method, hwnd):
    if not isinstance(capture_method, target_method):
        if capture_method is not None:
            capture_method.close()
        capture_method = target_method(hwnd)
    capture_method.hwnd_window = hwnd
    return capture_method
