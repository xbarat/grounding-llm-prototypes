# Configuration Protection and Crisis Management

## Protected Configuration Files

The following configuration files are protected to prevent accidental changes that could break the development environment:

1. `.gitignore`
   - Purpose: Controls which files are ignored by Git
   - Critical for: Preventing sensitive or generated files from being committed
   - Impact if corrupted: Could lead to committing node_modules, build files, or sensitive data

2. `.eslintrc.json`
   - Purpose: Defines code quality rules and TypeScript/JavaScript linting configuration
   - Critical for: Maintaining code quality and preventing build errors
   - Impact if corrupted: Build failures, TypeScript errors, code quality issues

3. `next.config.mjs`
   - Purpose: Next.js framework configuration
   - Critical for: Build process, routing, and framework features
   - Impact if corrupted: Build failures, routing issues, missing features

4. `tsconfig.json`
   - Purpose: TypeScript compiler configuration
   - Critical for: Type checking, module resolution, and compilation settings
   - Impact if corrupted: Type checking failures, import/export issues, build errors

5. `package.json`
   - Purpose: Project dependencies and scripts definition
   - Critical for: Package management and project scripts
   - Impact if corrupted: Dependency issues, missing packages, broken scripts

6. `postcss.config.mjs`
   - Purpose: CSS processing configuration
   - Critical for: Styling and CSS transformations
   - Impact if corrupted: Styling issues, CSS processing failures

## Protection Mechanism

These files are protected using Git's `assume-unchanged` flag and backup copies. A management script `frontend2/manage-config.sh` is provided to handle these protections.

### Using the Management Script

```bash
./manage-config.sh [command]

Commands:
  lock      - Lock all configuration files
  unlock    - Unlock all configuration files
  backup    - Create backups of all configuration files
  restore   - Restore all configuration files from backups
  status    - Show lock status of all configuration files
  help      - Show this help message
```

## Crisis Management

If you encounter issues with the development environment:

1. **Build Failures**
   - First check if any configuration files were modified
   - Run `./manage-config.sh status` to check file states
   - If needed, restore from backups: `./manage-config.sh restore`

2. **Styling Issues**
   - Check `postcss.config.mjs` and ensure it's not corrupted
   - Verify `.gitignore` is properly ignoring generated files
   - Rebuild node_modules if necessary:
     ```bash
     rm -rf node_modules
     rm -rf .next
     npm install
     ```

3. **TypeScript/ESLint Errors**
   - Verify `.eslintrc.json` and `tsconfig.json` are intact
   - Restore from backups if necessary
   - If errors persist, try rebuilding with ESLint disabled:
     ```bash
     DISABLE_ESLINT_PLUGIN=true npm run build
     ```

4. **Dependency Issues**
   - Check if `package.json` was modified
   - Restore from backup if necessary
   - Clear npm cache and reinstall:
     ```bash
     npm cache clean --force
     rm -rf node_modules
     rm -rf .next
     npm install
     ```

## Prevention Best Practices

1. **Always Use the Management Script**
   - Lock files when not actively changing them
   - Create new backups after intentional changes
   - Check status regularly

2. **Before Making Changes**
   - Create new backups: `./manage-config.sh backup`
   - Unlock specific files: `./manage-config.sh unlock`
   - Make your changes
   - Lock files again: `./manage-config.sh lock`

3. **Version Control**
   - Keep backup files in a separate branch
   - Document any intentional configuration changes
   - Test changes in a development environment first

## Recovery Steps

If all local fixes fail:

1. Restore from backups:
   ```bash
   ./manage-config.sh restore
   ```

2. If backups are corrupted:
   - Check out the files from the last known good commit
   - Rebuild the development environment from scratch

3. If problems persist:
   - Clone the repository fresh
   - Copy over only the necessary files from your working directory
   - Rebuild the development environment 