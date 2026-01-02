import json
import os
from datetime import datetime
from typing import Dict, Any

class Storage:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.warns_file = os.path.join(base_dir, "warns.json")
        self.bans_file = os.path.join(base_dir, "bans.json")
        self.mutes_file = os.path.join(base_dir, "mutes.json")
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files if they don't exist"""
        for file in [self.warns_file, self.bans_file, self.mutes_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)
    
    def _read_file(self, file_path: str) -> Dict:
        """Read data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_file(self, file_path: str, data: Dict):
        """Write data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # --- WARNS ---
    def get_warns(self, chat_id: int, user_id: int) -> int:
        """Get warn count for a user"""
        data = self._read_file(self.warns_file)
        return int(data.get(str(chat_id), {}).get(str(user_id), 0))
    
    def add_warn(self, chat_id: int, user_id: int):
        """Increment warn count"""
        data = self._read_file(self.warns_file)
        if str(chat_id) not in data:
            data[str(chat_id)] = {}
        data[str(chat_id)][str(user_id)] = self.get_warns(chat_id, user_id) + 1
        self._write_file(self.warns_file, data)
    
    def reset_warns(self, chat_id: int, user_id: int):
        """Reset warn count to 0"""
        data = self._read_file(self.warns_file)
        if str(chat_id) in data and str(user_id) in data[str(chat_id)]:
            data[str(chat_id)][str(user_id)] = 0
            self._write_file(self.warns_file, data)
    
    # --- BANS ---
    def add_ban(self, chat_id: int, user_id: int, user_name: str):
        """Record a ban"""
        data = self._read_file(self.bans_file)
        if str(chat_id) not in data:
            data[str(chat_id)] = {}
        data[str(chat_id)][str(user_id)] = {
            "name": user_name,
            "banned_at": datetime.now().isoformat()
        }
        self._write_file(self.bans_file, data)
    
    def remove_ban(self, chat_id: int, user_id: int):
        """Remove a ban record"""
        data = self._read_file(self.bans_file)
        if str(chat_id) in data and str(user_id) in data[str(chat_id)]:
            del data[str(chat_id)][str(user_id)]
            self._write_file(self.bans_file, data)
    
    # --- MUTES ---
    def add_mute(self, chat_id: int, user_id: int, user_name: str, until_date: str):
        """Record a mute"""
        data = self._read_file(self.mutes_file)
        if str(chat_id) not in data:
            data[str(chat_id)] = {}
        data[str(chat_id)][str(user_id)] = {
            "name": user_name,
            "muted_at": datetime.now().isoformat(),
            "until": until_date
        }
        self._write_file(self.mutes_file, data)
    
    def remove_mute(self, chat_id: int, user_id: int):
        """Remove a mute record"""
        data = self._read_file(self.mutes_file)
        if str(chat_id) in data and str(user_id) in data[str(chat_id)]:
            del data[str(chat_id)][str(user_id)]
            self._write_file(self.mutes_file, data)
