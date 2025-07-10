 : 0 - 13: mapped_pages:
 : 1 - 82: - https://www.elastic.co/guide/en/beats/auditbeat/
 : 2 - 251401: # ECS fields [exported-fields-ecs]  This section d
   : 3 - 889: # ECS fields [exported-fields-ecs]  This section d
   : 4 - 733: **`labels`** :   Custom key/value pairs. Can be us
   : 5 - 1760: ## agent [_agent]  The agent fields contain the da
     : 6 - 1042: ## agent [_agent]  The agent fields contain the da
     : 7 - 716: example: 8a4f500d  **`agent.name`** :   Custom nam
   : 8 - 614: ## as [_as]  An autonomous system (AS) is a collec
     : 9 - 614: ## as [_as]  An autonomous system (AS) is a collec
   : 10 - 7133: ## client [_client]  A client is defined as the in
     : 11 - 19: ## client [_client]
     : 12 - 896: A client is defined as the initiator of a network 
     : 13 - 1034: **`client.address`** :   Some event client address
     : 14 - 1111: **`client.geo.city_name`** :   City name.  type: k
     : 15 - 1073: **`client.geo.region_iso_code`** :   Region ISO co
     : 16 - 622: type: long  format: string  **`client.packets`** :
     : 17 - 1028: **`client.subdomain`** :   The subdomain portion o
     : 18 - 1049: example: co.uk  **`client.user.domain`** :   Name 
     : 19 - 285: **`client.user.name`** :   Short name or login of 
   : 20 - 5499: ## cloud [_cloud]  Fields related to the cloud or 
     : 21 - 991: ## cloud [_cloud]  Fields related to the cloud or 
     : 22 - 1072: **`cloud.origin.account.id`** :   The cloud accoun
     : 23 - 1046: example: my-project  **`cloud.origin.project.name`
     : 24 - 1040: **`cloud.provider`** :   Name of the cloud provide
     : 25 - 1032: **`cloud.target.availability_zone`** :   Availabil
     : 26 - 308: **`cloud.target.service.name`** :   The cloud serv
   : 27 - 1950: ## code_signature [_code_signature]  These fields 
     : 28 - 1008: ## code_signature [_code_signature]  These fields 
     : 29 - 940: **`code_signature.subject_name`** :   Subject name
   : 30 - 1591: ## container [_container]  Container fields are us
     : 31 - 976: ## container [_container]  Container fields are us
     : 32 - 613: **`container.memory.usage`** :   Memory usage perc
   : 33 - 2261: ## data_stream [_data_stream]  The data_stream fie
     : 34 - 894: ## data_stream [_data_stream]  The data_stream fie
     : 35 - 584: **`data_stream.dataset`** :   The field can contai
     : 36 - 779: **`data_stream.namespace`** :   A user defined nam
   : 37 - 7008: ## destination [_destination_2]  Destination field
     : 38 - 930: ## destination [_destination_2]  Destination field
     : 39 - 1065: **`destination.as.number`** :   Unique number allo
     : 40 - 1023: **`destination.geo.country_iso_code`** :   Country
     : 41 - 1090: **`destination.geo.timezone`** :   The time zone o
     : 42 - 1033: format: string  **`destination.registered_domain`*
     : 43 - 1029: example: east  **`destination.top_level_domain`** 
     : 44 - 826: **`destination.user.group.id`** :   Unique identif
   : 45 - 3983: ## dll [_dll]  These fields contain information ab
     : 46 - 1034: ## dll [_dll]  These fields contain information ab
     : 47 - 1068: **`dll.code_signature.status`** :   Additional inf
     : 48 - 1057: **`dll.code_signature.valid`** :   Boolean to capt
     : 49 - 818: **`dll.pe.file_version`** :   Internal version of 
   : 50 - 4934: ## dns [_dns]  Fields describing DNS queries and a
     : 51 - 957: ## dns [_dns]  Fields describing DNS queries and a
     : 52 - 954: **`dns.answers.data`** :   The data describing the
     : 53 - 842: **`dns.id`** :   The DNS packet identifier assigne
     : 54 - 708: **`dns.question.registered_domain`** :   The highe
     : 55 - 1029: **`dns.question.top_level_domain`** :   The effect
     : 56 - 434: **`dns.type`** :   The type of DNS event captured,
   : 57 - 386: ## ecs [_ecs]  Meta-information specific to ECS.  
     : 58 - 386: ## ecs [_ecs]  Meta-information specific to ECS.  
   : 59 - 2883: ## elf [_elf]  These fields contain Linux Executab
     : 60 - 1119: ## elf [_elf]  These fields contain Linux Executab
     : 61 - 1114: type: keyword  **`elf.header.type`** :   Header ty
     : 62 - 646: type: long  format: string  **`elf.sections.virtua
   : 63 - 666: ## error [_error]  These fields can represent erro
     : 64 - 666: ## error [_error]  These fields can represent erro
   : 65 - 11163: ## event [_event]  The event fields are used for c
     : 66 - 1029: ## event [_event]  The event fields are used for c
     : 67 - 44: type: keyword  example: user-password-change
     : 68 - 1107: **`event.agent_id_status`** :   Agents are normall
     : 69 - 845: type: keyword  example: verified  **`event.categor
     : 70 - 1034: **`event.created`** :   event.created contains the
     : 71 - 1055: **`event.duration`** :   Duration of the event in 
     : 72 - 906: **`event.kind`** :   This is one of four ECS Categ
     : 73 - 475: **`event.original`** :   Raw text message of entir
     : 74 - 946: **`event.outcome`** :   This is one of four ECS Ca
     : 75 - 825: **`event.provider`** :   Source of the event. Even
     : 76 - 934: **`event.reference`** :   Reference URL linking to
     : 77 - 745: **`event.severity`** :   The numeric severity of t
     : 78 - 796: **`event.timezone`** :   This field should be popu
     : 79 - 396: **`event.url`** :   URL linking to an external sys
   : 80 - 712: ## faas [_faas]  The user fields describe informat
     : 81 - 712: ## faas [_faas]  The user fields describe informat
   : 82 - 14039: ## file [_file_2]  A file is defined as a set of i
     : 83 - 1046: ## file [_file_2]  A file is defined as a set of i
     : 84 - 1035: example: sha256  **`file.code_signature.exists`** 
     : 85 - 1059: **`file.code_signature.timestamp`** :   Date and t
     : 86 - 1085: **`file.directory`** :   Directory where the file 
     : 87 - 1100: **`file.elf.header.data`** :   Data table of the E
     : 88 - 1101: type: keyword  **`file.elf.sections.name`** :   EL
     : 89 - 1030: **`file.extension`** :   File extension, excluding
     : 90 - 1132: example: Zone.Identifer  **`file.gid`** :   Primar
     : 91 - 733: type: keyword  example: alice  **`file.path`** :  
     : 92 - 1015: **`file.pe.imphash`** :   A hash of the imports in
     : 93 - 1080: **`file.uid`** :   The user ID (UID) or security i
     : 94 - 1099: **`file.x509.issuer.organizational_unit`** :   Lis
     : 95 - 1055: **`file.x509.serial_number`** :   Unique serial nu
     : 96 - 443: **`file.x509.subject.organization`** :   List of o
   : 97 - 1532: ## geo [_geo]  Geo fields can carry data about a s
     : 98 - 1017: ## geo [_geo]  Geo fields can carry data about a s
     : 99 - 513: **`geo.postal_code`** :   Postal code associated w
   : 100 - 387: ## group [_group_3]  The group fields are meant to
     : 101 - 387: ## group [_group_3]  The group fields are meant to
   : 102 - 770: ## hash [_hash]  The hash fields represent differe
     : 103 - 770: ## hash [_hash]  The hash fields represent differe
   : 104 - 5679: ## host [_host]  A host is defined as a general co
     : 105 - 964: ## host [_host]  A host is defined as a general co
     : 106 - 1098: **`host.domain`** :   Name of the domain of which 
     : 107 - 936: type: keyword  example: boston-dc  **`host.geo.pos
     : 108 - 1033: **`host.mac`** :   Host MAC addresses. The notatio
     : 109 - 835: **`host.network.ingress.packets`** :   The number 
     : 110 - 803: **`host.os.type`** :   Use the `os.type` field to 
   : 111 - 2441: ## http [_http]  Fields related to HTTP activity. 
     : 112 - 1036: ## http [_http]  Fields related to HTTP activity. 
     : 113 - 881: **`http.request.mime_type`** :   Mime type of the 
     : 114 - 520: **`http.response.mime_type`** :   Mime type of the
   : 115 - 803: ## interface [_interface]  The interface fields ar
     : 116 - 803: ## interface [_interface]  The interface fields ar
   : 117 - 3382: ## log [_log]  Details about the event’s logging m
     : 118 - 1033: ## log [_log]  Details about the event’s logging m
     : 119 - 909: **`log.logger`** :   The name of the logger inside
     : 120 - 1035: **`log.syslog.facility.code`** :   The Syslog nume
     : 121 - 399: **`log.syslog.severity.name`** :   The Syslog nume
   : 122 - 4189: ## network [_network]  The network is defined as t
     : 123 - 899: ## network [_network]  The network is defined as t
     : 124 - 242: **`network.community_id`** :   A hash of source an
     : 125 - 1039: type: keyword  example: 1:hO+sN4H+MG5MY/8hIrXPqc4Z
     : 126 - 961: **`network.iana_number`** :   IANA Protocol Number
     : 127 - 1040: **`network.packets`** :   Total packets transferre
   : 128 - 7234: ## observer [_observer]  An observer is defined as
     : 129 - 795: ## observer [_observer]  An observer is defined as
     : 130 - 973: **`observer.egress`** :   Observer.egress holds in
     : 131 - 1093: **`observer.egress.zone`** :   Network zone of out
     : 132 - 940: type: keyword  example: boston-dc  **`observer.geo
     : 133 - 977: **`observer.ingress.interface.alias`** :   Interfa
     : 134 - 1070: **`observer.mac`** :   MAC addresses of the observ
     : 135 - 959: **`observer.os.name`** :   Operating system name, 
     : 136 - 413: **`observer.type`** :   The type of the observer t
   : 137 - 1102: ## orchestrator [_orchestrator]  Fields that descr
     : 138 - 1102: ## orchestrator [_orchestrator]  Fields that descr
   : 139 - 441: ## organization [_organization]  The organization 
     : 140 - 441: ## organization [_organization]  The organization 
   : 141 - 1208: ## os [_os]  The OS fields contain information abo
     : 142 - 1080: ## os [_os]  The OS fields contain information abo
     : 143 - 126: type: keyword  example: macos  **`os.version`** : 
   : 144 - 1985: ## package [_package]  These fields contain inform
     : 145 - 1059: ## package [_package]  These fields contain inform
     : 146 - 924: **`package.license`** :   License under which the 
   : 147 - 1221: ## pe [_pe]  These fields contain Windows Portable
     : 148 - 1076: ## pe [_pe]  These fields contain Windows Portable
     : 149 - 143: **`pe.product`** :   Internal product name of the 
   : 150 - 19483: ## process [_process_2]  These fields contain info
     : 151 - 1034: ## process [_process_2]  These fields contain info
     : 152 - 1033: **`process.code_signature.exists`** :   Boolean to
     : 153 - 1051: **`process.code_signature.timestamp`** :   Date an
     : 154 - 1109: **`process.elf.byte_order`** :   Byte sequence of 
     : 155 - 1034: **`process.elf.header.version`** :   Version of th
     : 156 - 874: **`process.elf.sections.virtual_address`** :   ELF
     : 157 - 1077: **`process.entity_id`** :   Unique identifier for 
     : 158 - 1011: type: keyword  **`process.hash.ssdeep`** :   SSDEE
     : 159 - 1068: **`process.parent.code_signature.exists`** :   Boo
     : 160 - 1061: **`process.parent.code_signature.timestamp`** :   
     : 161 - 1021: type: keyword  example: x86-64  **`process.parent.
     : 162 - 1092: **`process.parent.elf.header.os_abi`** :   Applica
     : 163 - 1104: type: keyword  **`process.parent.elf.sections.phys
     : 164 - 1051: example: 2016-05-23T08:05:34.853Z  **`process.pare
     : 165 - 894: **`process.parent.hash.sha256`** :   SHA256 hash. 
     : 166 - 1085: **`process.parent.pe.imphash`** :   A hash of the 
     : 167 - 1044: type: long  example: 4242  format: string  **`proc
     : 168 - 1092: **`process.pe.file_version`** :   Internal version
     : 169 - 712: example: 2016-05-23T08:05:34.853Z  **`process.thre
   : 170 - 1558: ## registry [_registry]  Fields related to Windows
     : 171 - 1031: ## registry [_registry]  Fields related to Windows
     : 172 - 525: **`registry.hive`** :   Abbreviated name for the h
   : 173 - 1158: ## related [_related]  This field set is meant to 
     : 174 - 1045: ## related [_related]  This field set is meant to 
     : 175 - 111: type: ip  **`related.user`** :   All the user name
   : 176 - 2170: ## rule [_rule]  Rule fields are used to capture t
     : 177 - 1055: ## rule [_rule]  Rule fields are used to capture t
     : 178 - 1084: **`rule.license`** :   Name of the license under w
     : 179 - 27: type: keyword  example: 1.1
   : 180 - 7101: ## server [_server]  A Server is defined as the re
     : 181 - 19: ## server [_server]
     : 182 - 890: A Server is defined as the responder in a network 
     : 183 - 1034: **`server.address`** :   Some event server address
     : 184 - 1111: **`server.geo.city_name`** :   City name.  type: k
     : 185 - 1075: **`server.geo.region_iso_code`** :   Region ISO co
     : 186 - 594: **`server.packets`** :   Packets sent from the ser
     : 187 - 1028: **`server.subdomain`** :   The subdomain portion o
     : 188 - 1049: example: co.uk  **`server.user.domain`** :   Name 
     : 189 - 285: **`server.user.name`** :   Short name or login of 
   : 190 - 9426: ## service [_service]  The service fields describe
     : 191 - 951: ## service [_service]  The service fields describe
     : 192 - 1001: **`service.id`** :   Unique identifier of the runn
     : 193 - 941: **`service.node.name`** :   Name of a service node
     : 194 - 1036: **`service.origin.environment`** :   Identifies th
     : 195 - 535: type: keyword  example: d37e5ebfe0ae6c4972dbe9f017
     : 196 - 797: **`service.origin.node.name`** :   Name of a servi
     : 197 - 795: **`service.origin.type`** :   The type of the serv
     : 198 - 1036: **`service.target.environment`** :   Identifies th
     : 199 - 535: type: keyword  example: d37e5ebfe0ae6c4972dbe9f017
     : 200 - 797: **`service.target.node.name`** :   Name of a servi
     : 201 - 982: **`service.target.type`** :   The type of the serv
   : 202 - 6808: ## source [_source_2]  Source fields capture detai
     : 203 - 903: ## source [_source_2]  Source fields capture detai
     : 204 - 1105: **`source.as.number`** :   Unique number allocated
     : 205 - 1050: **`source.geo.country_name`** :   Country name.  t
     : 206 - 946: **`source.ip`** :   IP address of the source (IPv4
     : 207 - 1017: **`source.registered_domain`** :   The highest reg
     : 208 - 984: **`source.top_level_domain`** :   The effective to
     : 209 - 791: **`source.user.group.id`** :   Unique identifier f
   : 210 - 68088: ## threat [_threat]  Fields to classify events and
     : 211 - 997: ## threat [_threat]  Fields to classify events and
     : 212 - 1065: **`threat.enrichments.indicator.as.organization.na
     : 213 - 1038: **`threat.enrichments.indicator.file.attributes`**
     : 214 - 923: **`threat.enrichments.indicator.file.code_signatur
     : 215 - 1056: **`threat.enrichments.indicator.file.code_signatur
     : 216 - 1084: **`threat.enrichments.indicator.file.directory`** 
     : 217 - 1069: type: flattened  **`threat.enrichments.indicator.f
     : 218 - 1072: **`threat.enrichments.indicator.file.elf.sections`
     : 219 - 958: **`threat.enrichments.indicator.file.elf.sections.
     : 220 - 255: **`threat.enrichments.indicator.file.extension`** 
     : 221 - 971: **`threat.enrichments.indicator.file.fork_name`** 
     : 222 - 1039: **`threat.enrichments.indicator.file.group`** :   
     : 223 - 1080: **`threat.enrichments.indicator.file.mtime`** :   
     : 224 - 1078: **`threat.enrichments.indicator.file.pe.file_versi
     : 225 - 1040: **`threat.enrichments.indicator.file.target_path`*
     : 226 - 1050: **`threat.enrichments.indicator.file.x509.issuer.d
     : 227 - 1068: **`threat.enrichments.indicator.file.x509.not_befo
     : 228 - 980: example: 55FBB9C7DEBF09809D12CCAA  **`threat.enric
     : 229 - 1094: **`threat.enrichments.indicator.file.x509.subject.
     : 230 - 1041: **`threat.enrichments.indicator.geo.country_iso_co
     : 231 - 1093: **`threat.enrichments.indicator.geo.region_name`**
     : 232 - 717: example: 443  **`threat.enrichments.indicator.prov
     : 233 - 1071: **`threat.enrichments.indicator.registry.data.stri
     : 234 - 900: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
     : 235 - 921: **`threat.enrichments.indicator.url.domain`** :   
     : 236 - 1018: **`threat.enrichments.indicator.url.fragment`** : 
     : 237 - 715: **`threat.enrichments.indicator.url.password`** : 
     : 238 - 614: **`threat.enrichments.indicator.url.registered_dom
     : 239 - 613: **`threat.enrichments.indicator.url.subdomain`** :
     : 240 - 1047: **`threat.enrichments.indicator.url.top_level_doma
     : 241 - 1096: **`threat.enrichments.indicator.x509.issuer.countr
     : 242 - 1074: example: 2020-07-16 03:15:39+00:00  **`threat.enri
     : 243 - 1074: example: 55FBB9C7DEBF09809D12CCAA  **`threat.enric
     : 244 - 1091: example: Example, Inc.  **`threat.enrichments.indi
     : 245 - 1039: example: filebeat-8.0.0-2021.05.23-000011  **`thre
     : 246 - 920: **`threat.group.name`** :   The name of the group 
     : 247 - 813: **`threat.indicator.confidence`** :   Identifies t
     : 248 - 990: **`threat.indicator.file.attributes`** :   Array o
     : 249 - 875: **`threat.indicator.file.code_signature.status`** 
     : 250 - 996: **`threat.indicator.file.code_signature.trusted`**
     : 251 - 1017: **`threat.indicator.file.directory`** :   Director
     : 252 - 944: **`threat.indicator.file.elf.header.abi_version`**
     : 253 - 1084: **`threat.indicator.file.elf.sections`** :   An ar
     : 254 - 1011: format: string  **`threat.indicator.file.elf.secti
     : 255 - 1049: **`threat.indicator.file.fork_name`** :   A fork i
     : 256 - 1061: **`threat.indicator.file.hash.md5`** :   MD5 hash.
     : 257 - 897: **`threat.indicator.file.owner`** :   File owner’s
     : 258 - 1031: **`threat.indicator.file.pe.imphash`** :   A hash 
     : 259 - 1027: **`threat.indicator.file.type`** :   File type (fi
     : 260 - 1034: **`threat.indicator.file.x509.issuer.locality`** :
     : 261 - 1027: **`threat.indicator.file.x509.public_key_curve`** 
     : 262 - 1090: **`threat.indicator.file.x509.subject.common_name`
     : 263 - 830: type: keyword  example: 3  **`threat.indicator.fir
     : 264 - 1032: **`threat.indicator.geo.name`** :   User-defined d
     : 265 - 932: **`threat.indicator.last_seen`** :   The date and 
     : 266 - 1009: **`threat.indicator.registry.data.bytes`** :   Ori
     : 267 - 868: **`threat.indicator.registry.hive`** :   Abbreviat
     : 268 - 790: **`threat.indicator.type`** :   Type of indicator 
     : 269 - 945: **`threat.indicator.url.extension`** :   The field
     : 270 - 770: **`threat.indicator.url.original`** :   Unmodified
     : 271 - 972: **`threat.indicator.url.query`** :   The query fie
     : 272 - 601: **`threat.indicator.url.subdomain`** :   The subdo
     : 273 - 999: **`threat.indicator.url.top_level_domain`** :   Th
     : 274 - 1048: **`threat.indicator.x509.issuer.country`** :   Lis
     : 275 - 1001: **`threat.indicator.x509.not_before`** :   Time at
     : 276 - 991: **`threat.indicator.x509.signature_algorithm`** : 
     : 277 - 1080: **`threat.indicator.x509.subject.organizational_un
     : 278 - 931: example: AdFind  **`threat.software.platforms`** :
     : 279 - 1048: **`threat.tactic.id`** :   The id of tactic used b
     : 280 - 909: example: Command and Scripting Interpreter  **`thr
     : 281 - 285: **`threat.technique.subtechnique.reference`** :   
   : 282 - 14483: ## tls [_tls]  Fields related to a TLS connection.
     : 283 - 859: ## tls [_tls]  Fields related to a TLS connection.
     : 284 - 1048: **`tls.client.hash.md5`** :   Certificate fingerpr
     : 285 - 988: example: CN=Example Root CA, OU=Infrastructure Tea
     : 286 - 1076: **`tls.client.supported_ciphers`** :   Array of ci
     : 287 - 1013: **`tls.client.x509.issuer.organization`** :   List
     : 288 - 1037: **`tls.client.x509.public_key_exponent`** :   Expo
     : 289 - 1072: **`tls.client.x509.subject.distinguished_name`** :
     : 290 - 951: **`tls.next_protocol`** :   String indicating the 
     : 291 - 1026: **`tls.server.hash.md5`** :   Certificate fingerpr
     : 292 - 987: example: CN=Example Root CA, OU=Infrastructure Tea
     : 293 - 1028: **`tls.server.x509.issuer.common_name`** :   List 
     : 294 - 1076: **`tls.server.x509.not_after`** :   Time at which 
     : 295 - 1091: example: 55FBB9C7DEBF09809D12CCAA  **`tls.server.x
     : 296 - 968: type: keyword  **`tls.server.x509.subject.state_or
     : 297 - 235: **`transaction.id`** :   Unique identifier of the 
   : 298 - 4143: ## url [_url]  URL fields provide support for comp
     : 299 - 1005: ## url [_url]  URL fields provide support for comp
     : 300 - 1079: **`url.fragment`** :   Portion of the url after th
     : 301 - 951: example: 443  format: string  **`url.query`** :   
     : 302 - 1038: **`url.subdomain`** :   The subdomain portion of a
     : 303 - 62: **`url.username`** :   Username of the request.  t
   : 304 - 5476: ## user [_user_2]  The user fields describe inform
     : 305 - 931: ## user [_user_2]  The user fields describe inform
     : 306 - 1089: **`user.changes.hash`** :   Unique user hash to co
     : 307 - 1088: **`user.effective.full_name.text`** :   type: matc
     : 308 - 1040: **`user.full_name`** :   User’s full name, if avai
     : 309 - 1094: **`user.target.domain`** :   Name of the directory
     : 310 - 224: type: keyword  example: a.einstein  **`user.target
   : 311 - 1936: ## user_agent [_user_agent]  The user_agent fields
     : 312 - 1043: ## user_agent [_user_agent]  The user_agent fields
     : 313 - 891: **`user_agent.os.name`** :   Operating system name
   : 314 - 1178: ## vlan [_vlan]  The VLAN fields are used to ident
     : 315 - 992: ## vlan [_vlan]  The VLAN fields are used to ident
     : 316 - 184: **`vlan.id`** :   VLAN ID as reported by the obser
   : 317 - 3648: ## vulnerability [_vulnerability]  The vulnerabili
     : 318 - 975: ## vulnerability [_vulnerability]  The vulnerabili
     : 319 - 890: **`vulnerability.enumeration`** :   The type of id
     : 320 - 1005: **`vulnerability.score.base`** :   Scores can rang
     : 321 - 772: **`vulnerability.score.version`** :   The National
   : 322 - 4075: ## x509 [_x509]  This implements the common core f
     : 323 - 1041: ## x509 [_x509]  This implements the common core f
     : 324 - 1061: **`x509.issuer.country`** :   List of country © co
     : 325 - 1026: **`x509.public_key_algorithm`** :   Algorithm used
     : 326 - 941: **`x509.subject.common_name`** :   List of common 