# Enterprise NetDevOps Configuration & Backup Engine

A modular, scalable, and secure NetDevOps automation framework built for Cisco IOS devices using modern Python practices.

## Features
- **Data Validation**: Enforces IP address, VLAN ID, and port strict typing using **Pydantic**.
- **Template Engine**: Dynamically generates production-grade Cisco CLI configurations via **Jinja2**.
- **Parallel Execution**: Leverages **ThreadPoolExecutor** for concurrent multi-device asynchronous backups.
- **Security First**: Isolates sensitive credentials using `.env` environment variables and `.gitignore`.
- **Automated Logging & Testing**: Centralized application logging paired with automated unit testing via **pytest**.

## Project Architecture
```text
NetDevOps_Project/
├── inventory/      # Device inventory files (YAML)
├── models/         # Pydantic data verification schemas
├── templates/      # Jinja2 configuration templates
├── scripts/        # Configuration deploy and parallel backup scripts
├── backups/        # Generated configuration backups
├── logs/           # Application execution logs
└── tests/          # Unit test suites