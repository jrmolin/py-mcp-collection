# Elasticsearch Cluster Troubleshooting Procedure using ES MCP Tools

This document outlines a procedure for diagnosing common Elasticsearch cluster issues using the available tools in the ES MCP server. Note that while the ES MCP tools are useful for diagnosis, many resolution steps require actions not currently available through these tools and must be performed manually or via other means.

## 1. Watermark Errors

**Diagnosis:**
Use the following tools to check shard allocation and recovery status:
- Check shard allocation: [`es.cat.shards`](es_mcp/main.py:44)
- Check active shard recovery: [`es.cat.recovery`](es_mcp/main.py:41) with `active_only: true`

*Note: The `_cluster/allocation/explain` API is not available as an ES MCP tool for detailed allocation explanations.*

**Resolution:**
Resolution typically involves freeing up disk space (deleting indices, updating ILM policies, scaling nodes) or temporarily adjusting watermarks. These actions are not directly supported by the current ES MCP tools.

## 2. Circuit Breaker Errors

**Diagnosis:**
Check JVM memory usage and circuit breaker statistics:
- Check node heap usage: [`es.cat.nodes`](es_mcp/main.py:38) with `h: name,node*,heap*`
- Check circuit breaker statistics: [`es.nodes.stats`](es_mcp/main.py:54) with `breaker` metric

**Resolution:**
Resolution involves reducing JVM memory pressure (see below), avoiding fielddata on text fields, or clearing the fielddata cache. Clearing the cache is not directly supported by the current ES MCP tools.

## 3. High CPU Usage

**Diagnosis:**
Monitor node CPU usage and thread pool statistics:
- Check node CPU usage: [`es.cat.nodes`](es_mcp/main.py:38) with `s: cpu:desc`
- Check thread pool statistics: [`es.cat.thread_pool`](es_mcp/main.py:48)

*Note: The `_nodes/hot_threads` API is not available as an ES MCP tool for detailed thread analysis.*

**Resolution:**
Resolution involves scaling the cluster, optimizing requests, or canceling long-running tasks. Canceling tasks is not directly supported by the current ES MCP tools.

## 4. High JVM Memory Pressure

**Diagnosis:**
Check JVM memory statistics:
- Check JVM memory pool usage: [`es.nodes.stats`](es_mcp/main.py:54) with `filter_path: nodes.*.jvm.mem.pools.old`

*Note: Accessing garbage collection logs or capturing heap dumps is not supported by the current ES MCP tools.*

**Resolution:**
Resolution involves reducing shard count, avoiding expensive searches (requires setting updates not available), spreading bulk requests, or upgrading node memory. Modifying settings is not directly supported.

## 5. Red or Yellow Cluster Health Status

**Diagnosis:**
Check cluster and shard health:
- Check cluster health status: [`es.cluster.health`](es_mcp/main.py:50) with `filter_path: status,*_shards`
- View unassigned shards: [`es.cat.shards`](es_mcp/main.py:44) with `h: index,shard,prirep,state,node,unassigned.reason&s=state`

*Note: The `_cluster/allocation/explain` API is not available as an ES MCP tool for detailed allocation explanations.*

**Resolution:**
Resolution involves addressing underlying causes like lost nodes (requires rerouting not available), fixing allocation settings (requires setting updates not available), adjusting replica counts (requires setting updates not available), freeing up disk space (requires actions not available), re-enabling allocation (requires setting updates not available), or recovering lost primary shards (requires rerouting or data manipulation not available). Many resolution steps are not supported by the current ES MCP tools.

## 6. Rejected Requests

**Diagnosis:**
Check thread pool and circuit breaker statistics:
- Check rejected tasks per thread pool: [`es.cat.thread_pool`](es_mcp/main.py:48) with `h: id,name,queue,active,rejected,completed`
- Check tripped circuit breakers: [`es.nodes.stats`](es_mcp/main.py:54) with `breaker` metric
- Check indexing pressure rejections: [`es.nodes.stats`](es_mcp/main.py:54) with `filter_path: nodes.*.indexing_pressure`

**Resolution:**
Resolution involves addressing high CPU and JVM memory pressure (see above).

## 7. Task Queue Backlog

**Diagnosis:**
Check thread pool and task statistics:
- Check thread pool status: [`es.cat.thread_pool`](es_mcp/main.py:48) with `v&s=t,n&h=type,name,node_name,active,queue,rejected,completed`
- Identify long-running tasks: [`es.cat.tasks`](es_mcp/main.py:46)

*Note: The `_nodes/hot_threads` API and detailed `_tasks` information are not directly available as ES MCP tools.*

**Resolution:**
Resolution involves increasing resources (reducing CPU usage, increasing thread pool size - requires setting updates not available), canceling stuck tasks (not directly supported), or addressing hot spotting (see below).

## 8. Mapping Explosion

**Diagnosis:**
Check index field counts and resolve index patterns:
- Check index field counts (requires accessing mappings or field capabilities not available).
- Resolve index patterns: [`es.indices.resolve_index`](es_mcp/main.py:58)

*Note: Accessing detailed mappings or field capabilities is not directly supported by the current ES MCP tools.*

**Resolution:**
Resolution involves preventing further dynamic mapping issues (requires setting updates not available), reindexing (not directly supported), or deleting indices (not directly supported).

## 9. Hot Spotting

**Diagnosis:**
Identify uneven resource distribution across nodes:
- Detect uneven resource utilization: [`es.cat.nodes`](es_mcp/main.py:38) with `s: master,name&h=name,master,node.role,heap.percent,disk.used_percent,cpu`
- Check shard balancing: [`es.cat.allocation`](es_mcp/main.py:24) with `s: node&h=node,shards,disk.percent,disk.indices,disk.used`
- Check node indexing stats: [`es.nodes.stats`](es_mcp/main.py:54) with `filter_path: nodes.*.name,nodes.*.indices.indexing`
- Check thread pool queues (write, search): [`es.cat.thread_pool`](es_mcp/main.py:48) with `v=true&s=n,nn&h=n,nn,q,a,r,c`
- Check longest running tasks: [`es.cat.tasks`](es_mcp/main.py:46) with `v&s=time:desc&h=type,action,running_time,node,cancellable`
- Check pending cluster tasks: [`es.cat.pending_tasks`](es_mcp/main.py:39)

*Note: The `_nodes/hot_threads` API and detailed shard-level stats are not directly available as ES MCP tools.*

**Resolution:**
Resolution involves hardware changes, rebalancing shards (requires setting updates or rerouting not available), increasing thread pool size (requires setting updates not available), or canceling tasks (not directly supported).

This procedure provides a framework for using the available ES MCP tools to diagnose common Elasticsearch cluster issues. For resolution, manual intervention or the use of other tools outside of this specific ES MCP server may be required.