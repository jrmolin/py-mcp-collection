This repository, `beats`, is a collection of lightweight data shippers written in Go, designed to capture operational data (logs, metrics, network packets) and send it to Elasticsearch or Logstash for visualization in Kibana. It serves as the core framework (`libbeat`) for building these shippers and includes several officially supported Beats like Auditbeat, Filebeat, Heartbeat, Metricbeat, Packetbeat, Winlogbeat, and Osquerybeat.

## 1. Project Type & Technology Stack

*   **Project Type**: Data Shippers / Observability Agents. The repository contains a framework (`libbeat`) and multiple specialized agents (Beats) for collecting various types of operational data.
*   **Primary Programming Language**: Go (4443 files with `.go` extension).
*   **Framework Indicators**:
    *   `go.mod`: Indicates Go module management, listing numerous Go dependencies.
    *   `Makefile`: Used for build automation across various Beats.
    *   `magefile.go`: Indicates the use of Mage, a Go-based build tool, for more complex build tasks.
    *   `requirements.txt`, `pytest.ini`, `pylintrc`: Indicate the use of Python for scripting, testing, and linting.
    *   `Dockerfile`, `docker-compose.yml`: Used for containerization and defining multi-container Docker applications, especially for testing and deployment.
    *   `.buildkite/`: Contains Buildkite CI pipeline definitions (`.yml` files).
    *   `.github/workflows/`: Contains GitHub Actions workflows (`.yml` files) for CI/CD.
*   **Build System**: Primarily Go modules (`go.mod`) and Makefiles (`Makefile`, `make.bat`). Mage (`magefile.go`) is also extensively used for build automation, especially for tasks like packaging, testing, and documentation generation.

## 2. Directory Structure Analysis

The repository has a modular structure, with `libbeat` as the core framework and individual directories for each Beat.

*   `.buildkite/`: Contains Buildkite CI pipeline configurations and scripts for various Beats and deployment scenarios (Docker, Kubernetes).
*   `.devcontainer/`: Configuration for development containers, likely for VS Code Dev Containers.
*   `.github/`: GitHub-specific configurations, including issue templates, pull request templates, code owners, Dependabot, and GitHub Actions workflows.
*   `auditbeat/`: Source code, configuration, and tests for Auditbeat.
    *   `auditbeat/module/`: Contains subdirectories for different Auditbeat modules (e.g., `auditd`, `file_integrity`). Each module has its own configuration, fields, and test data.
    *   `auditbeat/tests/system/`: System-level tests for Auditbeat, written in Python.
*   `deploy/`: Contains deployment-related configurations for various platforms (Cloud Foundry, Docker, Kubernetes).
*   `dev-tools/`: Scripts and tools used for development, including Mage-related build scripts, dashboard export tools, and license generation.
    *   `dev-tools/mage/`: Core Mage build scripts and targets shared across Beats.
*   `docs/`: Documentation files, primarily in Markdown and AsciiDoc format, covering various aspects of Beats, modules, and developer guides.
*   `filebeat/`: Source code, configuration, and tests for Filebeat.
    *   `filebeat/input/`: Contains implementations for various Filebeat inputs (e.g., `filestream`, `journald`, `kafka`, `log`, `mqtt`, `redis`, `stdin`, `syslog`, `unix`, `winlog`).
    *   `filebeat/module/`: Contains subdirectories for different Filebeat modules (e.g., `apache`, `auditd`, `elasticsearch`, `haproxy`, `icinga`, `iis`, `kafka`, `kibana`, `logstash`, `mongodb`, `mysql`, `nats`, `nginx`, `osquery`, `pensando`, `postgresql`, `redis`, `santa`, `system`, `traefik`). Each module has its own configuration, fields, and test data.
    *   `filebeat/tests/system/`: System-level tests for Filebeat, written in Python.
*   `heartbeat/`: Source code, configuration, and tests for Heartbeat.
    *   `heartbeat/monitors/`: Contains implementations for different Heartbeat monitors (e.g., `http`, `icmp`, `tcp`).
    *   `heartbeat/tests/system/`: System-level tests for Heartbeat, written in Python.
*   `libbeat/`: The core Go framework for building Beats. This directory contains common utilities, publisher logic, configuration handling, and other shared components.
    *   `libbeat/autodiscover/`: Logic for automatically discovering services (e.g., Docker, Kubernetes, Jolokia).
    *   `libbeat/common/`: General-purpose utilities and data structures.
    *   `libbeat/ecs/`: Elastic Common Schema definitions.
    *   `libbeat/outputs/`: Implementations for various output types (e.g., Elasticsearch, Logstash, Kafka, Redis, Console, File).
    *   `libbeat/processors/`: Common event processors for enriching or manipulating data.
    *   `libbeat/publisher/`: Core publishing pipeline logic, including queues (memory, disk).
    *   `libbeat/reader/`: Components for reading and parsing input data (e.g., multiline, JSON, syslog).
    *   `libbeat/tests/system/`: System-level tests for `libbeat` components, written in Python.
*   `licenses/`: Contains various license files.
*   `metricbeat/`: Source code, configuration, and tests for Metricbeat.
    *   `metricbeat/mb/`: Metricbeat framework for modules and metricsets.
    *   `metricbeat/module/`: Contains subdirectories for different Metricbeat modules (e.g., `aerospike`, `apache`, `beat`, `ceph`, `consul`, `couchbase`, `couchdb`, `docker`, `dropwizard`, `elasticsearch`, `envoyproxy`, `etcd`, `golang`, `graphite`, `haproxy`, `http`, `jolokia`, `kafka`, `kibana`, `kubernetes`, `kvm`, `linux`, `logstash`, `memcached`, `meraki`, `mongodb`, `mssql`, `munin`, `mysql`, `nats`, `nginx`, `openmetrics`, `php_fpm`, `postgresql`, `prometheus`, `rabbitmq`, `redis`, `sql`, `stan`, `statsd`, `syncgateway`, `system`, `tomcat`, `traefik`, `uwsgi`, `vsphere`, `windows`, `zookeeper`). Each module contains multiple metricsets.
    *   `metricbeat/tests/system/`: System-level tests for Metricbeat, written in Python.
*   `packetbeat/`: Source code, configuration, and tests for Packetbeat.
    *   `packetbeat/protos/`: Implementations for various network protocols (e.g., `amqp`, `cassandra`, `dhcpv4`, `dns`, `http`, `icmp`, `memcache`, `mongodb`, `mysql`, `nfs`, `pgsql`, `redis`, `sip`, `thrift`, `tls`, `udp`).
    *   `packetbeat/tests/system/`: System-level tests for Packetbeat, written in Python.
*   `script/`: General-purpose scripts for building, testing, and documentation.
*   `testing/`: Utilities and environments for testing (e.g., `certutil`, Docker environments for various services, Terraform for ECH).
*   `tools/`: Go tools.
*   `winlogbeat/`: Source code, configuration, and tests for Winlogbeat.
    *   `winlogbeat/eventlog/`: Windows Event Log specific implementations.
    *   `winlogbeat/module/`: Contains modules for Windows event logs (e.g., `powershell`, `security`, `sysmon`).
    *   `winlogbeat/tests/system/`: System-level tests for Winlogbeat, written in Python.
*   `x-pack/`: Contains "X-Pack" (commercial) components of Beats, which extend the functionality of the open-source Beats. This includes additional Beats (e.g., `agentbeat`, `dockerlogbeat`, `osquerybeat`) and extended modules/processors for existing Beats.
    *   `x-pack/auditbeat/`, `x-pack/filebeat/`, `x-pack/heartbeat/`, `x-pack/metricbeat/`, `x-pack/packetbeat/`, `x-pack/winlogbeat/`: X-Pack specific extensions for the respective Beats, often including additional modules, inputs, or processors.
    *   `x-pack/otel/`: OpenTelemetry related components.

## 3. Key Files & Entry Points

*   **Main/Entry Point Files**:
    *   `auditbeat/main.go`: Entry point for Auditbeat.
    *   `filebeat/main.go`: Entry point for Filebeat.
    *   `heartbeat/main.go`: Entry point for Heartbeat.
    *   `metricbeat/main.go`: Entry point for Metricbeat.
    *   `packetbeat/main.go`: Entry point for Packetbeat.
    *   `winlogbeat/main.go`: Entry point for Winlogbeat.
    *   `x-pack/agentbeat/main.go`: Entry point for Agentbeat.
    *   `x-pack/dockerlogbeat/main.go`: Entry point for Dockerlogbeat.
    *   `x-pack/osquerybeat/main.go`: Entry point for Osquerybeat.
    *   `libbeat/cmd/root.go`: Defines the common root command structure for all Beats, handling CLI flags and subcommands.
    *   `libbeat/beat/beat.go`: Defines the `Beater` interface and `Beat` struct, which are fundamental to how each Beat runs and publishes events.
*   **Configuration Files**:
    *   `go.mod`: Go module definition, listing direct and indirect dependencies.
    *   `Makefile`: Main build script for the entire repository.
    *   `magefile.go`: Mage build script for the entire repository, orchestrating builds for individual Beats.
    *   `*.yml` files (e.g., `auditbeat/auditbeat.yml`, `filebeat/filebeat.yml`, `heartbeat/heartbeat.yml`, `metricbeat/metricbeat.yml`, `packetbeat/packetbeat.yml`, `winlogbeat/winlogbeat.yml`, `x-pack/osquerybeat/osquerybeat.yml`): Main configuration files for each Beat, defining inputs, modules, outputs, and other settings. These often include commented-out examples and references to more detailed configuration.
    *   `*_meta/config/*.tmpl`: Go template files for generating reference configuration files.
    *   `modules.d/*.yml.disabled`: Example module configurations that are disabled by default.
    *   `.github/workflows/*.yml`: GitHub Actions CI/CD workflow definitions.
    *   `.buildkite/*.yml`: Buildkite CI/CD pipeline definitions.
    *   `docker-compose.yml`: Used in various directories for setting up local development and testing environments with Docker.
*   **Dependency Management Files**:
    *   `go.mod`: Specifies Go module dependencies and versions.
    *   `go.sum`: Checksum file for Go module dependencies.
    *   `requirements.txt`: Python dependency file, primarily for testing and scripting tools.
*   **CI/CD Files**:
    *   `.github/workflows/`: Contains numerous GitHub Actions workflows for linting, testing, documentation builds, and other checks.
    *   `.buildkite/`: Contains Buildkite pipeline definitions for various build and deployment stages.
*   **Primary Data Models or Entities**:
    *   `libbeat/ecs/`: Contains Go files defining the Elastic Common Schema (ECS) fields, which are the standardized data model for events across all Beats. Examples include `agent.go`, `host.go`, `network.go`, `process.go`, `event.go`, `file.go`, etc.
    *   `libbeat/beat/event.go`: Defines the `Event` structure, the fundamental unit of data published by Beats.
    *   `*/_meta/fields.yml`: YAML files defining the specific fields collected by each Beat, module, or metricset, often mapping to ECS fields.
    *   `packetbeat/protos/*/event.go`: Defines event structures specific to each protocol.
    *   `metricbeat/mb/event.go`: Defines the `Event` structure for Metricbeat.

## 4. Key Patterns & Conventions

*   **Modular Architecture**: The repository is highly modular. `libbeat` provides the core framework, and each specific "Beat" (e.g., Filebeat, Metricbeat) is built on top of it. Within each Beat, functionality is further broken down into "modules" and "metricsets" (for Metricbeat) or "inputs" (for Filebeat) or "protocols" (for Packetbeat). This allows for clear separation of concerns and extensibility.
*   **Configuration-Driven**: Beats are heavily configured via YAML files (e.g., `*.yml`, `*.yml.tmpl`). These configurations define what data to collect, how to process it, and where to send it. Many configurations support reloading without restarting the Beat.
*   **Event-Based Data Flow**: Data is processed as "events." Each event is a structured piece of data, typically conforming to the Elastic Common Schema (ECS).
*   **Go-based Build Automation (Mage)**: While `Makefile` is present, `magefile.go` in the root and within each Beat directory indicates a strong preference for Mage for build tasks. This allows build logic to be written in Go, leveraging Go's tooling and type safety. The `magefile.go` in the root orchestrates tasks across all sub-projects.
*   **Cross-Platform Support**: The presence of platform-specific Go files (e.g., `_linux.go`, `_windows.go`, `_darwin.go`, `_other.go`) and build targets (e.g., `crosscompile` in `Makefile`) indicates a commitment to supporting multiple operating systems.
*   **Observability (Logging, Metrics)**:
    *   **Logging**: `github.com/elastic/elastic-agent-libs/logp` is used for structured logging. Configuration files (`*.yml`) include `logging.level` and `logging.selectors` to control verbosity and filter logs by component. Debugging is a common practice, with `logp.MakeDebug` used to create debug loggers for specific components (e.g., `packetbeat/protos/http/http.go`).
    *   **Metrics**: `github.com/elastic/elastic-agent-libs/monitoring` is used for internal metrics collection. Beats can export these metrics to a central Elasticsearch monitoring cluster, configured via `monitoring.enabled` and `monitoring.elasticsearch` in `*.yml` files.
    *   **Tracing**: `github.com/elastic/go-concert/ctxtool` and `go.elastic.co/apm/v2` are used for context propagation and APM tracing, respectively. `instrumentation` sections in `*.yml` files allow enabling and configuring APM tracing.
*   **Error Handling**: Errors are typically returned as `error` types in Go. The `github.com/pkg/errors` library is used for enhanced error handling (e.g., wrapping errors). Specific error types are defined for various components (e.g., `libbeat/beat/error.go`, `libbeat/statestore/error.go`).
*   **Data Storage**:
    *   **Configuration**: Configuration is primarily stored in YAML files.
    *   **Internal State**: `libbeat/statestore/` and `libbeat/publisher/queue/diskqueue/` indicate the use of persistent state storage, likely for tracking read offsets or other operational data to ensure data integrity across restarts. `github.com/dgraph-io/badger/v4` is a dependency, suggesting a key-value store for this purpose.
    *   **Output**: Data is primarily shipped to Elasticsearch or Logstash.
*   **API Design**:
    *   **Internal API**: `libbeat/api/` defines an internal HTTP API for managing and interacting with the Beat.
    *   **External APIs**: Beats interact with various external APIs and services for data collection (e.g., AWS, Azure, GCP, Docker, Kubernetes, various databases, message queues, network protocols). The specific API interactions are encapsulated within the respective modules/inputs/protocols.
*   **Security**:
    *   **Configuration Permissions**: `libbeat/common/config.go` includes `OwnerHasExclusiveWritePerms` to enforce strict file permissions on configuration files, ensuring only the owner or root can write to them.
    *   **Keystore**: `libbeat/cmd/keystore.go` indicates support for a keystore to securely store sensitive configuration values (e.g., passwords, API keys).
    *   **SSL/TLS**: Extensive configuration options for SSL/TLS are present in output configurations (e.g., `output.elasticsearch.protocol`, `ssl.certificate_authorities`, `ssl.certificate`, `ssl.key`), indicating secure communication with endpoints.
    *   **Seccomp**: `libbeat/common/seccomp/` and `libbeat/ebpf/seccomp_linux.go` indicate the use of seccomp profiles on Linux for syscall filtering, enhancing security by limiting the system calls a Beat can make. `x-pack/osquerybeat/osquerybeat.yml` explicitly disables seccomp for osqueryd, highlighting a specific security consideration for that Beat.
    *   **FIPS Compliance**: The presence of `_fips.go` and `_nofips.go` files (e.g., `auditbeat/helper/hasher/`, `libbeat/common/flowhash/`, `libbeat/common/kafka/`, `libbeat/common/transport/kerberos/`, `libbeat/processors/fingerprint/`) suggests support for FIPS 140-2 compliant cryptographic modules.
*   **Performance**:
    *   **Batching**: The `libbeat/publisher/pipeline/ttl_batch.go` and `libbeat/publisher/queue/memqueue/broker.go` indicate that events are batched before being sent to outputs, improving efficiency.
    *   **Queuing**: `libbeat/publisher/queue/` provides both in-memory (`memqueue`) and disk-based (`diskqueue`) queues to buffer events, ensuring data durability and handling backpressure.
    *   **Backoff/Retry**: `libbeat/common/backoff/` and `libbeat/outputs/backoff.go` implement exponential backoff and retry mechanisms for resilient communication with external services.
    *   **Concurrency**: Go routines are extensively used for concurrent processing of tasks (e.g., harvesting files, processing events, sending to outputs).
*   **Testing**:
    *   **Unit Tests**: Go files ending with `_test.go` contain unit tests.
    *   **Integration Tests**: Go files like `_integration_test.go` and Python scripts in `*/tests/system/` directories are used for integration and system tests, often leveraging Docker Compose (`docker-compose.yml`) to set up test environments.
    *   **Golden Files**: Many test directories contain `*.json` and `*-expected.json` files, indicating the use of golden file testing for verifying output consistency.
    *   **Test Data**: `testdata/` directories are common, containing sample logs, configurations, and other data for testing.
    *   **Python Testing Framework**: `pytest.ini` and `*.py` files in `tests/system` directories indicate a Python-based testing framework for system and integration tests.

## 5. Key Dependencies

*   **Go Libraries**:
    *   `github.com/elastic/elastic-agent-libs`: Core shared libraries for Elastic Agents, including configuration, logging, monitoring, and user agent utilities.
    *   `github.com/elastic/beats/v7/libbeat`: The foundational framework for all Beats.
    *   `cloud.google.com/go/*`, `github.com/Azure/azure-sdk-for-go`, `github.com/aws/aws-sdk-go-v2`: SDKs for interacting with major cloud providers (Google Cloud, Azure, AWS) for metadata enrichment and data collection.
    *   `github.com/docker/docker`, `k8s.io/api`, `k8s.io/apimachinery`, `k8s.io/client-go`: Libraries for interacting with Docker and Kubernetes for auto-discovery and metadata.
    *   `github.com/osquery/osquery-go`: For interacting with Osquery, used by Osquerybeat.
    *   `github.com/prometheus/client_model`, `github.com/prometheus/common`, `github.com/prometheus/procfs`: Prometheus client libraries for metrics collection.
    *   `github.com/vmware/govmomi`: VMware vSphere API client, used by Metricbeat's vSphere module.
    *   `github.com/go-sql-driver/mysql`, `github.com/lib/pq`, `github.com/microsoft/go-mssqldb`, `github.com/godror/godror`: Database drivers for MySQL, PostgreSQL, MSSQL, and Oracle, used by various Metricbeat modules and Filebeat inputs.
    *   `github.com/elastic/sarama`: Kafka client library.
    *   `github.com/gomodule/redigo`: Redis client library.
    *   `github.com/eclipse/paho.mqtt.golang`: MQTT client library.
    *   `github.com/miekg/dns`: DNS client library.
    *   `github.com/google/flatbuffers`: Used for efficient serialization, particularly in Auditbeat's file integrity module.
    *   `github.com/cilium/ebpf`: eBPF library for Linux kernel tracing, used in Auditbeat's file integrity and system socket modules.
    *   `github.com/dgraph-io/badger/v4`: Embedded key-value store for persistent state.
    *   `go.opentelemetry.io/collector/*`: OpenTelemetry Collector components, indicating integration with OpenTelemetry for metrics and traces.
*   **External APIs/Services**:
    *   **Elasticsearch**: Primary destination for collected data and monitoring metrics.
    *   **Logstash**: Alternative destination for collected data.
    *   **Kibana**: Used for visualizing collected data and loading dashboards.
    *   **AWS, Azure, Google Cloud**: Various services (EC2, S3, CloudWatch, Event Hubs, Blob Storage, Pub/Sub, Compute, Monitoring) are integrated for data collection and metadata enrichment.
    *   **Docker, Kubernetes, Nomad**: Used for auto-discovery of services and collecting container/orchestration metadata.
    *   **APM Server**: Destination for instrumentation traces.
    *   **Databases**: MySQL, PostgreSQL, MSSQL, Oracle, MongoDB, Cassandra, Redis, Aerospike, Couchbase, CockroachDB are monitored by various Beats.
    *   **Message Queues**: Kafka, RabbitMQ, NATS, ActiveMQ are monitored.
    *   **Network Protocols**: HTTP, DNS, ICMP, AMQP, DHCPv4, Memcache, NFS, PgSQL, Redis, SIP, Thrift, TLS are analyzed by Packetbeat.
    *   **Osquery**: Used by Osquerybeat to collect system information.
    *   **Meraki Dashboard API**: Used by Metricbeat's Meraki module.
    *   **OpenAI**: Used by Metricbeat's OpenAI module.
    *   **Salesforce**: Used by Filebeat's Salesforce input.
    *   **Snyk**: Used by Filebeat's Snyk module.
    *   **Sophos XG Firewall**: Used by Filebeat's Sophos module.
    *   **Suricata**: Used by Filebeat's Suricata module.
    *   **Threat Intelligence Feeds**: Abuse.ch, AlienVault OTX, Anomali, MalwareBazaar, MISP, ThreatQ are integrated by Filebeat's threatintel module.
    *   **Zoom Webhooks**: Used by Filebeat's Zoom module.

## 6. Development Workflow Indicators

*   **Test Directories and Frameworks**:
    *   `*/_test.go`: Standard Go unit tests.
    *   `*/_integration_test.go`: Go integration tests.
    *   `*/tests/system/`: Python-based system/integration tests, often using `pytest.ini` and `requirements.txt`.
    *   `testing/`: Contains shared testing utilities and Docker environments for various services.
    *   `Makefile` targets like `testsuite`, `unittest`, `integtest`, `coverage-report`.
*   **Linting/Formatting Configuration**:
    *   `.golangci.yml`: Configuration for `golangci-lint`, a popular Go linter.
    *   `.pylintrc`: Configuration for `pylint`, a Python linter.
    *   `.pre-commit-config.yaml`: Configuration for pre-commit hooks, enforcing code quality standards before commits.
    *   `Makefile` targets like `check-python`, `check-headers`, `fmt`, `misspell`.
*   **Documentation Files**:
    *   `README.md`: Main project overview.
    *   `CONTRIBUTING.md`: Guidelines for contributing to the project.
    *   `CHANGELOG.asciidoc`, `CHANGELOG-developer.asciidoc`: Changelog files.
    *   `docs/`: Extensive documentation, including developer guides (`docs/extend/`), reference documentation for each Beat and its modules (`docs/reference/`), and troubleshooting guides.
    *   `*/_meta/docs.md`: Module-specific documentation.
*   **Development Tools and Scripts**:
    *   `magefile.go`: Go-based build automation tool.
    *   `Makefile`: Traditional build automation.
    *   `dev-tools/`: Contains various scripts for development tasks (e.g., `aggregate_coverage.py`, `cherrypick_pr`, `get_version`, `promote_docs`, `set_version`).
    *   `script/`: Contains general-purpose scripts (e.g., `build_docs.sh`, `generate.py`, `pre_commit.sh`).
    *   `.go-version`, `.python-version`: Specify required Go and Python versions.
    *   `.editorconfig`: Ensures consistent coding styles across different editors.
    *   `Vagrantfile`: For setting up development virtual machines.

## 7. Navigation Guidance

To understand and work with this repository, an AI coding agent should prioritize the following:

1.  **Overall Structure**: Start with the root `README.md` for a high-level overview of the project and its components.
2.  **Core Framework**:
    *   `libbeat/`: This directory is crucial for understanding the fundamental architecture, event processing, and publishing mechanisms.
    *   `libbeat/beat/beat.go`: Defines the core `Beater` interface and `Beat` struct, which every Beat implements.
    *   `libbeat/cmd/root.go`: Understands how CLI commands are structured and handled across all Beats.
    *   `libbeat/ecs/`: Essential for understanding the standardized data model.
    *   `libbeat/publisher/pipeline/pipeline.go`: Explains the event publishing pipeline, including queues and outputs.
    *   `libbeat/common/config.go`: Details how configuration files are loaded and validated.
3.  **Specific Beat Implementation**:
    *   Choose the relevant Beat directory (e.g., `filebeat/`, `metricbeat/`, `auditbeat/`).
    *   `*/main.go`: The entry point for the specific Beat.
    *   `*/magefile.go`: Understand the build process for that specific Beat.
    *   `*/config/config.go`: How the Beat's configuration is structured and parsed.
    *   `*/beater/`: Contains the core logic for the Beat's `Run` loop.
4.  **Modules/Inputs/Protocols**:
    *   Navigate to `*/module/` (for Auditbeat, Filebeat, Metricbeat, Winlogbeat, X-Pack Beats) or `packetbeat/protos/` to understand how specific data sources or protocols are handled.
    *   Each subdirectory within these typically contains the Go implementation, configuration (`config.go`, `*.yml`), field definitions (`fields.go`, `_meta/fields.yml`), and test data.
5.  **Configuration and Documentation**:
    *   `*.yml` files in each Beat's root directory (e.g., `filebeat/filebeat.yml`) provide example configurations.
    *   `docs/reference/` and `docs/extend/` offer comprehensive guides and detailed explanations of concepts, configurations, and development practices.
    *   `CONTRIBUTING.md` is important for understanding development guidelines and expectations.
6.  **Testing**:
    *   `*/tests/system/` directories are important for understanding how end-to-end functionality is verified.
    *   `_test.go` files alongside source code provide examples of expected behavior.
7.  **Build System**:
    *   `magefile.go` (root and sub-projects) and `Makefile` are key to understanding how the project is built, tested, and packaged.

For any task, the AI agent should first identify which specific Beat and its modules/inputs/protocols are relevant, then delve into their respective Go source files, configuration files, and documentation.