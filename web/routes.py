import time
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, current_app

bp = Blueprint("main", __name__)


def _sm():
    return current_app.config["sync_manager"]


def _cm():
    return current_app.config["config_manager"]


def _ingress_redirect(endpoint, **kwargs):
    """Redirect with ingress path prefix."""
    ingress_path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    path = url_for(endpoint, **kwargs)
    return redirect(ingress_path + path)


@bp.route("/")
def dashboard():
    status = _sm().get_status_dict()
    collections = _cm().get_collections()
    return render_template("dashboard.html", status=status, collections=collections)


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    cm = _cm()
    if request.method == "POST":
        settings_dict = {}
        for key in request.form:
            settings_dict[key] = request.form[key]

        # Handle checkboxes (unchecked = missing from form)
        checkbox_fields = [
            "download_manually_added_lists",
            "download_my_mdblist_lists_automatically",
            "use_mdblist_collection_description",
            "update_collection_sort_name",
            "update_items_sort_names_default_value",
            "refresh_items_in_collections",
        ]
        for field in checkbox_fields:
            if field not in settings_dict:
                settings_dict[field] = "False"
            else:
                settings_dict[field] = "True"

        cm.update_admin_settings(settings_dict)
        flash("Settings saved successfully.", "success")
        return _ingress_redirect("main.settings")

    admin = cm.get_admin_settings()
    return render_template("settings.html", admin=admin)


@bp.route("/collections")
def collections_list():
    collections = _cm().get_collections()
    return render_template("collections.html", collections=collections)


@bp.route("/collections/add", methods=["GET", "POST"])
def collection_add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Collection name is required.", "error")
            return _ingress_redirect("main.collection_add")

        settings = {
            "source": request.form.get("source", ""),
            "frequency": request.form.get("frequency", "100"),
            "poster": request.form.get("poster", ""),
            "description": request.form.get("description", ""),
            "active_between": request.form.get("active_between", ""),
            "collection_sort_name": request.form.get("collection_sort_name", ""),
        }
        update_sort = request.form.get("update_items_sort_names")
        settings["update_items_sort_names"] = "True" if update_sort else "False"

        # Remove empty values
        settings = {k: v for k, v in settings.items() if v}

        if _cm().add_collection(name, settings):
            flash(f"Collection '{name}' added.", "success")
        else:
            flash(f"Collection '{name}' already exists.", "error")
        return _ingress_redirect("main.collections_list")

    return render_template("collection_edit.html", collection=None, is_new=True)


@bp.route("/collections/<path:name>/edit", methods=["GET", "POST"])
def collection_edit(name):
    cm = _cm()
    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if not new_name:
            new_name = name

        settings = {
            "source": request.form.get("source", ""),
            "frequency": request.form.get("frequency", "100"),
            "poster": request.form.get("poster", ""),
            "description": request.form.get("description", ""),
            "active_between": request.form.get("active_between", ""),
            "collection_sort_name": request.form.get("collection_sort_name", ""),
        }
        update_sort = request.form.get("update_items_sort_names")
        settings["update_items_sort_names"] = "True" if update_sort else "False"

        cm.update_collection(name, new_name, settings)
        flash(f"Collection '{new_name}' updated.", "success")
        return _ingress_redirect("main.collections_list")

    collection = cm.get_collection(name)
    if collection is None:
        flash(f"Collection '{name}' not found.", "error")
        return _ingress_redirect("main.collections_list")
    return render_template("collection_edit.html", collection=collection, is_new=False)


@bp.route("/collections/<path:name>/delete", methods=["POST"])
def collection_delete(name):
    if _cm().remove_collection(name):
        flash(f"Collection '{name}' removed.", "success")
    else:
        flash(f"Collection '{name}' not found.", "error")
    return _ingress_redirect("main.collections_list")


@bp.route("/logs")
def logs():
    return render_template("logs.html")


@bp.route("/api/logs")
def api_logs():
    count = request.args.get("count", 200, type=int)
    lines = _sm().get_logs(count)
    return jsonify({"logs": lines})


@bp.route("/api/sync", methods=["POST"])
def api_sync():
    sm = _sm()
    if sm.status == "syncing":
        return jsonify({"ok": False, "message": "Sync already in progress"})
    sm.trigger_force_sync()
    return jsonify({"ok": True, "message": "Sync triggered"})


@bp.route("/api/status")
def api_status():
    status = _sm().get_status_dict()
    return jsonify(status)


def _format_time(ts):
    if ts is None:
        return "Never"
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


@bp.app_template_filter("format_time")
def format_time_filter(ts):
    return _format_time(ts)


@bp.app_template_filter("time_until")
def time_until_filter(ts):
    if ts is None:
        return "N/A"
    diff = ts - time.time()
    if diff <= 0:
        return "Now"
    hours = int(diff // 3600)
    minutes = int((diff % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
