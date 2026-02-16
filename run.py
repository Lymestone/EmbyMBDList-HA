import os
import shutil
import threading


def main():
    config_path = os.environ.get("CONFIG_PATH", "config.cfg")

    # Copy default config if none exists at target path
    if not os.path.exists(config_path) and config_path != "config.cfg":
        config_dir = os.path.dirname(config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        if os.path.exists("config.cfg"):
            shutil.copy("config.cfg", config_path)
            print(f"Copied default config to {config_path}")

    from web.sync_manager import SyncManager
    from web.config_manager import ConfigManager
    from web import create_app

    sync_mgr = SyncManager(config_path=config_path)
    config_mgr = ConfigManager(config_path, sync_mgr.config_lock)

    sync_thread = threading.Thread(target=sync_mgr.sync_loop, daemon=True)
    sync_thread.start()

    app = create_app(sync_mgr, config_mgr)
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting web UI on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
