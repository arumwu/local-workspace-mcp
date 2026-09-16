/* Named macOS background entry point; no shell interpreter or embedded secrets. */
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 3 || argc > 4) {
        fprintf(stderr, "Launch through the configured ChatGPT login service.\n");
        return 64;
    }
    if (access(argv[1], X_OK) || access(argv[2], R_OK)) return 66;
    setenv("PATH", "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin", 1);
    setenv("PYTHONDONTWRITEBYTECODE", "1", 1);
    if (argc == 4) {
        pid_t pid = fork();
        if (pid < 0) return 71;
        if (pid == 0) { execl(argv[3], argv[3], (char *)NULL); _exit(72); }
        int status;
        if (waitpid(pid, &status, 0) < 0 || !WIFEXITED(status) || WEXITSTATUS(status)) return 73;
    }
    char *args[] = {argv[1], "run", "--config", argv[2], NULL};
    execv(args[0], args);
    perror("Cannot start ChatGPT tunnel");
    return 74;
}
