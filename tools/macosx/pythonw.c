/*
 * This wrapper program executes a python executable hidden inside an
 * application bundle inside the Python framework. This is needed to run
 * GUI code: some GUI API's don't work unless the program is inside an
 * application bundle.
 */
#include <unistd.h>
#include <err.h>
#include <sys/param.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
     
static char Python[PATH_MAX];

int main(int argc, char **argv) {
	char *rpath;
	
	realpath(argv[0], Python);
	rpath = dirname(Python);
	strcpy(Python, rpath);
	strcat(Python, "/../Resources/Python.app/Contents/MacOS/Python");
	printf("Path : %s\n", Python);
	argv[0] = Python;
	execv(Python, argv);
	err(1, "execv: %s", Python);
	/* NOTREACHED */
}
