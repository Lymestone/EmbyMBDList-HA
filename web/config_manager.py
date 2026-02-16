import configparser


class ConfigManager:
    def __init__(self, config_path, lock):
        self.config_path = config_path
        self.lock = lock

    def _read(self):
        cp = configparser.ConfigParser()
        cp.optionxform = str.lower
        cp.read(self.config_path, encoding="utf-8")
        return cp

    def _write(self, cp):
        with open(self.config_path, "w", encoding="utf-8") as f:
            cp.write(f)

    def get_admin_settings(self):
        with self.lock:
            cp = self._read()
            return dict(cp.items("admin"))

    def update_admin_settings(self, settings_dict):
        with self.lock:
            cp = self._read()
            for key, value in settings_dict.items():
                cp.set("admin", key, str(value))
            self._write(cp)

    def get_collections(self):
        with self.lock:
            cp = self._read()
            result = []
            for section in cp.sections():
                if section == "admin":
                    continue
                result.append({"name": section, **dict(cp.items(section))})
            return result

    def get_collection(self, name):
        with self.lock:
            cp = self._read()
            if not cp.has_section(name):
                return None
            return {"name": name, **dict(cp.items(name))}

    def add_collection(self, name, settings):
        with self.lock:
            cp = self._read()
            if cp.has_section(name):
                return False
            cp.add_section(name)
            for key, value in settings.items():
                if value:
                    cp.set(name, key, str(value))
            self._write(cp)
            return True

    def remove_collection(self, name):
        with self.lock:
            cp = self._read()
            if not cp.has_section(name):
                return False
            cp.remove_section(name)
            self._write(cp)
            return True

    def update_collection(self, old_name, new_name, settings):
        with self.lock:
            cp = self._read()
            if cp.has_section(old_name):
                cp.remove_section(old_name)
            if not cp.has_section(new_name):
                cp.add_section(new_name)
            for key, value in settings.items():
                if value:
                    cp.set(new_name, key, str(value))
                elif cp.has_option(new_name, key):
                    cp.remove_option(new_name, key)
            self._write(cp)
