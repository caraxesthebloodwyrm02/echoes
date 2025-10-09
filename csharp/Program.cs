using System;
using System.IO;
using System.Net.Http;
using System.Diagnostics;

class Program
{
    // Exit codes: 0 = success, 1 = java failed, 2 = java not found, 3 = http probe failed
    static int Main(string[] args)
    {
        // Java probe: search upward for bin/java.exe
        var dir = new DirectoryInfo(Directory.GetCurrentDirectory());
        FileInfo javaExe = null;
        while (dir != null)
        {
            var candidate = Path.Combine(dir.FullName, "bin", "java.exe");
            if (File.Exists(candidate)) { javaExe = new FileInfo(candidate); break; }
            dir = dir.Parent;
        }

        if (javaExe == null)
        {
            Console.Error.WriteLine("Java not found");
            return 2;
        }

        // Allow CI to signal that a placeholder java.exe is present; skip executing it.
        var allowFakeJava = Environment.GetEnvironmentVariable("ALLOW_FAKE_JAVA");
        if (!string.Equals(allowFakeJava, "1", StringComparison.Ordinal))
        {
            try
            {
                var p = new Process();
                p.StartInfo.FileName = javaExe.FullName;
                p.StartInfo.Arguments = "-version";
                p.StartInfo.RedirectStandardOutput = true;
                p.StartInfo.RedirectStandardError = true;
                p.StartInfo.UseShellExecute = false;
                p.Start();
                p.WaitForExit(5000);
                if (p.ExitCode != 0) { return 1; }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Java execution failed: " + ex.Message);
                return 1;
            }
        }

        // Optional HTTP probe (run after Java detection so CI can assert exit=2 when Java missing)
        // Skip if CI sets SKIP_HTTP_PROBE=1
        var skipHttp = Environment.GetEnvironmentVariable("SKIP_HTTP_PROBE");
        if (!string.Equals(skipHttp, "1", StringComparison.Ordinal))
        {
            try
            {
                using (var client = new HttpClient())
                {
                    var resp = client.GetAsync("http://127.0.0.1:8000/").Result;
                    if (!resp.IsSuccessStatusCode)
                    {
                        Console.Error.WriteLine("HTTP probe failed: " + resp.StatusCode);
                        return 3;
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("HTTP probe exception: " + ex.Message);
                return 3;
            }
        }

        Console.WriteLine("Runner completed successfully");
        return 0;
    }
}
