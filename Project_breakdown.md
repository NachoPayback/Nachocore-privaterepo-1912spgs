# Nachocore Project Documentation (Beta Branch)

This document describes the complete structure, file purposes, module responsibilities, and key workflows of the Nachocore project. It is intended to be a permanent, self-contained reference for future developers or AI models (with no prior memory) that need to navigate, optimize, or extend this project. All references below point to the **beta** branch.

**Permanent Beta Branch Reference:**  
[Nachocore Beta Branch](https://github.com/NachoPayback/Nachocore-privaterepo-1912spgs/tree/beta)

---

## Repository Overview

Nachocore is a game builder application that enables users to:
- **Build and Manage Tasks:** Create, edit, and arrange tasks (e.g., multiple-choice, short answer, location collection) which form the core challenges in the game.
- **Display Gift Card Progress:** As tasks are completed, a gift card code is revealed gradually. The gift card information is managed through configuration and “burned in” into the final executable.
- **Configure Security Settings:** Toggle features like UI keyboard, mouse locker, sleep blocker, and security monitoring.
- **Export a Self-Contained Executable:** Use PyInstaller to build a standalone game executable that bundles all tasks, configurations, and static manifests. The export process generates a detailed report and cleans up temporary files.

---

## File Structure

```
Nachocore-privaterepo-1912spgs/ (Project Root)
│
├── builder/
│   ├── builder.py                
│   │   - Main Builder UI with tabs for:
│   │     • Task Builder (managing tasks stored in builder/tasks/tasks.json)
│   │     • Gift Card Selection (choosing/updating gift card details)
│   │     • Export Options (configuring export settings and triggering export)
│   │     • Developer Zone (toggling security and beta features)
│   │   - Loads the global stylesheet from shared/theme/styles.qss.
│   ├── export.py                 
│   │   - Manages the export process:
│   │     • Updates config.json with current security and gift card settings.
│   │     • Calls generate_manifest.py to create builder/static_manifest.py.
│   │     • Uses PyInstaller (with UPX and strip flags) to build the final EXE.
│   │     • Cleans up build artifacts and displays a detailed export report.
│   ├── dev_zone.py               
│   │   - Developer Zone UI for configuring security/beta features.
│   ├── gift_card.py              
│   │   - Handles gift card selection, random code/PIN generation, and configuration updates.
│   │   - In frozen mode, loads gift card data from builder/static_manifest.py.
│   ├── task_builder.py           
│   │   - Manages task creation, editing, and saving (to builder/tasks/tasks.json).
│   ├── cleanup.py                
│   │   - Utility module with functions like clean_pycache() to remove temporary files.
│   ├── static_manifest.py        
│   │   - **Auto-generated file** (by generate_manifest.py).
│   │   - Contains:
│   │       • TASK_MANIFEST: Mapping of task types to module import paths.
│   │       • GIFT_CARD_STATIC: Current gift card data (burned into the EXE).
│   │       • SECURITY_SETTINGS_STATIC: Current security settings.
│   ├── config.json               
│   │   - Main configuration file storing selected gift card, security settings, etc.
│   └── data/
│       └── gift_cards/           
│           - Contains JSON files defining various gift card options.
│
├── game/
│   └── game.py                   
│       - Main game executable script.
│       - Loads tasks, security settings, and gift card data.
│       - Manages game progression and displays the gift card progress.
│
├── shared/
│   ├── tasks/                    
│   │   - Contains individual task modules (each defines a TASK_TYPE and a Task class).
│   ├── theme/
│   │   └── styles.qss            
│   │       - Global stylesheet for the project.
│   └── utils/                    
│       - Contains utility modules:
│           • data_helpers.py       - Provides get_data_path() and related functions.
│           • close_button_blocker.py
│           • keyboard_blocker.py
│           • mouse_locker.py
│           • sleep_blocker.py
│           • security_monitor.py
│           • logger.py
│           • ui_keyboard.py
│
└── generate_manifest.py          
    - Build-step script that reads config.json and scans shared/tasks to generate/update builder/static_manifest.py.
```

---

## Module and File Purposes

### builder/
- **builder.py:**  
  The central interface for building and exporting the game. It contains tabs for:
  - **Task Builder:** For creating, editing, and arranging tasks.
  - **Gift Card Selection:** For choosing or customizing the gift card used in the game’s progress bar.
  - **Export Options:** For configuring export parameters (e.g., security mode) and triggering the export process.
  - **Developer Zone:** For accessing advanced/beta features and toggling security settings.
  Loads a global stylesheet from `shared/theme/styles.qss`.

- **export.py:**  
  Manages the process of exporting the game as a standalone EXE. It:
  - Updates configuration (from the UI) into `config.json`.
  - Calls the static manifest generator (via `generate_manifest.py`) to update `builder/static_manifest.py` with the current task mappings, gift card data, and security settings.
  - Builds the EXE using PyInstaller (with flags such as `--strip` and `--upx-dir` for compression).
  - Cleans up build artifacts (build, dist, spec files).
  - Displays a detailed export report dialog that summarizes:
    - Imported task types (from TASK_MANIFEST)
    - Burned-in gift card data (from GIFT_CARD_STATIC)
    - Security settings (from SECURITY_SETTINGS_STATIC)
    - A summary of tasks from `builder/tasks/tasks.json`

- **dev_zone.py:**  
  Provides the Developer Zone UI, allowing toggling of security and beta features. Changes here update the configuration in `config.json`.

- **gift_card.py:**  
  Manages gift card functionality. It:
  - Loads gift card definitions from JSON files in `builder/data/gift_cards`.
  - Generates random codes/PINs if needed.
  - Updates the configuration with the selected gift card.
  - In a frozen EXE, returns gift card data from `builder/static_manifest.py`.

- **task_builder.py:**  
  Handles task creation, editing, and saving of task data to `builder/tasks/tasks.json`.

- **cleanup.py:**  
  Contains utility functions (e.g., `clean_pycache()`) to remove temporary files like __pycache__ folders.

- **static_manifest.py:**  
  An auto-generated file (by `generate_manifest.py`) that “burns in” the current state. It contains:
  - `TASK_MANIFEST`: A mapping of normalized task types to their module paths.
  - `GIFT_CARD_STATIC`: The current gift card details.
  - `SECURITY_SETTINGS_STATIC`: The current security settings.

- **config.json:**  
  The main configuration file that stores the selected gift card, security settings, and other global options.

- **data/gift_cards/**  
  Contains JSON files for each gift card option.

### game/
- **game.py:**  
  The main executable script for the game. It:
  - Loads tasks from `builder/tasks/tasks.json`.
  - Dynamically loads task modules from `shared/tasks/`.
  - Loads security settings (using a frozen-friendly method).
  - Loads gift card data using `load_gift_card_from_config()` (which, in frozen mode, reads from `static_manifest.py`).
  - Manages game progression and reveals the gift card code as tasks are completed.

### shared/
- **tasks/**  
  Contains individual task modules. Each module defines a `TASK_TYPE` and a corresponding Task class that provides UI components and logic.
- **theme/styles.qss:**  
  The global stylesheet used across both the builder and the game.
- **utils/**  
  Contains various utility modules (e.g., `data_helpers.py`, `logger.py`, `ui_keyboard.py`, etc.) that support the overall functionality of the project.

### generate_manifest.py
- A build-step script that:
  - Scans `shared/tasks` for task modules.
  - Reads the current configuration from `builder/config.json`.
  - Generates/updates `builder/static_manifest.py` with:
    - `TASK_MANIFEST`
    - `GIFT_CARD_STATIC`
    - `SECURITY_SETTINGS_STATIC`
  This ensures the frozen EXE uses the latest configuration and module mappings.

---

## How to Navigate and Use the Project

1. **Development:**  
   - Run `builder.py` to launch the main game builder UI.
   - Use the Task Builder, Gift Card Selection, and Developer Zone tabs to create and manage tasks, choose gift card options, and adjust security settings.
   - The configuration is saved in `config.json` and tasks in `builder/tasks/tasks.json`.

2. **Exporting the Game:**  
   - In the Export Options tab, set your desired EXE name and security mode.
   - Click "Export to EXE". The export process (handled by `export.py`) will:
     - Update `config.json` with your current settings.
     - Generate a new `static_manifest.py` using `generate_manifest.py`.
     - Build the EXE using PyInstaller (compressing and stripping it).
     - Clean up temporary build artifacts.
     - Display a detailed "Export Report" dialog showing:
       - Imported task types from `TASK_MANIFEST`
       - Burned-in gift card data from `GIFT_CARD_STATIC`
       - Security settings from `SECURITY_SETTINGS_STATIC`
       - A summary of tasks from `builder/tasks/tasks.json`
   - The final executable is placed in the `exported` folder, and your main builder window remains open.

3. **Cleaning Up:**  
   - When closing the builder, the `closeEvent()` in `builder.py` calls a cleanup function (in `cleanup.py`) to remove all `__pycache__` folders, keeping the project directory tidy.

4. **Version Control:**  
   - The project is maintained using Git. For experimental features, work in the beta branch ([Beta Branch](https://github.com/NachoPayback/Nachocore-privaterepo-1912spgs/tree/beta)).  
   - The main branch (`main`) holds the stable, production-ready code.

---

## Module Responsibilities Summary

- **Builder UI (builder.py):**  
  Provides the main interface for task creation, gift card selection, export options, and developer features.

- **Export Process (export.py & generate_manifest.py):**  
  Combines configuration updates, static manifest generation, and PyInstaller packaging to produce a self-contained game executable. It cleans up build artifacts and provides a detailed export report.

- **Gift Card Management (gift_card.py):**  
  Handles loading, updating, and generating gift card data. In frozen mode, it uses the burned-in data from `static_manifest.py`.

- **Task Management (task_builder.py & shared/tasks/):**  
  Manages task creation, editing, and dynamic loading during gameplay.

- **Developer Tools (dev_zone.py, cleanup.py):**  
  Provide additional configuration options and maintain a clean project structure by removing temporary files.

---

This document should allow any developer—or an AI model with no prior memory—to fully understand the structure, purpose, and interrelationships of the project files in the beta branch. Use this as a reference for future modifications, optimizations, or feature additions.

---

*End of Documentation*
