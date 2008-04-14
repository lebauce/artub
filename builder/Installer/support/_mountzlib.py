import archive, iu, sys
import time
iu._globalownertypes.insert(0, archive.PYZOwner)
sys.importManager = iu.ImportManager()
sys.importManager.install()
if not hasattr(sys, 'frozen'):
    sys.frozen = 1
