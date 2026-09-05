"""OS keyring for OpenTimeLogger BYOK secrets (security-auditor).

Windows Credential Locker via ctypes — stdlib only, no third-party wheels.
`ai_config.json` keeps only {key_id, provider, label} refs; secret bytes live
in the Locker under SERVICE/key_id and never touch disk, logs, or git.

Non-Windows platforms: all functions fail closed ({ok: False}) so callers
fall back to an explicit, user-consented path instead of silent plaintext.
"""

import sys

SERVICE = "OpenTimeLogger/ai"

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2


def available():
    """True when a real OS locker backend exists on this platform."""
    return sys.platform == "win32"


def _advapi():
    import ctypes
    return ctypes.WinDLL("advapi32", use_last_error=True)


def _credential_blob(secret):
    data = secret.encode("utf-8")
    import ctypes
    buf = ctypes.create_string_buffer(data)
    return buf, len(data)


def save_key(key_id, secret):
    """Store/overwrite a secret. Returns {ok: True} or {ok, error}."""
    if not available():
        return {"ok": False, "error": "OS keyring unavailable on this platform"}
    if not key_id or not secret:
        return {"ok": False, "error": "key_id and secret are required"}
    try:
        import ctypes
        from ctypes import wintypes
        advapi = _advapi()

        class CREDENTIALW(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        buf, size = _credential_blob(secret)
        cred = CREDENTIALW()
        cred.Flags = 0
        cred.Type = CRED_TYPE_GENERIC
        cred.TargetName = "%s/%s" % (SERVICE, key_id)
        cred.Comment = None
        cred.CredentialBlobSize = size
        cred.CredentialBlob = ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte))
        cred.Persist = CRED_PERSIST_LOCAL_MACHINE
        cred.AttributeCount = 0
        cred.Attributes = None
        cred.TargetAlias = None
        cred.UserName = None

        advapi.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIALW), wintypes.DWORD]
        advapi.CredWriteW.restype = wintypes.BOOL
        ok = advapi.CredWriteW(ctypes.byref(cred), 0)
        # scrub local copies
        ctypes.memset(buf, 0, size)
        if not ok:
            raise OSError("CredWriteW failed, err=%d" % ctypes.get_last_error())
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": "keyring write failed: %s" % e}


def load_key(key_id):
    """Read a secret. Returns {ok: True, secret} or {ok: False, error}."""
    if not available():
        return {"ok": False, "error": "OS keyring unavailable on this platform"}
    if not key_id:
        return {"ok": False, "error": "key_id is required"}
    try:
        import ctypes
        from ctypes import wintypes
        advapi = _advapi()
        advapi.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                     wintypes.DWORD,
                                     ctypes.POINTER(ctypes.c_void_p)]
        advapi.CredReadW.restype = wintypes.BOOL
        advapi.CredFree.argtypes = [ctypes.c_void_p]
        advapi.CredFree.restype = None

        out = ctypes.c_void_p()
        ok = advapi.CredReadW("%s/%s" % (SERVICE, key_id),
                              CRED_TYPE_GENERIC, 0, ctypes.byref(out))
        if not ok:
            return {"ok": False, "error": "key not found in OS keyring"}

        class CREDENTIALW(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", ctypes.c_void_p),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        try:
            cred = ctypes.cast(out, ctypes.POINTER(CREDENTIALW)).contents
            size = int(cred.CredentialBlobSize)
            if not cred.CredentialBlob or size <= 0:
                return {"ok": False, "error": "keyring entry is empty"}
            raw = ctypes.string_at(cred.CredentialBlob, size)
            return {"ok": True, "secret": raw.decode("utf-8")}
        finally:
            advapi.CredFree(out)
    except Exception as e:
        return {"ok": False, "error": "keyring read failed: %s" % e}


def delete_key(key_id):
    """Delete a secret. Missing credentials count as success."""
    if not available():
        return {"ok": False, "error": "OS keyring unavailable on this platform"}
    if not key_id:
        return {"ok": False, "error": "key_id is required"}
    try:
        import ctypes
        from ctypes import wintypes
        advapi = _advapi()
        advapi.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                       wintypes.DWORD]
        advapi.CredDeleteW.restype = wintypes.BOOL
        ok = advapi.CredDeleteW("%s/%s" % (SERVICE, key_id),
                                CRED_TYPE_GENERIC, 0)
        if not ok:
            err = ctypes.get_last_error()
            if err == 1168:  # ERROR_NOT_FOUND — already gone
                return {"ok": True}
            raise OSError("CredDeleteW failed, err=%d" % err)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": "keyring delete failed: %s" % e}
