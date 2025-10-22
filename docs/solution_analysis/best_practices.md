# Solution Structure Guidelines

## Overview
This document outlines the structure and organization of the Visual Studio solution for the Echoes project.

## Solution Format
- Visual Studio 2022 (Version 17.8.0)
- Solution Format Version: 12.00
- Minimum VS Version: 10.0.40219.1

## Solution Organization
The solution is organized into logical folders to improve maintainability and navigation:

- **Core/** - Core functionality and shared components
  - **Language/** - Language processing and related components
    - `language-bundle` - Main language processing library

## Build Configurations
The solution supports four build configurations:
1. **Debug** - For development with debugging information
2. **Development** - For development environment deployment
3. **Staging** - For pre-production testing
4. **Release** - For production deployment

## Best Practices
1. **Project References**
   - Always use project references instead of file references
   - Ensure referenced projects exist in the solution
   - Remove unused project references

2. **Solution Folders**
   - Group related projects in solution folders
   - Use meaningful folder names
   - Maintain a shallow folder hierarchy

3. **Build Configurations**
   - Use appropriate configuration for each environment
   - Maintain consistent configuration across all projects
   - Test all configurations before deployment

## CI/CD Integration
The solution includes automated analysis in the CI/CD pipeline:
- Validates solution format version
- Checks for missing project references
- Verifies required build configurations
- Runs on push to main branch and pull requests
- Located in `.github/workflows/solution-analysis.yml`

## Adding New Projects
When adding new projects:
1. Create project in appropriate solution folder
2. Add all required build configurations
3. Update solution analysis workflow if needed
4. Document any special configuration requirements

## Troubleshooting
Common issues and solutions:
1. Missing Project References
   - Check project GUID in .csproj file
   - Verify project path is correct
   - Remove reference if project no longer exists

2. Build Configuration Issues
   - Ensure all projects have matching configurations
   - Check platform target settings
   - Verify configuration names match exactly
