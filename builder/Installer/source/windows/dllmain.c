#include "launch.h"
#include <windows.h>
#include <olectl.h>

typedef int (__stdcall *__PROC__DllCanUnloadNow) (void);
__PROC__DllCanUnloadNow Pyc_DllCanUnloadNow = NULL;
typedef HRESULT (__stdcall *__PROC__DllGetClassObject) (REFCLSID, REFIID, LPVOID *);
__PROC__DllGetClassObject Pyc_DllGetClassObject = NULL;
typedef int (__cdecl *__PROC__DllRegisterServerEx) (const char *);
__PROC__DllRegisterServerEx Pyc_DllRegisterServerEx = NULL;
typedef int (__cdecl *__PROC__DllUnregisterServerEx) (const char *);
__PROC__DllUnregisterServerEx Pyc_DllUnregisterServerEx = NULL;
typedef void (__cdecl *__PROC__PyCom_CoUninitialize) (void);
__PROC__PyCom_CoUninitialize PyCom_CoUninitialize = NULL;

HINSTANCE gPythoncom = 0;
char here[_MAX_PATH + 1];
int LoadPythonCom(void);
void releasePythonCom(void);
HINSTANCE gInstance;
PyThreadState *thisthread = NULL;

int launch(char const * archivePath, char  const * archiveName)
{
	PyObject *obHandle;
	int loadedNew = 0;
	char pathnm[_MAX_PATH];

    VS("START");
	strcpy(pathnm, archivePath);
	strcat(pathnm, archiveName);
    /* Set up paths */
    if (setPaths(archivePath, archiveName))
        return -1;
	VS("Got Paths");
    /* Open the archive */
    if (openArchive())
        return -1;
	VS("Opened Archive");
    /* Load Python DLL */
    if (attachPython(&loadedNew))
        return -1;

	if (loadedNew) {
		/* Start Python with silly command line */
		PyEval_InitThreads();
		if (startPython(1, (char**)&pathnm))
			return -1;
		VS("Started new Python");
		thisthread = PyThreadState_Swap(NULL);
		PyThreadState_Swap(thisthread);
	}
	else {
		VS("Attached to existing Python");

		/* start a mew interp */
		thisthread = PyThreadState_Swap(NULL);
		PyThreadState_Swap(thisthread);
		if (thisthread == NULL) {
			thisthread = Py_NewInterpreter();
			VS("created thisthread");
		}
		else
			VS("grabbed thisthread");
		PyRun_SimpleString("import sys;sys.argv=[]");
	}

	/* a signal to scripts */
	PyRun_SimpleString("import sys;sys.frozen='dll'\n");
	VS("set sys.frozen");
	/* Create a 'frozendllhandle' as a counterpart to
	   sys.dllhandle (which is the Pythonxx.dll handle)
	*/
	obHandle = Py_BuildValue("i", gInstance);
	PySys_SetObject("frozendllhandle", obHandle);
	Py_XDECREF(obHandle);
    /* Import modules from archive - this is to bootstrap */
    if (importModules())
        return -1;
	VS("Imported Modules");
    /* Install zlibs - now import hooks are in place */
    if (installZlibs())
        return -1;
	VS("Installed Zlibs");
    /* Run scripts */
    if (runScripts())
        return -1;
	VS("All scripts run");
    if (PyErr_Occurred()) {
		// PyErr_Print();
		//PyErr_Clear();
		VS("Some error occurred");
    }
	VS("PGL released");
	// Abandon our thread state.
	PyEval_ReleaseThread(thisthread);
    VS("OK.");
    return 0;
}
void startUp()
{
	char thisfile[_MAX_PATH + 1];
	char *p;
	int len;

	if (!GetModuleFileNameA(gInstance, thisfile, _MAX_PATH)) {
		FATALERROR("System error - unable to load!");
		return;
	}
	// fill in here (directory of thisfile)
	//GetModuleFileName returns an absolute path
	strcpy(here, thisfile);
	for (p=here+strlen(here); *p != '\\' && p >= here+2; --p);
	*++p = '\0';
	len = p - here;
	//VS(here);
	//VS(&thisfile[len]);
	launch(here, &thisfile[len]);
	LoadPythonCom();
	// Now Python is up and running (any scripts have run)
}

BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved)
{
	char msg[40];

	if ( dwReason == DLL_PROCESS_ATTACH) {
		sprintf(msg, "Attach from thread %x", GetCurrentThreadId()); 
		VS(msg);
		gInstance = hInstance;
	}
	else if ( dwReason == DLL_PROCESS_DETACH ) {
		VS("Process Detach");
		//if (gPythoncom)
		//	releasePythonCom();
		//finalizePython();
	}

	return TRUE; 
}

int LoadPythonCom()
{
	char dllpath[_MAX_PATH+1];
	VS("Loading Pythoncom");
	// see if pythoncom is already loaded
	sprintf(dllpath, "pythoncom%02d.dll", getPyVersion());
	gPythoncom = GetModuleHandle(dllpath);
	if (gPythoncom == NULL) {
		sprintf(dllpath, "%spythoncom%02d.dll", here, getPyVersion());
		//VS(dllpath);
		gPythoncom = LoadLibraryEx( dllpath, // points to name of executable module 
					   NULL, // HANDLE hFile, // reserved, must be NULL 
					   LOAD_WITH_ALTERED_SEARCH_PATH // DWORD dwFlags // entry-point execution flag 
					  ); 
	}
	if (!gPythoncom) {
		VS("Pythoncom failed to load");
		return -1;
	}
	// debugging
	GetModuleFileNameA(gPythoncom, dllpath, _MAX_PATH);
	VS(dllpath);

	Pyc_DllCanUnloadNow = (__PROC__DllCanUnloadNow)GetProcAddress(gPythoncom, "DllCanUnloadNow");
	Pyc_DllGetClassObject = (__PROC__DllGetClassObject)GetProcAddress(gPythoncom, "DllGetClassObject");
	// DllRegisterServerEx etc are mainly used for "scripts", so that regsvr32.exe can be run on
	// a .py file, for example.  They aren't really relevant here.
	Pyc_DllRegisterServerEx = (__PROC__DllRegisterServerEx)GetProcAddress(gPythoncom, "DllRegisterServerEx");
	Pyc_DllUnregisterServerEx = (__PROC__DllUnregisterServerEx)GetProcAddress(gPythoncom, "DllUnregisterServerEx");
	PyCom_CoUninitialize = (__PROC__PyCom_CoUninitialize)GetProcAddress(gPythoncom, "PyCom_CoUninitialize");
	if (Pyc_DllGetClassObject == NULL) {
		VS("Couldn't get DllGetClassObject from pythoncom!");
		return -1;
	}
	if (PyCom_CoUninitialize == NULL) {
		VS("Couldn't get PyCom_CoUninitialize from pythoncom!");
		return -1;
	}
	return 0;
}
void releasePythonCom(void)
{
	if (gPythoncom) {
		PyCom_CoUninitialize();
		FreeLibrary(gPythoncom);
		gPythoncom = 0;
	}
}
//__declspec(dllexport) int __stdcall DllCanUnloadNow(void)
//__declspec(dllexport)
//STDAPI
HRESULT __stdcall DllCanUnloadNow(void)
{
	char msg[80];
	HRESULT rc;

	sprintf(msg, "DllCanUnloadNow from thread %x", GetCurrentThreadId()); 
	VS(msg);
	if (gPythoncom == 0)
		startUp();
	rc = Pyc_DllCanUnloadNow();
	sprintf(msg, "DllCanUnloadNow returns %x", rc); 
	VS(msg);
	//if (rc == S_OK)
	//	PyCom_CoUninitialize();
	return rc;
}

//__declspec(dllexport) int __stdcall DllGetClassObject(void *rclsid, void *riid, void *ppv)
HRESULT __stdcall DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv)
{
	char msg[80];
	HRESULT rc;
	sprintf(msg, "DllGetClassObject from thread %x", GetCurrentThreadId()); 
	VS(msg);
	if (gPythoncom == 0)
		startUp();
	rc = Pyc_DllGetClassObject(rclsid, riid, ppv);
	sprintf(msg, "DllGetClassObject set %x and returned %x", *ppv, rc);
	VS(msg);
	return rc;
}

__declspec(dllexport) int DllRegisterServerEx(LPCSTR fileName)
{
	char msg[40];
	sprintf(msg, "DllRegisterServerEx from thread %x", GetCurrentThreadId()); 
	VS(msg);
	if (gPythoncom == 0)
		startUp();
	return Pyc_DllRegisterServerEx(fileName);
}

__declspec(dllexport) int DllUnregisterServerEx(LPCSTR fileName)
{
	if (gPythoncom == 0)
		startUp();
	return Pyc_DllUnregisterServerEx(fileName);
}

STDAPI DllRegisterServer()
{
	int rc, pyrc;
	if (gPythoncom == 0)
		startUp();
	PyEval_AcquireThread(thisthread);
	rc = callSimpleEntryPoint("DllRegisterServer", &pyrc);
	PyEval_ReleaseThread(thisthread);
	return rc==0 ? pyrc : SELFREG_E_CLASS;
}

STDAPI DllUnregisterServer()
{
	int rc, pyrc;
	if (gPythoncom == 0)
		startUp();
	PyEval_AcquireThread(thisthread);
	rc = callSimpleEntryPoint("DllUnregisterServer", &pyrc);
	PyEval_ReleaseThread(thisthread);
	return rc==0 ? pyrc : SELFREG_E_CLASS;
}
