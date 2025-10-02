# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by emailing security@example.com.

- **DO NOT** create a public GitHub issue for security vulnerabilities
- You should receive a response within 48 hours
- If the issue is confirmed, we will release a patch as soon as possible

## Security Best Practices

- Always run the framework with the least privileges necessary
- Regularly update dependencies to their latest secure versions
- Use the `--dry-run` flag when testing new tasks
- Review task configurations before execution
- Use environment variables for sensitive information instead of hardcoding values
