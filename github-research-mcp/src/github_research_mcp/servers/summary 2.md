This repository, `beats`, is a collection of lightweight data shippers written in Go, designed to send operational data (logs, metrics, network packet data) to Elasticsearch, either directly or via Logstash, for visualization with Kibana. It serves as a monorepo containing `libbeat`, a Go framework for creating Beats, and several officially supported Beats.

## 1. Project Type & Technology Stack

*   **Primary Language**: Go (4443 files).
*   **Framework/Build Indicators**:
    *   `go.mod`: Defines Go module dependencies (`go.mod:1-3`).
    *   `Makefile`: Orchestrates build, test, and packaging tasks across multiple Beats (`Makefile:1-221`).
    *   `magefile.go`: Utilizes Mage, a Go-based build tool, for more complex build and automation tasks (`magefile.go:1-285`). This is a project-specific build system that complements or extends the traditional `Makefile`.
    *   `Dockerfile`: Present in individual Beat directories (e.g., `auditbeat/Dockerfile`, `filebeat/Dockerfile`) and `deploy/docker`, indicating Docker containerization for deployment and testing.
    *   `docker-compose.yml`: Used for defining and running multi-container Docker applications, particularly for testing environments (`deploy/docker/docker-compose.yml`, `auditbeat/docker-compose.yml`).
    *   `.buildkite/`: Contains Buildkite CI pipeline definitions (`.buildkite/pipeline.yml`), indicating a robust CI/CD setup.
    *   `.github/workflows/`: Contains GitHub Actions workflows (e.g., `golangci-lint.yml`), also for CI/CD.
*   **Directory Purpose & Layout**:
    *   `.buildkite/`: Contains Buildkite CI pipeline configurations and scripts (`.buildkite/pipeline.yml`, `.buildkite/scripts/`). This directory is crucial for understanding the project's continuous integration and deployment processes.
    *   `.devcontainer/`: Contains development container configurations (`.devcontainer/devcontainer.json`), facilitating a standardized development environment.
    *   `.github/`: GitHub-specific configurations, including issue templates, pull request templates, and GitHub Actions workflows (`.github/workflows/`).
    *   `auditbeat/`, `filebeat/`, `heartbeat/`, `libbeat/`, `metricbeat/`, `packetbeat/`, `winlogbeat/`: These are the main directories for each individual Beat. Each typically contains:
        *   `main.go`: The entry point for the Beat.
        *   `magefile.go`, `Makefile`: Build and automation scripts specific to that Beat.
        *   `_meta/`: Metadata, including common fields, configuration templates, and Kibana dashboards (e.g., `auditbeat/_meta/fields.common.yml`, `auditbeat/_meta/kibana/7/dashboard/`).
        *   `module/`: Contains definitions for various modules and metricsets that the Beat can collect data from (e.g., `auditbeat/module/auditd/`, `filebeat/module/apache/`).
        *   `tests/system/`: Python-based system tests for the Beat.
    *   `deploy/`: Contains deployment configurations for various environments like Cloud Foundry and Kubernetes (`deploy/cloudfoundry/`, `deploy/kubernetes/`).
    *   `dev-tools/`: Houses scripts and tools used for development, such as `magefile.go` for common build tasks, and scripts for managing dependencies and documentation (`dev-tools/mage/`, `dev-tools/cmd/`).
    *   `docs/`: Project documentation, including developer guides and reference documentation for each Beat (`docs/extend/`, `docs/reference/`).
    *   `licenses/`: Contains license files for the project and its dependencies.
    *   `x-pack/`: Contains the X-Pack specific Beats and extensions to `libbeat` (e.g., `x-pack/auditbeat/`, `x-pack/filebeat/`). This indicates a commercial/enterprise offering alongside the open-source components.
    *   `testing/`: Contains utilities and environments for testing, including Docker environments and certificate generation tools (`testing/environments/`, `testing/certutil/`).
    *   `script/`: General-purpose shell and Python scripts for various tasks like building docs, checking requirements, and generating files.

## 2. Key Files & Entry Points

*   **Main/Entry Point Files**:
    *   `libbeat/libbeat.go:29-33`: Defines the `RootCmd` for `libbeat` and executes it, serving as the core command-line interface for all Beats.
    *   `auditbeat/main.go:27-31`: The main entry point for Auditbeat, executing its root command.
    *   `filebeat/main.go:37-40`: The main entry point for Filebeat, executing its root command and initializing default inputs.
    *   `metricbeat/main.go:34-38`: The main entry point for Metricbeat, executing its root command.
    *   `packetbeat/main.go:28-32`: The main entry point for Packetbeat, executing its root command.
    *   `winlogbeat/main.go:35-39`: The main entry point for Winlogbeat, executing its root command.
    *   `x-pack/agentbeat/main.go`, `x-pack/dockerlogbeat/main.go`, `x-pack/osquerybeat/main.go`: Entry points for X-Pack specific Beats.
*   **Critical Configuration Files**:
    *   `go.mod`: Manages Go module dependencies and versions (`go.mod:1-249`).
    *   `Makefile`: Top-level build orchestration (`Makefile:1-221`).
    *   `magefile.go`: Go-based build automation, defining targets like `Fmt`, `UnitTest`, `IntegTest`, `Package`, and `Update` (`magefile.go:124-285`).
    *   `libbeat/_meta/config/general.reference.yml.tmpl`: Template for general Beat configuration options, including `name`, `tags`, `fields`, `queue` settings (memory/disk), and `max_procs` (`libbeat/_meta/config/general.reference.yml.tmpl:1-89`).
    *   `auditbeat/auditbeat.reference.yml`, `filebeat/filebeat.reference.yml`, `metricbeat/metricbeat.reference.yml`, `packetbeat/packetbeat.reference.yml`, `winlogbeat/winlogbeat.reference.yml`: Reference configuration files for each Beat, detailing all available options for modules, processors, and general settings.
    *   `filebeat/modules.d/*.yml.disabled`, `metricbeat/modules.d/*.yml.disabled`, `x-pack/filebeat/modules.d/*.yml.disabled`, `x-pack/metricbeat/modules.d/*.yml.disabled`: Disabled module configuration files, indicating available modules that can be enabled.
    *   `docker-compose.yml`: Used for setting up local development and testing environments with Docker.
    *   `.buildkite/pipeline.yml`: Defines the main Buildkite CI pipeline, including triggers for individual Beat builds based on file changes (`.buildkite/pipeline.yml:1-400`).
    *   `.github/workflows/golangci-lint.yml`: Configures `golangci-lint` for Go code quality checks on pull requests (`.github/workflows/golangci-lint.yml:1-53`).
*   **Dependency Management Files**:
    *   `go.mod`, `go.sum`: Standard Go module files.
    *   `dev-tools/notice/rules.json`, `dev-tools/notice/overrides.json`, `dev-tools/notice/NOTICE.txt.tmpl`: Used by `go-licence-detector` to generate the `NOTICE.txt` file, managing open-source license compliance (`Makefile:158-170`).
*   **CI/CD Definitions**:
    *   `.buildkite/pipeline.yml`: Central Buildkite pipeline orchestrating builds for various Beats and X-Pack components, triggered by changes in specific directories (`.buildkite/pipeline.yml:1-400`).
    *   `.github/workflows/`: Contains various GitHub Actions for tasks like unit tests, linting, and dependency updates (e.g., `auditbeat-macos-unit-tests.yml`, `golangci-lint.yml`).
*   **Primary Data Models/Entities**:
    *   `libbeat/ecs/`: Contains Go structs and definitions for the Elastic Common Schema (ECS), which standardizes event fields across the Elastic Stack (`libbeat/ecs/ecs.go`).
    *   `auditbeat/module/file_integrity/schema/`: Flatbuffers schema definitions for file integrity events (`auditbeat/module/file_integrity/schema/Event.go`).
    *   `filebeat/input/filestream/internal/input-logfile/store.go`: Manages the state of log files being harvested, including offsets and file identifiers.
    *   `metricbeat/mb/event.go`: Defines the `Event` structure used by Metricbeat metricsets to report collected data.
*   **Test Directories and Frameworks**:
    *   `*/tests/system/`: Python-based system tests for each Beat (e.g., `auditbeat/tests/system/`, `filebeat/tests/system/`). These often use `pytest.ini` for configuration.
    *   `*/_meta/test/`: Contains test data and expected outputs for modules and metricsets (e.g., `auditbeat/module/auditd/testdata/`).
    *   `libbeat/tests/integration/`: Go-based integration tests for `libbeat`.
    *   `testing/environments/docker/`: Docker environments for integration testing.
*   **Linting/Formatting/Type-check Configuration**:
    *   `.golangci.yml`: Configuration for `golangci-lint`, used for Go code quality checks.
    *   `.pylintrc`: Configuration for `pylint`, used for Python code quality checks.
    *   `.pre-commit-config.yaml`: Defines pre-commit hooks for various checks, including formatting and linting.
    *   `Makefile:117-122`: Python linting and formatting using `autopep8` and `pylint`.
*   **Important Documentation Files and Developer Tooling/Scripts**:
    *   `README.md`: General project overview and getting started information (`README.md:4-70`).
    *   `CONTRIBUTING.md`: Guidelines for contributing to the project (`CONTRIBUTING.md:5-17`).
    *   `docs/extend/`: Developer guides for extending Beats and creating new modules.
    *   `script/generate.py`: A Python script likely used for generating various project artifacts, such as configuration files or code.
    *   `dev-tools/cmd/`: Contains various Go commands for developer tooling, such as `asset` (`dev-tools/cmd/asset/asset.go`), `dashboards` (`dev-tools/cmd/dashboards/export_dashboards.go`), and `license` (`dev-tools/cmd/license/license_generate.go`).
*   **Unique Workflows**:
    *   **Code Generation**: `magefile.go` and scripts in `*/scripts/mage/generate/` are heavily used for generating boilerplate code, configuration files (e.g., `fields.go`, `fields.yml`, `module.yml`), and documentation. This is a core aspect of how new modules and metricsets are added and maintained.
    *   **Packaging Customization**: Each Beat's `magefile.go` includes `CustomizePackaging` functions (e.g., `auditbeat/magefile.go:90`, `filebeat/magefile.go:90`), allowing for project-specific adjustments to the packaging process.
    *   **Kibana Dashboard Management**: `magefile.go` includes `PackageBeatDashboards` (`magefile.go:87-122`) and `Dashboards` (`magefile.go:157-159`) targets for collecting and packaging Kibana dashboards, indicating a tight integration with Kibana for visualization.
    *   **X-Pack Integration**: The `x-pack/` directory contains extended versions of Beats and `libbeat` components, suggesting a modular approach where core functionality is in `libbeat` and specialized features are in X-Pack.

## 3. Key Patterns, Conventions, and Dependencies

*   **Observability**:
    *   **Logging**: `github.com/elastic/elastic-agent-libs/logp` is used for structured logging across the project (`libbeat/common/config.go:29`).
    *   **Metrics**: `github.com/elastic/elastic-agent-libs/monitoring` is used for collecting internal metrics (`metricbeat/mb/mb.go:35`).
*   **Error Handling**:
    *   `go.uber.org/multierr` is used for combining multiple errors, particularly in build and test processes (`magefile.go:31`).
    *   Custom error types like `ErrClosed`, `ErrFileTruncate`, `ErrInactive` are defined in `filebeat/input/filestream/filestream.go:40-43` for specific file processing scenarios.
*   **Data Storage**:
    *   `libbeat/publisher/queue/diskqueue/`: Implements a disk-based queue for event persistence, allowing events to survive restarts (`libbeat/publisher/queue/diskqueue/`).
    *   `libbeat/statestore/backend/memlog/`: Provides a memory-mapped log-based state store for efficient state management.
*   **API Design**:
    *   `libbeat/api/`: Defines an internal API for Beats, including named pipes on Windows (`libbeat/api/npipe/listener_windows.go`).
    *   `metricbeat/mb/mb.go`: Defines interfaces for `Module` and `MetricSet` implementations, standardizing how data collection components are structured and interact.
*   **Security**:
    *   **File Permissions**: `libbeat/common/config.go:118-149` includes `OwnerHasExclusiveWritePerms` to enforce strict file permissions on configuration files, ensuring only the owner or root can write to them.
    *   **FIPS Compliance**: References to `_fips.go` and `_nofips.go` files (e.g., `libbeat/common/flowhash/communityid_fips.go`, `libbeat/common/transport/kerberos/client_fips.go`) indicate support for FIPS 140-2 compliant cryptographic modules.
    *   **Keystore**: `libbeat/keystore` (implied by `libbeat/cmd/keystore.go`) is used for securely storing sensitive configuration values.
    *   **Seccomp**: `libbeat/common/seccomp/` contains policies for Linux seccomp, enhancing security by restricting system calls.
*   **Performance**:
    *   **Queuing**: Both in-memory (`memqueue`) and disk-based (`diskqueue`) queues are available for buffering events, configurable via `queue` settings in `general.reference.yml.tmpl`.
    *   **Concurrency**: `max_procs` setting in `general.reference.yml.tmpl` allows limiting CPU usage.
    *   **Backoff**: `github.com/elastic/beats/v7/libbeat/common/backoff` is used for implementing retry logic with exponential backoff, improving resilience in network operations (`filebeat/input/filestream/filestream.go:94`).
*   **Critical/Non-Standard Dependencies**:
    *   `github.com/elastic/go-libaudit/v2`: Used by Auditbeat for interacting with the Linux audit framework (`go.mod:63`).
    *   `github.com/google/gopacket`: Core dependency for Packetbeat for network packet capture and decoding (`go.mod:90`, `packetbeat/sniffer/sniffer.go:31`).
    *   `github.com/osquery/osquery-go`: Used by Osquerybeat for interacting with Osquery (`go.mod:107`).
    *   `github.com/vmware/govmomi`: Used by Metricbeat's vSphere module for interacting with VMware vSphere environments (`go.mod:121`).
    *   `github.com/Azure/azure-event-hubs-go/v3`, `github.com/Azure/azure-sdk-for-go`: Used by Filebeat for Azure Event Hubs and other Azure services (`go.mod:12-13`).
    *   `github.com/aws/aws-sdk-go-v2`: Used by Filebeat and Metricbeat for various AWS services (`go.mod:25-39`).
    *   `github.com/hashicorp/nomad/api`: Used by `x-pack/libbeat/autodiscover/providers/nomad` for Nomad integration (`go.mod:95`).
    *   `github.com/elastic/elastic-agent-libs`: A shared library providing common functionalities across Elastic agents and Beats (`go.mod:179`).
    *   `go.opentelemetry.io/collector/*`: OpenTelemetry Collector components, indicating integration with OpenTelemetry for telemetry data collection (`go.mod:221-247`). This is particularly visible in `x-pack/otel/`.