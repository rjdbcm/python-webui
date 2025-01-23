import ctypes
import sys
from ctypes import *
import subprocess
import os
import platform
import enum


def _get_current_folder() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _get_architecture() -> str:
    arch = platform.machine()
    if arch in ['x86_64', 'AMD64', 'amd64']:
        return 'x64'
    elif arch in ['aarch64', 'ARM64', 'arm64']:
        return 'arm64'
    elif arch in ['arm']:
        return 'arm'
    else:
        return arch


def _get_library_folder_name() -> str:
    arch = _get_architecture()
    if platform.system() == 'Darwin':
        return f'/webui-macos-clang-{arch}/webui-2.dylib'
    elif platform.system() == 'Windows':
        return f'\\webui-windows-msvc-{arch}\\webui-2.dll'
    elif platform.system() == 'Linux':
        return f'/webui-linux-gcc-{arch}/webui-2.so'
    else:
        return ""


def _get_library_path() -> str:
    folderName = _get_library_folder_name()
    return _get_current_folder() + folderName


def run_cmd(command):
    subprocess.run(command, shell=True)


def _download_library():
    script = 'sh bootstrap.sh'
    cd = 'cd '
    if platform.system() == 'Windows':
        script = 'bootstrap.bat'
        cd = 'cd /d '
    # Run: `cd {folder} && bootstrap.sh minimal`
    run_cmd(cd + _get_current_folder() +
               ' && ' + script + ' minimal')


# Load WebUI Dynamic Library
def _load_library() -> ctypes.CDLL | None:
    library: ctypes.CDLL | None = None
    lib_path = _get_library_path()
    if not os.path.exists(lib_path):
        _download_library()

    if not os.path.exists(lib_path):
        return library

    if platform.system() == 'Darwin':
        library = ctypes.CDLL(lib_path)
        if library is None:
            print("WebUI Dynamic Library not found.")
    elif platform.system() == 'Windows':
        if sys.version_info.major==3 and sys.version_info.minor<=8:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            library = ctypes.CDLL(lib_path)
        else:
            os.chdir(os.getcwd())
            os.add_dll_directory(os.getcwd())
            library = cdll.LoadLibrary(lib_path)
        if library is None:
            print("WebUI Dynamic Library not found.")
    elif platform.system() == 'Linux':
        library = ctypes.CDLL(lib_path)
        if library is None:
            print("WebUI Dynamic Library not found.")
    else:
        print("Unsupported OS")

    return library




# 1) Load the shared library
lib: CDLL | None = _load_library()
if lib is None:
    print('WebUI Dynamic Library not found.')
    sys.exit(1)
else:
    webui_lib: CDLL = lib


class WebuiBrowser(enum.IntEnum):
    NoBrowser      = 0    # 0. No web browser
    AnyBrowser     = 1    # 1. Default recommended web browser
    Chrome         = 2    # 2. Google Chrome
    Firefox        = 3    # 3. Mozilla Firefox
    Edge           = 4    # 4. Microsoft Edge
    Safari         = 5    # 5. Apple Safari
    Chromium       = 6    # 6. The Chromium Project
    Opera          = 7    # 7. Opera Browser
    Brave          = 8    # 8. The Brave Browser
    Vivaldi        = 9    # 9. The Vivaldi Browser
    Epic           = 10   # 10. The Epic Browser
    Yandex         = 11   # 11. The Yandex Browser
    ChromiumBased  = 12   # 12. Any Chromium based browser
    Webview        = 13   # 13. WebView (Non-web-browser)


# 2) Define the WebuiEventT struct
class WebuiEventT(Structure):
    _fields_ = [
        ("window",        c_size_t),
        ("event_type",    c_size_t),
        ("element",       c_char_p),
        ("event_number",  c_size_t),
        ("bind_id",       c_size_t),
        ("client_id",     c_size_t),
        ("connection_id", c_size_t),
        ("cookies",       c_char_p),
    ]

# 3) (Optional) Define a function pointer type for callbacks
#    In C: void (*func)(webui_event_t* e)
WEBUI_CALLBACK = CFUNCTYPE(None, POINTER(WebuiEventT))


# 4) Wrap each needed function:

# size_t webui_new_window(void);
webui_new_window = webui_lib.webui_new_window
webui_new_window.argtypes = []
webui_new_window.restype  = c_size_t

# size_t webui_new_window_id(size_t window_number);
webui_new_window_id = webui_lib.webui_new_window_id
webui_new_window_id.argtypes = [c_size_t]
webui_new_window_id.restype  = c_size_t

# size_t webui_get_new_window_id(void);
webui_get_new_window_id = webui_lib.webui_get_new_window_id
webui_get_new_window_id.argtypes = []
webui_get_new_window_id.restype  = c_size_t

# size_t webui_bind(size_t window, const char* element, void (*func)(webui_event_t* e));
webui_bind = webui_lib.webui_bind
webui_bind.argtypes = [c_size_t, c_char_p, WEBUI_CALLBACK]
webui_bind.restype  = c_size_t

# size_t webui_get_best_browser(size_t window);
webui_get_best_browser = webui_lib.webui_get_best_browser
webui_get_best_browser.argtypes = [c_size_t]
webui_get_best_browser.restype  = c_size_t

# bool webui_show(size_t window, const char* content);
webui_show = webui_lib.webui_show
webui_show.argtypes = [c_size_t, c_char_p]
webui_show.restype  = c_bool

# bool webui_show_client(webui_event_t* e, const char* content);
webui_show_client = webui_lib.webui_show_client
webui_show_client.argtypes = [POINTER(WebuiEventT), c_char_p]
webui_show_client.restype  = c_bool

# bool webui_show_browser(size_t window, const char* content, size_t browser);
webui_show_browser = webui_lib.webui_show_browser
webui_show_browser.argtypes = [c_size_t, c_char_p, c_size_t]
webui_show_browser.restype  = c_bool

# const char* webui_start_server(size_t window, const char* content);
webui_start_server = webui_lib.webui_start_server
webui_start_server.argtypes = [c_size_t, c_char_p]
webui_start_server.restype  = c_char_p

# bool webui_show_wv(size_t window, const char* content);
webui_show_wv = webui_lib.webui_show_wv
webui_show_wv.argtypes = [c_size_t, c_char_p]
webui_show_wv.restype  = c_bool

# void webui_set_kiosk(size_t window, bool status);
webui_set_kiosk = webui_lib.webui_set_kiosk
webui_set_kiosk.argtypes = [c_size_t, c_bool]
webui_set_kiosk.restype  = None

# void webui_set_custom_parameters(size_t window, char* params);
webui_set_custom_parameters = webui_lib.webui_set_custom_parameters
webui_set_custom_parameters.argtypes = [c_size_t, c_char_p]
webui_set_custom_parameters.restype  = None

# bool webui_browser_exist(size_t browser);
webui_browser_exist = webui_lib.webui_browser_exist
webui_browser_exist.argtypes = [c_size_t]
webui_browser_exist.restype  = c_bool

# void webui_wait(void);
webui_wait = webui_lib.webui_wait
webui_wait.argtypes = []
webui_wait.restype  = None

# void webui_close(size_t window);
webui_close = webui_lib.webui_close
webui_close.argtypes = [c_size_t]
webui_close.restype  = None

# void webui_exit(void);
webui_exit = webui_lib.webui_exit
webui_exit.argtypes = []
webui_exit.restype = None

# bool webui_is_high_contrast(void);
webui_is_high_contrast = webui_lib.webui_is_high_contrast
webui_is_high_contrast.argtypes = []
webui_is_high_contrast.restype = c_bool

# /*
#   WebUI Library
#   https://webui.me
#   https://github.com/webui-dev/webui
#   Copyright (c) 2020-2024 Hassan Draga.
#   Licensed under MIT License.
#   All rights reserved.
#   Canada.
# */

# // -- Enums ---------------------------
# enum webui_browser {
#     NoBrowser = 0,  // 0. No web browser
#     AnyBrowser = 1, // 1. Default recommended web browser
#     Chrome,         // 2. Google Chrome
#     Firefox,        // 3. Mozilla Firefox
#     Edge,           // 4. Microsoft Edge
#     Safari,         // 5. Apple Safari
#     Chromium,       // 6. The Chromium Project
#     Opera,          // 7. Opera Browser
#     Brave,          // 8. The Brave Browser
#     Vivaldi,        // 9. The Vivaldi Browser
#     Epic,           // 10. The Epic Browser
#     Yandex,         // 11. The Yandex Browser
#     ChromiumBased,  // 12. Any Chromium based browser
#     Webview,        // 13. WebView (Non-web-browser)
# };
#
# enum webui_runtime {
#     None = 0, // 0. Prevent WebUI from using any runtime for .js and .ts files
#     Deno,     // 1. Use Deno runtime for .js and .ts files
#     NodeJS,   // 2. Use Nodejs runtime for .js files
#     Bun,      // 3. Use Bun runtime for .js and .ts files
# };
#
# enum webui_event {
#     WEBUI_EVENT_DISCONNECTED = 0, // 0. Window disconnection event
#     WEBUI_EVENT_CONNECTED,        // 1. Window connection event
#     WEBUI_EVENT_MOUSE_CLICK,      // 2. Mouse click event
#     WEBUI_EVENT_NAVIGATION,       // 3. Window navigation event
#     WEBUI_EVENT_CALLBACK,         // 4. Function call event
# };
#
# typedef enum {
#     // Control if `webui_show()`, `webui_show_browser()` and
#     // `webui_show_wv()` should wait for the window to connect
#     // before returns or not.
#     //
#     // Default: True
#     show_wait_connection = 0,
#     // Control if WebUI should block and process the UI events
#     // one a time in a single thread `True`, or process every
#     // event in a new non-blocking thread `False`. This updates
#     // all windows. You can use `webui_set_event_blocking()` for
#     // a specific single window update.
#     //
#     // Default: False
#     ui_event_blocking,
#     // Automatically refresh the window UI when any file in the
#     // root folder gets changed.
#     //
#     // Default: False
#     folder_monitor,
#     // Allow multiple clients to connect to the same window,
#     // This is helpful for web apps (non-desktop software),
#     // Please see the documentation for more details.
#     //
#     // Default: False
#     multi_client,
#     // Allow or prevent WebUI from adding `webui_auth` cookies.
#     // WebUI uses these cookies to identify clients and block
#     // unauthorized access to the window content using a URL.
#     // Please keep this option to `True` if you want only a single
#     // client to access the window content.
#     //
#     // Default: True
#     use_cookies,
#     // If the backend uses asynchronous operations, set this
#     // option to `True`. This will make webui wait until the
#     // backend sets a response using `webui_return_x()`.
#     asynchronous_response
# } webui_config;
#
# // -- Structs -------------------------
# typedef struct webui_event_t {
#     size_t window;          // The window object number
#     size_t event_type;      // Event type
#     char* element;          // HTML element ID
#     size_t event_number;    // Internal WebUI
#     size_t bind_id;         // Bind ID
#     size_t client_id;       // Client's unique ID
#     size_t connection_id;   // Client's connection ID
#     char* cookies;          // Client's full cookies
# } webui_event_t;
#
# // -- Definitions ---------------------
#
# /**
#  * @brief Create a new WebUI window object.
#  *
#  * @return Returns the window number.
#  *
#  * @example size_t myWindow = webui_new_window();
#  */
# WEBUI_EXPORT size_t webui_new_window(void);
#
# /**
#  * @brief Create a new webui window object using a specified window number.
#  *
#  * @param window_number The window number (should be > 0, and < WEBUI_MAX_IDS)
#  *
#  * @return Returns the same window number if success.
#  *
#  * @example size_t myWindow = webui_new_window_id(123);
#  */
# WEBUI_EXPORT size_t webui_new_window_id(size_t window_number);
#
# /**
#  * @brief Get a free window number that can be used with
#  * `webui_new_window_id()`.
#  *
#  * @return Returns the first available free window number. Starting from 1.
#  *
#  * @example size_t myWindowNumber = webui_get_new_window_id();
#  */
# WEBUI_EXPORT size_t webui_get_new_window_id(void);
#
# /**
#  * @brief Bind an HTML element and a JavaScript object with a backend function. Empty
#  * element name means all events.
#  *
#  * @param window The window number
#  * @param element The HTML element / JavaScript object
#  * @param func The callback function
#  *
#  * @return Returns a unique bind ID.
#  *
#  * @example webui_bind(myWindow, "myFunction", myFunction);
#  */
# WEBUI_EXPORT size_t webui_bind(size_t window, const char* element, void (*func)(webui_event_t* e));
#
# /**
#  * @brief Get the recommended web browser ID to use. If you
#  * are already using one, this function will return the same ID.
#  *
#  * @param window The window number
#  *
#  * @return Returns a web browser ID.
#  *
#  * @example size_t browserID = webui_get_best_browser(myWindow);
#  */
# WEBUI_EXPORT size_t webui_get_best_browser(size_t window);
#
# /**
#  * @brief Show a window using embedded HTML, or a file. If the window is already
#  * open, it will be refreshed. This will refresh all windows in multi-client mode.
#  *
#  * @param window The window number
#  * @param content The HTML, URL, Or a local file
#  *
#  * @return Returns True if showing the window is successed.
#  *
#  * @example webui_show(myWindow, "<html>...</html>"); |
#  * webui_show(myWindow, "index.html"); | webui_show(myWindow, "http://...");
#  */
# WEBUI_EXPORT bool webui_show(size_t window, const char* content);
#
# /**
#  * @brief Show a window using embedded HTML, or a file. If the window is already
#  * open, it will be refreshed. Single client.
#  *
#  * @param e The event struct
#  * @param content The HTML, URL, Or a local file
#  *
#  * @return Returns True if showing the window is successed.
#  *
#  * @example webui_show_client(e, "<html>...</html>"); |
#  * webui_show_client(e, "index.html"); | webui_show_client(e, "http://...");
#  */
# WEBUI_EXPORT bool webui_show_client(webui_event_t* e, const char* content);
#
# /**
#  * @brief Same as `webui_show()`. But using a specific web browser.
#  *
#  * @param window The window number
#  * @param content The HTML, Or a local file
#  * @param browser The web browser to be used
#  *
#  * @return Returns True if showing the window is successed.
#  *
#  * @example webui_show_browser(myWindow, "<html>...</html>", Chrome); |
#  * webui_show(myWindow, "index.html", Firefox);
#  */
# WEBUI_EXPORT bool webui_show_browser(size_t window, const char* content, size_t browser);
#
# /**
#  * @brief Same as `webui_show()`. But start only the web server and return the URL.
#  * No window will be shown.
#  *
#  * @param window The window number
#  * @param content The HTML, Or a local file
#  *
#  * @return Returns the url of this window server.
#  *
#  * @example const char* url = webui_start_server(myWindow, "/full/root/path");
#  */
# WEBUI_EXPORT const char* webui_start_server(size_t window, const char* content);
#
# /**
#  * @brief Show a WebView window using embedded HTML, or a file. If the window is already
#  * open, it will be refreshed. Note: Win32 need `WebView2Loader.dll`.
#  *
#  * @param window The window number
#  * @param content The HTML, URL, Or a local file
#  *
#  * @return Returns True if showing the WebView window is successed.
#  *
#  * @example webui_show_wv(myWindow, "<html>...</html>"); | webui_show_wv(myWindow,
#  * "index.html"); | webui_show_wv(myWindow, "http://...");
#  */
# WEBUI_EXPORT bool webui_show_wv(size_t window, const char* content);
#
# /**
#  * @brief Set the window in Kiosk mode (Full screen).
#  *
#  * @param window The window number
#  * @param status True or False
#  *
#  * @example webui_set_kiosk(myWindow, true);
#  */
# WEBUI_EXPORT void webui_set_kiosk(size_t window, bool status);
#
# /**
#  * @brief Add a user-defined web browser's CLI parameters.
#  *
#  * @param window The window number
#  * @param params Command line parameters
#  *
#  * @example webui_set_custom_parameters(myWindow, "--remote-debugging-port=9222");
#  */
# WEBUI_EXPORT void webui_set_custom_parameters(size_t window, char *params);
#
# /**
#  * @brief Set the window with high-contrast support. Useful when you want to
#  * build a better high-contrast theme with CSS.
#  *
#  * @param window The window number
#  * @param status True or False
#  *
#  * @example webui_set_high_contrast(myWindow, true);
#  */
# WEBUI_EXPORT void webui_set_high_contrast(size_t window, bool status);
#
# /**
#  * @brief Get OS high contrast preference.
#  *
#  * @return Returns True if OS is using high contrast theme
#  *
#  * @example bool hc = webui_is_high_contrast();
#  */
# WEBUI_EXPORT bool webui_is_high_contrast(void);
#
# /**
#  * @brief Check if a web browser is installed.
#  *
#  * @return Returns True if the specified browser is available
#  *
#  * @example bool status = webui_browser_exist(Chrome);
#  */
# WEBUI_EXPORT bool webui_browser_exist(size_t browser);
#
# /**
#  * @brief Wait until all opened windows get closed.
#  *
#  * @example webui_wait();
#  */
# WEBUI_EXPORT void webui_wait(void);
#
# /**
#  * @brief Close a specific window only. The window object will still exist.
#  * All clients.
#  *
#  * @param window The window number
#  *
#  * @example webui_close(myWindow);
#  */
# WEBUI_EXPORT void webui_close(size_t window);
#
# /**
#  * @brief Close a specific client.
#  *
#  * @param e The event struct
#  *
#  * @example webui_close_client(e);
#  */
# WEBUI_EXPORT void webui_close_client(webui_event_t* e);
#
# /**
#  * @brief Close a specific window and free all memory resources.
#  *
#  * @param window The window number
#  *
#  * @example webui_destroy(myWindow);
#  */
# WEBUI_EXPORT void webui_destroy(size_t window);
#
# /**
#  * @brief Close all open windows. `webui_wait()` will return (Break).
#  *
#  * @example webui_exit();
#  */
# WEBUI_EXPORT void webui_exit(void);
#
# /**
#  * @brief Set the web-server root folder path for a specific window.
#  *
#  * @param window The window number
#  * @param path The local folder full path
#  *
#  * @example webui_set_root_folder(myWindow, "/home/Foo/Bar/");
#  */
# WEBUI_EXPORT bool webui_set_root_folder(size_t window, const char* path);
#
# /**
#  * @brief Set the web-server root folder path for all windows. Should be used
#  * before `webui_show()`.
#  *
#  * @param path The local folder full path
#  *
#  * @example webui_set_default_root_folder("/home/Foo/Bar/");
#  */
# WEBUI_EXPORT bool webui_set_default_root_folder(const char* path);
#
# /**
#  * @brief Set a custom handler to serve files. This custom handler should
#  * return full HTTP header and body.
#  * This deactivates any previous handler set with `webui_set_file_handler_window`
#  *
#  * @param window The window number
#  * @param handler The handler function: `void myHandler(const char* filename,
#  * int* length)`
#  *
#  * @example webui_set_file_handler(myWindow, myHandlerFunction);
#  */
# WEBUI_EXPORT void webui_set_file_handler(size_t window, const void* (*handler)(const char* filename, int* length));
#
# /**
#  * @brief Set a custom handler to serve files. This custom handler should
#  * return full HTTP header and body.
#  * This deactivates any previous handler set with `webui_set_file_handler`
#  *
#  * @param window The window number
#  * @param handler The handler function: `void myHandler(size_t window, const char* filename,
#  * int* length)`
#  *
#  * @example webui_set_file_handler_window(myWindow, myHandlerFunction);
#  */
# WEBUI_EXPORT void webui_set_file_handler_window(size_t window, const void* (*handler)(size_t window, const char* filename, int* length));
#
#
# /**
#  * @brief Check if the specified window is still running.
#  *
#  * @param window The window number
#  *
#  * @example webui_is_shown(myWindow);
#  */
# WEBUI_EXPORT bool webui_is_shown(size_t window);
#
# /**
#  * @brief Set the maximum time in seconds to wait for the window to connect.
#  * This effect `show()` and `wait()`. Value of `0` means wait forever.
#  *
#  * @param second The timeout in seconds
#  *
#  * @example webui_set_timeout(30);
#  */
# WEBUI_EXPORT void webui_set_timeout(size_t second);
#
# /**
#  * @brief Set the default embedded HTML favicon.
#  *
#  * @param window The window number
#  * @param icon The icon as string: `<svg>...</svg>`
#  * @param icon_type The icon type: `image/svg+xml`
#  *
#  * @example webui_set_icon(myWindow, "<svg>...</svg>", "image/svg+xml");
#  */
# WEBUI_EXPORT void webui_set_icon(size_t window, const char* icon, const char* icon_type);
#
# /**
#  * @brief Encode text to Base64. The returned buffer need to be freed.
#  *
#  * @param str The string to encode (Should be null terminated)
#  *
#  * @return Returns the base64 encoded string
#  *
#  * @example char* base64 = webui_encode("Foo Bar");
#  */
# WEBUI_EXPORT char* webui_encode(const char* str);
#
# /**
#  * @brief Decode a Base64 encoded text. The returned buffer need to be freed.
#  *
#  * @param str The string to decode (Should be null terminated)
#  *
#  * @return Returns the base64 decoded string
#  *
#  * @example char* str = webui_decode("SGVsbG8=");
#  */
# WEBUI_EXPORT char* webui_decode(const char* str);
#
# /**
#  * @brief Safely free a buffer allocated by WebUI using `webui_malloc()`.
#  *
#  * @param ptr The buffer to be freed
#  *
#  * @example webui_free(myBuffer);
#  */
# WEBUI_EXPORT void webui_free(void* ptr);
#
# /**
#  * @brief Safely allocate memory using the WebUI memory management system. It
#  * can be safely freed using `webui_free()` at any time.
#  *
#  * @param size The size of memory in bytes
#  *
#  * @example char* myBuffer = (char*)webui_malloc(1024);
#  */
# WEBUI_EXPORT void* webui_malloc(size_t size);
#
# /**
#  * @brief Safely send raw data to the UI. All clients.
#  *
#  * @param window The window number
#  * @param function The JavaScript function to receive raw data: `function
#  * myFunc(myData){}`
#  * @param raw The raw data buffer
#  * @param size The raw data size in bytes
#  *
#  * @example webui_send_raw(myWindow, "myJavaScriptFunc", myBuffer, 64);
#  */
# WEBUI_EXPORT void webui_send_raw(size_t window, const char* function, const void* raw, size_t size);
#
# /**
#  * @brief Safely send raw data to the UI. Single client.
#  *
#  * @param e The event struct
#  * @param function The JavaScript function to receive raw data: `function
#  * myFunc(myData){}`
#  * @param raw The raw data buffer
#  * @param size The raw data size in bytes
#  *
#  * @example webui_send_raw_client(e, "myJavaScriptFunc", myBuffer, 64);
#  */
# WEBUI_EXPORT void webui_send_raw_client(webui_event_t* e, const char* function,
#     const void* raw, size_t size);
#
# /**
#  * @brief Set a window in hidden mode. Should be called before `webui_show()`.
#  *
#  * @param window The window number
#  * @param status The status: True or False
#  *
#  * @example webui_set_hide(myWindow, True);
#  */
# WEBUI_EXPORT void webui_set_hide(size_t window, bool status);
#
# /**
#  * @brief Set the window size.
#  *
#  * @param window The window number
#  * @param width The window width
#  * @param height The window height
#  *
#  * @example webui_set_size(myWindow, 800, 600);
#  */
# WEBUI_EXPORT void webui_set_size(size_t window, unsigned int width, unsigned int height);
#
# /**
#  * @brief Set the window minimum size.
#  *
#  * @param window The window number
#  * @param width The window width
#  * @param height The window height
#  *
#  * @example webui_set_minimum_size(myWindow, 800, 600);
#  */
# WEBUI_EXPORT void webui_set_minimum_size(size_t window, unsigned int width, unsigned int height);
#
# /**
#  * @brief Set the window position.
#  *
#  * @param window The window number
#  * @param x The window X
#  * @param y The window Y
#  *
#  * @example webui_set_position(myWindow, 100, 100);
#  */
# WEBUI_EXPORT void webui_set_position(size_t window, unsigned int x, unsigned int y);
#
# /**
#  * @brief Set the web browser profile to use. An empty `name` and `path` means
#  * the default user profile. Need to be called before `webui_show()`.
#  *
#  * @param window The window number
#  * @param name The web browser profile name
#  * @param path The web browser profile full path
#  *
#  * @example webui_set_profile(myWindow, "Bar", "/Home/Foo/Bar"); |
#  * webui_set_profile(myWindow, "", "");
#  */
# WEBUI_EXPORT void webui_set_profile(size_t window, const char* name, const char* path);
#
# /**
#  * @brief Set the web browser proxy server to use. Need to be called before `webui_show()`.
#  *
#  * @param window The window number
#  * @param proxy_server The web browser proxy_server
#  *
#  * @example webui_set_proxy(myWindow, "http://127.0.0.1:8888");
#  */
# WEBUI_EXPORT void webui_set_proxy(size_t window, const char* proxy_server);
#
# /**
#  * @brief Get current URL of a running window.
#  *
#  * @param window The window number
#  *
#  * @return Returns the full URL string
#  *
#  * @example const char* url = webui_get_url(myWindow);
#  */
# WEBUI_EXPORT const char* webui_get_url(size_t window);
#
# /**
#  * @brief Open an URL in the native default web browser.
#  *
#  * @param url The URL to open
#  *
#  * @example webui_open_url("https://webui.me");
#  */
# WEBUI_EXPORT void webui_open_url(const char* url);
#
# /**
#  * @brief Allow a specific window address to be accessible from a public network.
#  *
#  * @param window The window number
#  * @param status True or False
#  *
#  * @example webui_set_public(myWindow, true);
#  */
# WEBUI_EXPORT void webui_set_public(size_t window, bool status);
#
# /**
#  * @brief Navigate to a specific URL. All clients.
#  *
#  * @param window The window number
#  * @param url Full HTTP URL
#  *
#  * @example webui_navigate(myWindow, "http://domain.com");
#  */
# WEBUI_EXPORT void webui_navigate(size_t window, const char* url);
#
# /**
#  * @brief Navigate to a specific URL. Single client.
#  *
#  * @param e The event struct
#  * @param url Full HTTP URL
#  *
#  * @example webui_navigate_client(e, "http://domain.com");
#  */
# WEBUI_EXPORT void webui_navigate_client(webui_event_t* e, const char* url);
#
# /**
#  * @brief Free all memory resources. Should be called only at the end.
#  *
#  * @example
#  * webui_wait();
#  * webui_clean();
#  */
# WEBUI_EXPORT void webui_clean(void);
#
# /**
#  * @brief Delete all local web-browser profiles folder. It should be called at the
#  * end.
#  *
#  * @example
#  * webui_wait();
#  * webui_delete_all_profiles();
#  * webui_clean();
#  */
# WEBUI_EXPORT void webui_delete_all_profiles(void);
#
# /**
#  * @brief Delete a specific window web-browser local folder profile.
#  *
#  * @param window The window number
#  *
#  * @example
#  * webui_wait();
#  * webui_delete_profile(myWindow);
#  * webui_clean();
#  *
#  * @note This can break functionality of other windows if using the same
#  * web-browser.
#  */
# WEBUI_EXPORT void webui_delete_profile(size_t window);
#
# /**
#  * @brief Get the ID of the parent process (The web browser may re-create
#  * another new process).
#  *
#  * @param window The window number
#  *
#  * @return Returns the the parent process id as integer
#  *
#  * @example size_t id = webui_get_parent_process_id(myWindow);
#  */
# WEBUI_EXPORT size_t webui_get_parent_process_id(size_t window);
#
# /**
#  * @brief Get the ID of the last child process.
#  *
#  * @param window The window number
#  *
#  * @return Returns the the child process id as integer
#  *
#  * @example size_t id = webui_get_child_process_id(myWindow);
#  */
# WEBUI_EXPORT size_t webui_get_child_process_id(size_t window);
#
# /**
#  * @brief Get the network port of a running window.
#  * This can be useful to determine the HTTP link of `webui.js`
#  *
#  * @param window The window number
#  *
#  * @return Returns the network port of the window
#  *
#  * @example size_t port = webui_get_port(myWindow);
#  */
# WEBUI_EXPORT size_t webui_get_port(size_t window);
#
# /**
#  * @brief Set a custom web-server/websocket network port to be used by WebUI.
#  * This can be useful to determine the HTTP link of `webui.js` in case
#  * you are trying to use WebUI with an external web-server like NGNIX.
#  *
#  * @param window The window number
#  * @param port The web-server network port WebUI should use
#  *
#  * @return Returns True if the port is free and usable by WebUI
#  *
#  * @example bool ret = webui_set_port(myWindow, 8080);
#  */
# WEBUI_EXPORT bool webui_set_port(size_t window, size_t port);
#
# /**
#  * @brief Get an available usable free network port.
#  *
#  * @return Returns a free port
#  *
#  * @example size_t port = webui_get_free_port();
#  */
# WEBUI_EXPORT size_t webui_get_free_port(void);
#
# /**
#  * @brief Control the WebUI behaviour. It's recommended to be called at the beginning.
#  *
#  * @param option The desired option from `webui_config` enum
#  * @param status The status of the option, `true` or `false`
#  *
#  * @example webui_set_config(show_wait_connection, false);
#  */
# WEBUI_EXPORT void webui_set_config(webui_config option, bool status);
#
# /**
#  * @brief Control if UI events comming from this window should be processed
#  * one a time in a single blocking thread `True`, or process every event in
#  * a new non-blocking thread `False`. This update single window. You can use
#  * `webui_set_config(ui_event_blocking, ...)` to update all windows.
#  *
#  * @param window The window number
#  * @param status The blocking status `true` or `false`
#  *
#  * @example webui_set_event_blocking(myWindow, true);
#  */
# WEBUI_EXPORT void webui_set_event_blocking(size_t window, bool status);
#
# /**
#  * @brief Get the HTTP mime type of a file.
#  *
#  * @return Returns the HTTP mime string
#  *
#  * @example const char* mime = webui_get_mime_type("foo.png");
#  */
# WEBUI_EXPORT const char* webui_get_mime_type(const char* file);
#
# // -- SSL/TLS -------------------------
#
# /**
#  * @brief Set the SSL/TLS certificate and the private key content, both in PEM
#  * format. This works only with `webui-2-secure` library. If set empty WebUI
#  * will generate a self-signed certificate.
#  *
#  * @param certificate_pem The SSL/TLS certificate content in PEM format
#  * @param private_key_pem The private key content in PEM format
#  *
#  * @return Returns True if the certificate and the key are valid.
#  *
#  * @example bool ret = webui_set_tls_certificate("-----BEGIN
#  * CERTIFICATE-----\n...", "-----BEGIN PRIVATE KEY-----\n...");
#  */
# WEBUI_EXPORT bool webui_set_tls_certificate(const char* certificate_pem, const char* private_key_pem);
#
# // -- JavaScript ----------------------
#
# /**
#  * @brief Run JavaScript without waiting for the response. All clients.
#  *
#  * @param window The window number
#  * @param script The JavaScript to be run
#  *
#  * @example webui_run(myWindow, "alert('Hello');");
#  */
# WEBUI_EXPORT void webui_run(size_t window, const char* script);
#
# /**
#  * @brief Run JavaScript without waiting for the response. Single client.
#  *
#  * @param e The event struct
#  * @param script The JavaScript to be run
#  *
#  * @example webui_run_client(e, "alert('Hello');");
#  */
# WEBUI_EXPORT void webui_run_client(webui_event_t* e, const char* script);
#
# /**
#  * @brief Run JavaScript and get the response back. Work only in single client mode.
#  * Make sure your local buffer can hold the response.
#  *
#  * @param window The window number
#  * @param script The JavaScript to be run
#  * @param timeout The execution timeout in seconds
#  * @param buffer The local buffer to hold the response
#  * @param buffer_length The local buffer size
#  *
#  * @return Returns True if there is no execution error
#  *
#  * @example bool err = webui_script(myWindow, "return 4 + 6;", 0, myBuffer, myBufferSize);
#  */
# WEBUI_EXPORT bool webui_script(size_t window, const char* script, size_t timeout,
#     char* buffer, size_t buffer_length);
#
# /**
#  * @brief Run JavaScript and get the response back. Single client.
#  * Make sure your local buffer can hold the response.
#  *
#  * @param e The event struct
#  * @param script The JavaScript to be run
#  * @param timeout The execution timeout in seconds
#  * @param buffer The local buffer to hold the response
#  * @param buffer_length The local buffer size
#  *
#  * @return Returns True if there is no execution error
#  *
#  * @example bool err = webui_script_client(e, "return 4 + 6;", 0, myBuffer, myBufferSize);
#  */
# WEBUI_EXPORT bool webui_script_client(webui_event_t* e, const char* script, size_t timeout,
#     char* buffer, size_t buffer_length);
#
# /**
#  * @brief Chose between Deno and Nodejs as runtime for .js and .ts files.
#  *
#  * @param window The window number
#  * @param runtime Deno | Bun | Nodejs | None
#  *
#  * @example webui_set_runtime(myWindow, Deno);
#  */
# WEBUI_EXPORT void webui_set_runtime(size_t window, size_t runtime);
#
# /**
#  * @brief Get how many arguments there are in an event.
#  *
#  * @param e The event struct
#  *
#  * @return Returns the arguments count.
#  *
#  * @example size_t count = webui_get_count(e);
#  */
# WEBUI_EXPORT size_t webui_get_count(webui_event_t* e);
#
# /**
#  * @brief Get an argument as integer at a specific index.
#  *
#  * @param e The event struct
#  * @param index The argument position starting from 0
#  *
#  * @return Returns argument as integer
#  *
#  * @example long long int myNum = webui_get_int_at(e, 0);
#  */
# WEBUI_EXPORT long long int webui_get_int_at(webui_event_t* e, size_t index);
#
# /**
#  * @brief Get the first argument as integer.
#  *
#  * @param e The event struct
#  *
#  * @return Returns argument as integer
#  *
#  * @example long long int myNum = webui_get_int(e);
#  */
# WEBUI_EXPORT long long int webui_get_int(webui_event_t* e);
#
# /**
#  * @brief Get an argument as float at a specific index.
#  *
#  * @param e The event struct
#  * @param index The argument position starting from 0
#  *
#  * @return Returns argument as float
#  *
#  * @example double myNum = webui_get_float_at(e, 0);
#  */
# WEBUI_EXPORT double webui_get_float_at(webui_event_t* e, size_t index);
#
# /**
#  * @brief Get the first argument as float.
#  *
#  * @param e The event struct
#  *
#  * @return Returns argument as float
#  *
#  * @example double myNum = webui_get_float(e);
#  */
# WEBUI_EXPORT double webui_get_float(webui_event_t* e);
#
# /**
#  * @brief Get an argument as string at a specific index.
#  *
#  * @param e The event struct
#  * @param index The argument position starting from 0
#  *
#  * @return Returns argument as string
#  *
#  * @example const char* myStr = webui_get_string_at(e, 0);
#  */
# WEBUI_EXPORT const char* webui_get_string_at(webui_event_t* e, size_t index);
#
# /**
#  * @brief Get the first argument as string.
#  *
#  * @param e The event struct
#  *
#  * @return Returns argument as string
#  *
#  * @example const char* myStr = webui_get_string(e);
#  */
# WEBUI_EXPORT const char* webui_get_string(webui_event_t* e);
#
# /**
#  * @brief Get an argument as boolean at a specific index.
#  *
#  * @param e The event struct
#  * @param index The argument position starting from 0
#  *
#  * @return Returns argument as boolean
#  *
#  * @example bool myBool = webui_get_bool_at(e, 0);
#  */
# WEBUI_EXPORT bool webui_get_bool_at(webui_event_t* e, size_t index);
#
# /**
#  * @brief Get the first argument as boolean.
#  *
#  * @param e The event struct
#  *
#  * @return Returns argument as boolean
#  *
#  * @example bool myBool = webui_get_bool(e);
#  */
# WEBUI_EXPORT bool webui_get_bool(webui_event_t* e);
#
# /**
#  * @brief Get the size in bytes of an argument at a specific index.
#  *
#  * @param e The event struct
#  * @param index The argument position starting from 0
#  *
#  * @return Returns size in bytes
#  *
#  * @example size_t argLen = webui_get_size_at(e, 0);
#  */
# WEBUI_EXPORT size_t webui_get_size_at(webui_event_t* e, size_t index);
#
# /**
#  * @brief Get size in bytes of the first argument.
#  *
#  * @param e The event struct
#  *
#  * @return Returns size in bytes
#  *
#  * @example size_t argLen = webui_get_size(e);
#  */
# WEBUI_EXPORT size_t webui_get_size(webui_event_t* e);
#
# /**
#  * @brief Return the response to JavaScript as integer.
#  *
#  * @param e The event struct
#  * @param n The integer to be send to JavaScript
#  *
#  * @example webui_return_int(e, 123);
#  */
# WEBUI_EXPORT void webui_return_int(webui_event_t* e, long long int n);
#
# /**
#  * @brief Return the response to JavaScript as float.
#  *
#  * @param e The event struct
#  * @param f The float number to be send to JavaScript
#  *
#  * @example webui_return_float(e, 123.456);
#  */
# WEBUI_EXPORT void webui_return_float(webui_event_t* e, double f);
#
# /**
#  * @brief Return the response to JavaScript as string.
#  *
#  * @param e The event struct
#  * @param n The string to be send to JavaScript
#  *
#  * @example webui_return_string(e, "Response...");
#  */
# WEBUI_EXPORT void webui_return_string(webui_event_t* e, const char* s);
#
# /**
#  * @brief Return the response to JavaScript as boolean.
#  *
#  * @param e The event struct
#  * @param n The boolean to be send to JavaScript
#  *
#  * @example webui_return_bool(e, true);
#  */
# WEBUI_EXPORT void webui_return_bool(webui_event_t* e, bool b);
#
# // -- Wrapper's Interface -------------
#
# /**
#  * @brief Bind a specific HTML element click event with a function. Empty element means all events.
#  *
#  * @param window The window number
#  * @param element The element ID
#  * @param func The callback as myFunc(Window, EventType, Element, EventNumber, BindID)
#  *
#  * @return Returns unique bind ID
#  *
#  * @example size_t id = webui_interface_bind(myWindow, "myID", myCallback);
#  */
# WEBUI_EXPORT size_t webui_interface_bind(size_t window, const char* element,
#     void (*func)(size_t, size_t, char*, size_t, size_t));
#
# /**
#  * @brief When using `webui_interface_bind()`, you may need this function to easily set a response.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param response The response as string to be send to JavaScript
#  *
#  * @example webui_interface_set_response(myWindow, e->event_number, "Response...");
#  */
# WEBUI_EXPORT void webui_interface_set_response(size_t window, size_t event_number, const char* response);
#
# /**
#  * @brief Check if the app still running.
#  *
#  * @return Returns True if app is running
#  *
#  * @example bool status = webui_interface_is_app_running();
#  */
# WEBUI_EXPORT bool webui_interface_is_app_running(void);
#
# /**
#  * @brief Get a unique window ID.
#  *
#  * @param window The window number
#  *
#  * @return Returns the unique window ID as integer
#  *
#  * @example size_t id = webui_interface_get_window_id(myWindow);
#  */
# WEBUI_EXPORT size_t webui_interface_get_window_id(size_t window);
#
# /**
#  * @brief Get an argument as string at a specific index.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param index The argument position
#  *
#  * @return Returns argument as string
#  *
#  * @example const char* myStr = webui_interface_get_string_at(myWindow, e->event_number, 0);
#  */
# WEBUI_EXPORT const char* webui_interface_get_string_at(size_t window, size_t event_number, size_t index);
#
# /**
#  * @brief Get an argument as integer at a specific index.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param index The argument position
#  *
#  * @return Returns argument as integer
#  *
#  * @example long long int myNum = webui_interface_get_int_at(myWindow, e->event_number, 0);
#  */
# WEBUI_EXPORT long long int webui_interface_get_int_at(size_t window, size_t event_number, size_t index);
#
# /**
#  * @brief Get an argument as float at a specific index.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param index The argument position
#  *
#  * @return Returns argument as float
#  *
#  * @example double myFloat = webui_interface_get_int_at(myWindow, e->event_number, 0);
#  */
# WEBUI_EXPORT double webui_interface_get_float_at(size_t window, size_t event_number, size_t index);
#
# /**
#  * @brief Get an argument as boolean at a specific index.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param index The argument position
#  *
#  * @return Returns argument as boolean
#  *
#  * @example bool myBool = webui_interface_get_bool_at(myWindow, e->event_number, 0);
#  */
# WEBUI_EXPORT bool webui_interface_get_bool_at(size_t window, size_t event_number, size_t index);
#
# /**
#  * @brief Get the size in bytes of an argument at a specific index.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param index The argument position
#  *
#  * @return Returns size in bytes
#  *
#  * @example size_t argLen = webui_interface_get_size_at(myWindow, e->event_number, 0);
#  */
# WEBUI_EXPORT size_t webui_interface_get_size_at(size_t window, size_t event_number, size_t index);
#
# /**
#  * @brief Show a window using embedded HTML, or a file. If the window is already
#  * open, it will be refreshed. Single client.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param content The HTML, URL, Or a local file
#  *
#  * @return Returns True if showing the window is successed.
#  *
#  * @example webui_show_client(e, "<html>...</html>"); |
#  * webui_show_client(e, "index.html"); | webui_show_client(e, "http://...");
#  */
# WEBUI_EXPORT bool webui_interface_show_client(size_t window, size_t event_number, const char* content);
#
# /**
#  * @brief Close a specific client.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  *
#  * @example webui_close_client(e);
#  */
# WEBUI_EXPORT void webui_interface_close_client(size_t window, size_t event_number);
#
# /**
#  * @brief Safely send raw data to the UI. Single client.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param function The JavaScript function to receive raw data: `function
#  * myFunc(myData){}`
#  * @param raw The raw data buffer
#  * @param size The raw data size in bytes
#  *
#  * @example webui_send_raw_client(e, "myJavaScriptFunc", myBuffer, 64);
#  */
# WEBUI_EXPORT void webui_interface_send_raw_client(size_t window, size_t event_number, const char* function, const void* raw, size_t size);
#
# /**
#  * @brief Navigate to a specific URL. Single client.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param url Full HTTP URL
#  *
#  * @example webui_navigate_client(e, "http://domain.com");
#  */
# WEBUI_EXPORT void webui_interface_navigate_client(size_t window, size_t event_number, const char* url);
#
# /**
#  * @brief Run JavaScript without waiting for the response. Single client.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param script The JavaScript to be run
#  *
#  * @example webui_run_client(e, "alert('Hello');");
#  */
# WEBUI_EXPORT void webui_interface_run_client(size_t window, size_t event_number, const char* script);
#
# /**
#  * @brief Run JavaScript and get the response back. Single client.
#  * Make sure your local buffer can hold the response.
#  *
#  * @param window The window number
#  * @param event_number The event number
#  * @param script The JavaScript to be run
#  * @param timeout The execution timeout in seconds
#  * @param buffer The local buffer to hold the response
#  * @param buffer_length The local buffer size
#  *
#  * @return Returns True if there is no execution error
#  *
#  * @example bool err = webui_script_client(e, "return 4 + 6;", 0, myBuffer, myBufferSize);
#  */
# WEBUI_EXPORT bool webui_interface_script_client(size_t window, size_t event_number, const char* script, size_t timeout, char* buffer, size_t buffer_length);
