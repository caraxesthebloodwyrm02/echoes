# Solution Quick Reference Guide

## Build Configurations

| Configuration | Purpose | When to Use |
|--------------|---------|-------------|
| `Debug` | Development with full symbols | Local development and debugging |
| `Development` | Development environment | Integration testing, feature validation |
| `Staging` | Pre-production testing | UAT, performance testing |
| `Release` | Production deployment | Production releases |

## Key Files and Locations

### Core Files
- `Development.sln` - Main solution file
- `.github/workflows/solution-analysis.yml` - CI/CD pipeline configuration
- `docs/solution_analysis/` - Solution documentation
- `scripts/validate-builds.ps1` - Build validation script

### Project Structure
```
Solution 'Development'
├── Core/
│   └── Language/
│       └── language-bundle.csproj
```

## Common Tasks

### Adding New Projects
1. Create project in appropriate directory
2. Add to solution: `dotnet sln add <project-path>`
3. Move to correct solution folder
4. Add all build configurations
5. Verify in solution analysis workflow

### Build Configuration Updates
1. Edit project file to add new configuration
2. Update solution configurations
3. Run `scripts/validate-builds.ps1`
4. Update CI/CD workflow if needed

### Troubleshooting Build Issues
1. Check solution analysis workflow output
2. Verify project references
3. Validate configuration names match exactly
4. Review build logs in CI/CD pipeline

## CI/CD Pipeline

### What's Validated
- Solution format version
- Project references
- Build configurations
- Project structure

### Common Pipeline Tasks
- Push to `main`: Triggers full validation
- Pull Request: Validates solution changes
- Manual run: Available through GitHub Actions UI

## Architecture Reviews

### Monthly Review Checklist
1. Solution structure alignment with architecture
2. Build configuration consistency
3. Project reference health
4. Documentation accuracy
5. CI/CD pipeline performance

### Health Metrics
- Build success rate
- Solution load time
- Reference validation status
- Configuration consistency

## Quick Commands

```powershell
# Validate all builds
./scripts/validate-builds.ps1

# Add new project
dotnet sln add path/to/project.csproj

# Create new configuration
dotnet build -c NewConfig

# Run solution analysis locally
git checkout -b test/solution-validation
# make changes
git commit -m "test: solution validation"
git push origin test/solution-validation
```

## Contact and Support

- Architecture Team: [architecture@echoes.internal](mailto:architecture@echoes.internal)
- DevOps Support: [devops@echoes.internal](mailto:devops@echoes.internal)
- Documentation: [docs/solution_analysis/best_practices.md](docs/solution_analysis/best_practices.md)
