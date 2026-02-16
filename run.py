import os
import shutil
import threading


def _create_default_config(config_path):
    """Create a default config at config_path from available templates."""
    config_dir = os.path.dirname(config_path)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)

    # Try config.cfg first (present in standalone Docker), then config.cfg.example (git repo)
    for template in ["config.cfg", "config.cfg.example"]:
        if os.path.exists(template):
            shutil.copy(template, config_path)
            print(f"Created initial config from {template} at {config_path}")
            return

    # No template found — create a minimal config so the WebUI can start
    with open(config_path, "w") as f:
        f.write("[admin]\n")
        f.write("emby_server_url = http://your-emby-server:8096\n")
        f.write("emby_user_id = your_emby_user_id\n")
        f.write("emby_api_key = your_emby_api_key\n")
        f.write("mdblist_api_key = your_mdblist_api_key\n")
        f.write("download_manually_added_lists = True\n")
        f.write("download_my_mdblist_lists_automatically = True\n")
        f.write("use_mdblist_collection_description = True\n")
        f.write("update_collection_sort_name = True\n")
        f.write("hours_between_refresh = 6\n")
        f.write("update_items_sort_names_default_value = False\n")
        f.write("refresh_items_in_collections = True\n")
        f.write("refresh_items_in_collections_max_days_since_added = 10\n")
        f.write("refresh_items_in_collections_max_days_since_premiered = 30\n")
    print(f"Created minimal default config at {config_path}")
    print("Please configure your API keys via the Settings page.")


def main():
    config_path = os.environ.get("CONFIG_PATH", "config.cfg")

    # Create config if it doesn't exist
    if not os.path.exists(config_path):
        _create_default_config(config_path)

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
