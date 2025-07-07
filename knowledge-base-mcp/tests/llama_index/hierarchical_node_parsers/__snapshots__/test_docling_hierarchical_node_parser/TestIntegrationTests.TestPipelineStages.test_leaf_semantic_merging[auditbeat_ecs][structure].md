 : 0 - 13: mapped_pages:
 : 1 - 82: - https://www.elastic.co/guide/en/beats/auditbeat/
 : 2 - 34: # ECS fields [exported-fields-ecs]
 : 3 - 124: This section defines Elastic Common Schema (ECS) f
 : 4 - 275: This is an exhaustive list, and fields listed here
 : 5 - 43: See the ECS reference for more information.
 : 6 - 342: **`@timestamp`** :   Date/time when the event orig
 : 7 - 10: type: date
 : 8 - 33: example: 2016-05-23T08:05:34.853Z
 : 9 - 14: required: True
 : 10 - 192: **`labels`** :   Custom key/value pairs. Can be us
 : 11 - 12: type: object
 : 12 - 56: example: {"application": "foo-bar", "env": "produc
 : 13 - 317: **`message`** :   For log events the message field
 : 14 - 21: type: match_only_text
 : 15 - 20: example: Hello World
 : 16 - 55: **`tags`** :   List of keywords used to tag each e
 : 17 - 13: type: keyword
 : 18 - 31: example: ["production", "env2"]
 : 19 - 17: ## agent [_agent]
 : 20 - 364: The agent fields contain the data about the softwa
 : 21 - 196: **`agent.build.original`** :   Extended build info
 : 22 - 13: type: keyword
 : 23 - 135: example: metricbeat version 7.6.0 (amd64), libbeat
 : 24 - 147: **`agent.ephemeral_id`** :   Ephemeral identifier 
 : 25 - 13: type: keyword
 : 26 - 17: example: 8a4f500f
 : 27 - 109: **`agent.id`** :   Unique identifier of this agent
 : 28 - 13: type: keyword
 : 29 - 17: example: 8a4f500d
 : 30 - 320: **`agent.name`** :   Custom name of the agent. Thi
 : 31 - 13: type: keyword
 : 32 - 12: example: foo
 : 33 - 230: **`agent.type`** :   Type of the agent. The agent 
 : 34 - 13: type: keyword
 : 35 - 17: example: filebeat
 : 36 - 45: **`agent.version`** :   Version of the agent.
 : 37 - 13: type: keyword
 : 38 - 18: example: 6.0.0-rc2
 : 39 - 11: ## as [_as]
 : 40 - 271: An autonomous system (AS) is a collection of conne
 : 41 - 154: **`as.number`** :   Unique number allocated to the
 : 42 - 10: type: long
 : 43 - 14: example: 15169
 : 44 - 49: **`as.organization.name`** :   Organization name.
 : 45 - 13: type: keyword
 : 46 - 19: example: Google LLC
 : 47 - 57: **`as.organization.name.text`** :   type: match_on
 : 48 - 19: ## client [_client]
 : 49 - 896: A client is defined as the initiator of a network 
 : 50 - 290: **`client.address`** :   Some event client address
 : 51 - 13: type: keyword
 : 52 - 161: **`client.as.number`** :   Unique number allocated
 : 53 - 10: type: long
 : 54 - 14: example: 15169
 : 55 - 56: **`client.as.organization.name`** :   Organization
 : 56 - 13: type: keyword
 : 57 - 19: example: Google LLC
 : 58 - 64: **`client.as.organization.name.text`** :   type: m
 : 59 - 64: **`client.bytes`** :   Bytes sent from the client 
 : 60 - 10: type: long
 : 61 - 12: example: 184
 : 62 - 13: format: bytes
 : 63 - 228: **`client.domain`** :   The domain name of the cli
 : 64 - 13: type: keyword
 : 65 - 24: example: foo.example.com
 : 66 - 41: **`client.geo.city_name`** :   City name.
 : 67 - 13: type: keyword
 : 68 - 17: example: Montreal
 : 69 - 82: **`client.geo.continent_code`** :   Two-letter cod
 : 70 - 13: type: keyword
 : 71 - 11: example: NA
 : 72 - 58: **`client.geo.continent_name`** :   Name of the co
 : 73 - 13: type: keyword
 : 74 - 22: example: North America
 : 75 - 55: **`client.geo.country_iso_code`** :   Country ISO 
 : 76 - 13: type: keyword
 : 77 - 11: example: CA
 : 78 - 47: **`client.geo.country_name`** :   Country name.
 : 79 - 13: type: keyword
 : 80 - 15: example: Canada
 : 81 - 53: **`client.geo.location`** :   Longitude and latitu
 : 82 - 15: type: geo_point
 : 83 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 84 - 269: **`client.geo.name`** :   User-defined description
 : 85 - 13: type: keyword
 : 86 - 18: example: boston-dc
 : 87 - 198: **`client.geo.postal_code`** :   Postal code assoc
 : 88 - 13: type: keyword
 : 89 - 14: example: 94040
 : 90 - 53: **`client.geo.region_iso_code`** :   Region ISO co
 : 91 - 13: type: keyword
 : 92 - 14: example: CA-QC
 : 93 - 45: **`client.geo.region_name`** :   Region name.
 : 94 - 13: type: keyword
 : 95 - 15: example: Quebec
 : 96 - 89: **`client.geo.timezone`** :   The time zone of the
 : 97 - 13: type: keyword
 : 98 - 39: example: America/Argentina/Buenos_Aires
 : 99 - 60: **`client.ip`** :   IP address of the client (IPv4
 : 100 - 8: type: ip
 : 101 - 280: **`client.mac`** :   MAC address of the client. Th
 : 102 - 13: type: keyword
 : 103 - 26: example: 00-00-5E-00-53-23
 : 104 - 174: **`client.nat.ip`** :   Translated IP of source ba
 : 105 - 8: type: ip
 : 106 - 178: **`client.nat.port`** :   Translated port of sourc
 : 107 - 10: type: long
 : 108 - 14: format: string
 : 109 - 68: **`client.packets`** :   Packets sent from the cli
 : 110 - 10: type: long
 : 111 - 11: example: 12
 : 112 - 41: **`client.port`** :   Port of the client.
 : 113 - 10: type: long
 : 114 - 14: format: string
 : 115 - 391: **`client.registered_domain`** :   The highest reg
 : 116 - 13: type: keyword
 : 117 - 20: example: example.com
 : 118 - 557: **`client.subdomain`** :   The subdomain portion o
 : 119 - 13: type: keyword
 : 120 - 13: example: east
 : 121 - 424: **`client.top_level_domain`** :   The effective to
 : 122 - 13: type: keyword
 : 123 - 14: example: co.uk
 : 124 - 129: **`client.user.domain`** :   Name of the directory
 : 125 - 13: type: keyword
 : 126 - 47: **`client.user.email`** :   User email address.
 : 127 - 13: type: keyword
 : 128 - 63: **`client.user.full_name`** :   User’s full name, 
 : 129 - 13: type: keyword
 : 130 - 24: example: Albert Einstein
 : 131 - 58: **`client.user.full_name.text`** :   type: match_o
 : 132 - 136: **`client.user.group.domain`** :   Name of the dir
 : 133 - 13: type: keyword
 : 134 - 86: **`client.user.group.id`** :   Unique identifier f
 : 135 - 13: type: keyword
 : 136 - 51: **`client.user.group.name`** :   Name of the group
 : 137 - 13: type: keyword
 : 138 - 187: **`client.user.hash`** :   Unique user hash to cor
 : 139 - 13: type: keyword
 : 140 - 55: **`client.user.id`** :   Unique identifier of the 
 : 141 - 13: type: keyword
 : 142 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 143 - 59: **`client.user.name`** :   Short name or login of 
 : 144 - 13: type: keyword
 : 145 - 19: example: a.einstein
 : 146 - 53: **`client.user.name.text`** :   type: match_only_t
 : 147 - 73: **`client.user.roles`** :   Array of user roles at
 : 148 - 13: type: keyword
 : 149 - 43: example: ["kibana_admin", "reporting_user"]
 : 150 - 17: ## cloud [_cloud]
 : 151 - 73: Fields related to the cloud or infrastructure the 
 : 152 - 205: **`cloud.account.id`** :   The cloud account or or
 : 153 - 13: type: keyword
 : 154 - 21: example: 666777888999
 : 155 - 186: **`cloud.account.name`** :   The cloud account nam
 : 156 - 13: type: keyword
 : 157 - 20: example: elastic-dev
 : 158 - 104: **`cloud.availability_zone`** :   Availability zon
 : 159 - 13: type: keyword
 : 160 - 19: example: us-east-1c
 : 161 - 60: **`cloud.instance.id`** :   Instance ID of the hos
 : 162 - 13: type: keyword
 : 163 - 28: example: i-1234567890abcdef0
 : 164 - 64: **`cloud.instance.name`** :   Instance name of the
 : 165 - 13: type: keyword
 : 166 - 62: **`cloud.machine.type`** :   Machine type of the h
 : 167 - 13: type: keyword
 : 168 - 18: example: t2.medium
 : 169 - 212: **`cloud.origin.account.id`** :   The cloud accoun
 : 170 - 13: type: keyword
 : 171 - 21: example: 666777888999
 : 172 - 193: **`cloud.origin.account.name`** :   The cloud acco
 : 173 - 13: type: keyword
 : 174 - 20: example: elastic-dev
 : 175 - 111: **`cloud.origin.availability_zone`** :   Availabil
 : 176 - 13: type: keyword
 : 177 - 19: example: us-east-1c
 : 178 - 67: **`cloud.origin.instance.id`** :   Instance ID of 
 : 179 - 13: type: keyword
 : 180 - 28: example: i-1234567890abcdef0
 : 181 - 71: **`cloud.origin.instance.name`** :   Instance name
 : 182 - 13: type: keyword
 : 183 - 69: **`cloud.origin.machine.type`** :   Machine type o
 : 184 - 13: type: keyword
 : 185 - 18: example: t2.medium
 : 186 - 116: **`cloud.origin.project.id`** :   The cloud projec
 : 187 - 13: type: keyword
 : 188 - 19: example: my-project
 : 189 - 116: **`cloud.origin.project.name`** :   The cloud proj
 : 190 - 13: type: keyword
 : 191 - 19: example: my project
 : 192 - 112: **`cloud.origin.provider`** :   Name of the cloud 
 : 193 - 13: type: keyword
 : 194 - 12: example: aws
 : 195 - 89: **`cloud.origin.region`** :   Region in which this
 : 196 - 13: type: keyword
 : 197 - 18: example: us-east-1
 : 198 - 276: **`cloud.origin.service.name`** :   The cloud serv
 : 199 - 13: type: keyword
 : 200 - 15: example: lambda
 : 201 - 109: **`cloud.project.id`** :   The cloud project ident
 : 202 - 13: type: keyword
 : 203 - 19: example: my-project
 : 204 - 109: **`cloud.project.name`** :   The cloud project nam
 : 205 - 13: type: keyword
 : 206 - 19: example: my project
 : 207 - 105: **`cloud.provider`** :   Name of the cloud provide
 : 208 - 13: type: keyword
 : 209 - 12: example: aws
 : 210 - 82: **`cloud.region`** :   Region in which this host, 
 : 211 - 13: type: keyword
 : 212 - 18: example: us-east-1
 : 213 - 269: **`cloud.service.name`** :   The cloud service nam
 : 214 - 13: type: keyword
 : 215 - 15: example: lambda
 : 216 - 212: **`cloud.target.account.id`** :   The cloud accoun
 : 217 - 13: type: keyword
 : 218 - 21: example: 666777888999
 : 219 - 193: **`cloud.target.account.name`** :   The cloud acco
 : 220 - 13: type: keyword
 : 221 - 20: example: elastic-dev
 : 222 - 111: **`cloud.target.availability_zone`** :   Availabil
 : 223 - 13: type: keyword
 : 224 - 19: example: us-east-1c
 : 225 - 67: **`cloud.target.instance.id`** :   Instance ID of 
 : 226 - 13: type: keyword
 : 227 - 28: example: i-1234567890abcdef0
 : 228 - 71: **`cloud.target.instance.name`** :   Instance name
 : 229 - 13: type: keyword
 : 230 - 69: **`cloud.target.machine.type`** :   Machine type o
 : 231 - 13: type: keyword
 : 232 - 18: example: t2.medium
 : 233 - 116: **`cloud.target.project.id`** :   The cloud projec
 : 234 - 13: type: keyword
 : 235 - 19: example: my-project
 : 236 - 116: **`cloud.target.project.name`** :   The cloud proj
 : 237 - 13: type: keyword
 : 238 - 19: example: my project
 : 239 - 112: **`cloud.target.provider`** :   Name of the cloud 
 : 240 - 13: type: keyword
 : 241 - 12: example: aws
 : 242 - 89: **`cloud.target.region`** :   Region in which this
 : 243 - 13: type: keyword
 : 244 - 18: example: us-east-1
 : 245 - 276: **`cloud.target.service.name`** :   The cloud serv
 : 246 - 13: type: keyword
 : 247 - 15: example: lambda
 : 248 - 35: ## code_signature [_code_signature]
 : 249 - 62: These fields contain information about binary code
 : 250 - 222: **`code_signature.digest_algorithm`** :   The hash
 : 251 - 13: type: keyword
 : 252 - 15: example: sha256
 : 253 - 77: **`code_signature.exists`** :   Boolean to capture
 : 254 - 13: type: boolean
 : 255 - 13: example: true
 : 256 - 193: **`code_signature.signing_id`** :   The identifier
 : 257 - 13: type: keyword
 : 258 - 28: example: com.apple.xpc.proxy
 : 259 - 256: **`code_signature.status`** :   Additional informa
 : 260 - 13: type: keyword
 : 261 - 29: example: ERROR_UNTRUSTED_ROOT
 : 262 - 69: **`code_signature.subject_name`** :   Subject name
 : 263 - 13: type: keyword
 : 264 - 30: example: Microsoft Corporation
 : 265 - 186: **`code_signature.team_id`** :   The team identifi
 : 266 - 13: type: keyword
 : 267 - 19: example: EQHXZ8M8AV
 : 268 - 98: **`code_signature.timestamp`** :   Date and time w
 : 269 - 10: type: date
 : 270 - 29: example: 2021-01-01T12:10:30Z
 : 271 - 229: **`code_signature.trusted`** :   Stores the trust 
 : 272 - 13: type: boolean
 : 273 - 13: example: true
 : 274 - 164: **`code_signature.valid`** :   Boolean to capture 
 : 275 - 13: type: boolean
 : 276 - 13: example: true
 : 277 - 25: ## container [_container]
 : 278 - 178: Container fields are used for meta information abo
 : 279 - 142: **`container.cpu.usage`** :   Percent CPU used whi
 : 280 - 18: type: scaled_float
 : 281 - 149: **`container.disk.read.bytes`** :   The total numb
 : 282 - 10: type: long
 : 283 - 153: **`container.disk.write.bytes`** :   The total num
 : 284 - 10: type: long
 : 285 - 43: **`container.id`** :   Unique container id.
 : 286 - 13: type: keyword
 : 287 - 76: **`container.image.name`** :   Name of the image t
 : 288 - 13: type: keyword
 : 289 - 51: **`container.image.tag`** :   Container image tags
 : 290 - 13: type: keyword
 : 291 - 40: **`container.labels`** :   Image labels.
 : 292 - 12: type: object
 : 293 - 105: **`container.memory.usage`** :   Memory usage perc
 : 294 - 18: type: scaled_float
 : 295 - 40: **`container.name`** :   Container name.
 : 296 - 13: type: keyword
 : 297 - 154: **`container.network.egress.bytes`** :   The numbe
 : 298 - 10: type: long
 : 299 - 155: **`container.network.ingress.bytes`** :   The numb
 : 300 - 10: type: long
 : 301 - 60: **`container.runtime`** :   Runtime managing this 
 : 302 - 13: type: keyword
 : 303 - 15: example: docker
 : 304 - 29: ## data_stream [_data_stream]
 : 305 - 863: The data_stream fields take part in defining the n
 : 306 - 537: **`data_stream.dataset`** :   The field can contai
 : 307 - 22: type: constant_keyword
 : 308 - 21: example: nginx.access
 : 309 - 507: **`data_stream.namespace`** :   A user defined nam
 : 310 - 22: type: constant_keyword
 : 311 - 19: example: production
 : 312 - 186: **`data_stream.type`** :   An overarching type for
 : 313 - 22: type: constant_keyword
 : 314 - 13: example: logs
 : 315 - 31: ## destination [_destination_2]
 : 316 - 580: Destination fields capture details about the recei
 : 317 - 300: **`destination.address`** :   Some event destinati
 : 318 - 13: type: keyword
 : 319 - 166: **`destination.as.number`** :   Unique number allo
 : 320 - 10: type: long
 : 321 - 14: example: 15169
 : 322 - 61: **`destination.as.organization.name`** :   Organiz
 : 323 - 13: type: keyword
 : 324 - 19: example: Google LLC
 : 325 - 69: **`destination.as.organization.name.text`** :   ty
 : 326 - 74: **`destination.bytes`** :   Bytes sent from the de
 : 327 - 10: type: long
 : 328 - 12: example: 184
 : 329 - 13: format: bytes
 : 330 - 238: **`destination.domain`** :   The domain name of th
 : 331 - 13: type: keyword
 : 332 - 24: example: foo.example.com
 : 333 - 46: **`destination.geo.city_name`** :   City name.
 : 334 - 13: type: keyword
 : 335 - 17: example: Montreal
 : 336 - 87: **`destination.geo.continent_code`** :   Two-lette
 : 337 - 13: type: keyword
 : 338 - 11: example: NA
 : 339 - 63: **`destination.geo.continent_name`** :   Name of t
 : 340 - 13: type: keyword
 : 341 - 22: example: North America
 : 342 - 60: **`destination.geo.country_iso_code`** :   Country
 : 343 - 13: type: keyword
 : 344 - 11: example: CA
 : 345 - 52: **`destination.geo.country_name`** :   Country nam
 : 346 - 13: type: keyword
 : 347 - 15: example: Canada
 : 348 - 58: **`destination.geo.location`** :   Longitude and l
 : 349 - 15: type: geo_point
 : 350 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 351 - 274: **`destination.geo.name`** :   User-defined descri
 : 352 - 13: type: keyword
 : 353 - 18: example: boston-dc
 : 354 - 203: **`destination.geo.postal_code`** :   Postal code 
 : 355 - 13: type: keyword
 : 356 - 14: example: 94040
 : 357 - 58: **`destination.geo.region_iso_code`** :   Region I
 : 358 - 13: type: keyword
 : 359 - 14: example: CA-QC
 : 360 - 50: **`destination.geo.region_name`** :   Region name.
 : 361 - 13: type: keyword
 : 362 - 15: example: Quebec
 : 363 - 94: **`destination.geo.timezone`** :   The time zone o
 : 364 - 13: type: keyword
 : 365 - 39: example: America/Argentina/Buenos_Aires
 : 366 - 70: **`destination.ip`** :   IP address of the destina
 : 367 - 8: type: ip
 : 368 - 290: **`destination.mac`** :   MAC address of the desti
 : 369 - 13: type: keyword
 : 370 - 26: example: 00-00-5E-00-53-23
 : 371 - 166: **`destination.nat.ip`** :   Translated ip of dest
 : 372 - 8: type: ip
 : 373 - 145: **`destination.nat.port`** :   Port the source ses
 : 374 - 10: type: long
 : 375 - 14: format: string
 : 376 - 78: **`destination.packets`** :   Packets sent from th
 : 377 - 10: type: long
 : 378 - 11: example: 12
 : 379 - 51: **`destination.port`** :   Port of the destination
 : 380 - 10: type: long
 : 381 - 14: format: string
 : 382 - 401: **`destination.registered_domain`** :   The highes
 : 383 - 13: type: keyword
 : 384 - 20: example: example.com
 : 385 - 562: **`destination.subdomain`** :   The subdomain port
 : 386 - 13: type: keyword
 : 387 - 13: example: east
 : 388 - 429: **`destination.top_level_domain`** :   The effecti
 : 389 - 13: type: keyword
 : 390 - 14: example: co.uk
 : 391 - 134: **`destination.user.domain`** :   Name of the dire
 : 392 - 13: type: keyword
 : 393 - 52: **`destination.user.email`** :   User email addres
 : 394 - 13: type: keyword
 : 395 - 68: **`destination.user.full_name`** :   User’s full n
 : 396 - 13: type: keyword
 : 397 - 24: example: Albert Einstein
 : 398 - 63: **`destination.user.full_name.text`** :   type: ma
 : 399 - 141: **`destination.user.group.domain`** :   Name of th
 : 400 - 13: type: keyword
 : 401 - 91: **`destination.user.group.id`** :   Unique identif
 : 402 - 13: type: keyword
 : 403 - 56: **`destination.user.group.name`** :   Name of the 
 : 404 - 13: type: keyword
 : 405 - 192: **`destination.user.hash`** :   Unique user hash t
 : 406 - 13: type: keyword
 : 407 - 60: **`destination.user.id`** :   Unique identifier of
 : 408 - 13: type: keyword
 : 409 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 410 - 64: **`destination.user.name`** :   Short name or logi
 : 411 - 13: type: keyword
 : 412 - 19: example: a.einstein
 : 413 - 58: **`destination.user.name.text`** :   type: match_o
 : 414 - 78: **`destination.user.roles`** :   Array of user rol
 : 415 - 13: type: keyword
 : 416 - 43: example: ["kibana_admin", "reporting_user"]
 : 417 - 13: ## dll [_dll]
 : 418 - 88: These fields contain information about code librar
 : 419 - 312: Many operating systems refer to "shared code libra
 : 420 - 226: **`dll.code_signature.digest_algorithm`** :   The 
 : 421 - 13: type: keyword
 : 422 - 15: example: sha256
 : 423 - 81: **`dll.code_signature.exists`** :   Boolean to cap
 : 424 - 13: type: boolean
 : 425 - 13: example: true
 : 426 - 197: **`dll.code_signature.signing_id`** :   The identi
 : 427 - 13: type: keyword
 : 428 - 28: example: com.apple.xpc.proxy
 : 429 - 260: **`dll.code_signature.status`** :   Additional inf
 : 430 - 13: type: keyword
 : 431 - 29: example: ERROR_UNTRUSTED_ROOT
 : 432 - 73: **`dll.code_signature.subject_name`** :   Subject 
 : 433 - 13: type: keyword
 : 434 - 30: example: Microsoft Corporation
 : 435 - 190: **`dll.code_signature.team_id`** :   The team iden
 : 436 - 13: type: keyword
 : 437 - 19: example: EQHXZ8M8AV
 : 438 - 102: **`dll.code_signature.timestamp`** :   Date and ti
 : 439 - 10: type: date
 : 440 - 29: example: 2021-01-01T12:10:30Z
 : 441 - 233: **`dll.code_signature.trusted`** :   Stores the tr
 : 442 - 13: type: boolean
 : 443 - 13: example: true
 : 444 - 168: **`dll.code_signature.valid`** :   Boolean to capt
 : 445 - 13: type: boolean
 : 446 - 13: example: true
 : 447 - 32: **`dll.hash.md5`** :   MD5 hash.
 : 448 - 13: type: keyword
 : 449 - 34: **`dll.hash.sha1`** :   SHA1 hash.
 : 450 - 13: type: keyword
 : 451 - 38: **`dll.hash.sha256`** :   SHA256 hash.
 : 452 - 13: type: keyword
 : 453 - 38: **`dll.hash.sha512`** :   SHA512 hash.
 : 454 - 13: type: keyword
 : 455 - 38: **`dll.hash.ssdeep`** :   SSDEEP hash.
 : 456 - 13: type: keyword
 : 457 - 92: **`dll.name`** :   Name of the library. This gener
 : 458 - 13: type: keyword
 : 459 - 21: example: kernel32.dll
 : 460 - 49: **`dll.path`** :   Full file path of the library.
 : 461 - 13: type: keyword
 : 462 - 41: example: C:\Windows\System32\kernel32.dll
 : 463 - 67: **`dll.pe.architecture`** :   CPU architecture tar
 : 464 - 13: type: keyword
 : 465 - 12: example: x64
 : 466 - 85: **`dll.pe.company`** :   Internal company name of 
 : 467 - 13: type: keyword
 : 468 - 30: example: Microsoft Corporation
 : 469 - 88: **`dll.pe.description`** :   Internal description 
 : 470 - 13: type: keyword
 : 471 - 14: example: Paint
 : 472 - 85: **`dll.pe.file_version`** :   Internal version of 
 : 473 - 13: type: keyword
 : 474 - 23: example: 6.3.9600.17415
 : 475 - 357: **`dll.pe.imphash`** :   A hash of the imports in 
 : 476 - 13: type: keyword
 : 477 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 478 - 88: **`dll.pe.original_file_name`** :   Internal name 
 : 479 - 13: type: keyword
 : 480 - 20: example: MSPAINT.EXE
 : 481 - 85: **`dll.pe.product`** :   Internal product name of 
 : 482 - 13: type: keyword
 : 483 - 45: example: Microsoft® Windows® Operating System
 : 484 - 13: ## dns [_dns]
 : 485 - 300: Fields describing DNS queries and answers. DNS eve
 : 486 - 512: **`dns.answers`** :   An array containing an objec
 : 487 - 12: type: object
 : 488 - 84: **`dns.answers.class`** :   The class of DNS data 
 : 489 - 13: type: keyword
 : 490 - 11: example: IN
 : 491 - 139: **`dns.answers.data`** :   The data describing the
 : 492 - 13: type: keyword
 : 493 - 20: example: 10.10.10.10
 : 494 - 267: **`dns.answers.name`** :   The domain name to whic
 : 495 - 13: type: keyword
 : 496 - 24: example: www.example.com
 : 497 - 178: **`dns.answers.ttl`** :   The time interval in sec
 : 498 - 10: type: long
 : 499 - 12: example: 180
 : 500 - 78: **`dns.answers.type`** :   The type of data contai
 : 501 - 13: type: keyword
 : 502 - 14: example: CNAME
 : 503 - 111: **`dns.header_flags`** :   Array of 2 letter DNS h
 : 504 - 13: type: keyword
 : 505 - 21: example: ["RD", "RA"]
 : 506 - 134: **`dns.id`** :   The DNS packet identifier assigne
 : 507 - 13: type: keyword
 : 508 - 14: example: 62111
 : 509 - 170: **`dns.op_code`** :   The DNS operation code that 
 : 510 - 13: type: keyword
 : 511 - 14: example: QUERY
 : 512 - 64: **`dns.question.class`** :   The class of records 
 : 513 - 13: type: keyword
 : 514 - 11: example: IN
 : 515 - 337: **`dns.question.name`** :   The name being queried
 : 516 - 13: type: keyword
 : 517 - 24: example: www.example.com
 : 518 - 390: **`dns.question.registered_domain`** :   The highe
 : 519 - 13: type: keyword
 : 520 - 20: example: example.com
 : 521 - 250: **`dns.question.subdomain`** :   The subdomain is 
 : 522 - 13: type: keyword
 : 523 - 12: example: www
 : 524 - 430: **`dns.question.top_level_domain`** :   The effect
 : 525 - 13: type: keyword
 : 526 - 14: example: co.uk
 : 527 - 61: **`dns.question.type`** :   The type of record bei
 : 528 - 13: type: keyword
 : 529 - 13: example: AAAA
 : 530 - 337: **`dns.resolved_ip`** :   Array containing all IPs
 : 531 - 8: type: ip
 : 532 - 39: example: ["10.10.10.10", "10.10.10.11"]
 : 533 - 50: **`dns.response_code`** :   The DNS response code.
 : 534 - 13: type: keyword
 : 535 - 16: example: NOERROR
 : 536 - 402: **`dns.type`** :   The type of DNS event captured,
 : 537 - 13: type: keyword
 : 538 - 15: example: answer
 : 539 - 13: ## ecs [_ecs]
 : 540 - 33: Meta-information specific to ECS.
 : 541 - 289: **`ecs.version`** :   ECS version this event confo
 : 542 - 13: type: keyword
 : 543 - 14: example: 1.0.0
 : 544 - 14: required: True
 : 545 - 13: ## elf [_elf]
 : 546 - 69: These fields contain Linux Executable Linkable For
 : 547 - 64: **`elf.architecture`** :   Machine architecture of
 : 548 - 13: type: keyword
 : 549 - 15: example: x86-64
 : 550 - 51: **`elf.byte_order`** :   Byte sequence of ELF file
 : 551 - 13: type: keyword
 : 552 - 22: example: Little Endian
 : 553 - 48: **`elf.cpu_type`** :   CPU type of the ELF file.
 : 554 - 13: type: keyword
 : 555 - 14: example: Intel
 : 556 - 160: **`elf.creation_date`** :   Extracted when possibl
 : 557 - 10: type: date
 : 558 - 63: **`elf.exports`** :   List of exported element nam
 : 559 - 15: type: flattened
 : 560 - 87: **`elf.header.abi_version`** :   Version of the EL
 : 561 - 13: type: keyword
 : 562 - 56: **`elf.header.class`** :   Header class of the ELF
 : 563 - 13: type: keyword
 : 564 - 55: **`elf.header.data`** :   Data table of the ELF he
 : 565 - 13: type: keyword
 : 566 - 66: **`elf.header.entrypoint`** :   Header entrypoint 
 : 567 - 10: type: long
 : 568 - 14: format: string
 : 569 - 65: **`elf.header.object_version`** :   "0x1" for orig
 : 570 - 13: type: keyword
 : 571 - 79: **`elf.header.os_abi`** :   Application Binary Int
 : 572 - 13: type: keyword
 : 573 - 54: **`elf.header.type`** :   Header type of the ELF f
 : 574 - 13: type: keyword
 : 575 - 55: **`elf.header.version`** :   Version of the ELF he
 : 576 - 13: type: keyword
 : 577 - 63: **`elf.imports`** :   List of imported element nam
 : 578 - 15: type: flattened
 : 579 - 191: **`elf.sections`** :   An array containing an obje
 : 580 - 12: type: nested
 : 581 - 79: **`elf.sections.chi2`** :   Chi-square probability
 : 582 - 10: type: long
 : 583 - 14: format: number
 : 584 - 76: **`elf.sections.entropy`** :   Shannon entropy cal
 : 585 - 10: type: long
 : 586 - 14: format: number
 : 587 - 52: **`elf.sections.flags`** :   ELF Section List flag
 : 588 - 13: type: keyword
 : 589 - 50: **`elf.sections.name`** :   ELF Section List name.
 : 590 - 13: type: keyword
 : 591 - 63: **`elf.sections.physical_offset`** :   ELF Section
 : 592 - 13: type: keyword
 : 593 - 68: **`elf.sections.physical_size`** :   ELF Section L
 : 594 - 10: type: long
 : 595 - 13: format: bytes
 : 596 - 50: **`elf.sections.type`** :   ELF Section List type.
 : 597 - 13: type: keyword
 : 598 - 72: **`elf.sections.virtual_address`** :   ELF Section
 : 599 - 10: type: long
 : 600 - 14: format: string
 : 601 - 66: **`elf.sections.virtual_size`** :   ELF Section Li
 : 602 - 10: type: long
 : 603 - 14: format: string
 : 604 - 191: **`elf.segments`** :   An array containing an obje
 : 605 - 12: type: nested
 : 606 - 60: **`elf.segments.sections`** :   ELF object segment
 : 607 - 13: type: keyword
 : 608 - 52: **`elf.segments.type`** :   ELF object segment typ
 : 609 - 13: type: keyword
 : 610 - 80: **`elf.shared_libraries`** :   List of shared libr
 : 611 - 13: type: keyword
 : 612 - 57: **`elf.telfhash`** :   telfhash symbol hash for EL
 : 613 - 13: type: keyword
 : 614 - 17: ## error [_error]
 : 615 - 154: These fields can represent errors of any kind. Use
 : 616 - 53: **`error.code`** :   Error code describing the err
 : 617 - 13: type: keyword
 : 618 - 51: **`error.id`** :   Unique identifier for the error
 : 619 - 13: type: keyword
 : 620 - 38: **`error.message`** :   Error message.
 : 621 - 21: type: match_only_text
 : 622 - 72: **`error.stack_trace`** :   The stack trace of thi
 : 623 - 14: type: wildcard
 : 624 - 54: **`error.stack_trace.text`** :   type: match_only_
 : 625 - 88: **`error.type`** :   The type of the error, for ex
 : 626 - 13: type: keyword
 : 627 - 39: example: java.lang.NullPointerException
 : 628 - 17: ## event [_event]
 : 629 - 749: The event fields are used for context information 
 : 630 - 259: **`event.action`** :   The action captured by the 
 : 631 - 13: type: keyword
 : 632 - 29: example: user-password-change
 : 633 - 1107: **`event.agent_id_status`** :   Agents are normall
 : 634 - 13: type: keyword
 : 635 - 17: example: verified
 : 636 - 488: **`event.category`** :   This is one of four ECS C
 : 637 - 13: type: keyword
 : 638 - 23: example: authentication
 : 639 - 251: **`event.code`** :   Identification code for this 
 : 640 - 13: type: keyword
 : 641 - 13: example: 4648
 : 642 - 620: **`event.created`** :   event.created contains the
 : 643 - 10: type: date
 : 644 - 33: example: 2016-05-23T08:05:34.857Z
 : 645 - 326: **`event.dataset`** :   Name of the dataset. If an
 : 646 - 13: type: keyword
 : 647 - 22: example: apache.access
 : 648 - 169: **`event.duration`** :   Duration of the event in 
 : 649 - 10: type: long
 : 650 - 16: format: duration
 : 651 - 108: **`event.end`** :   event.end contains the date wh
 : 652 - 10: type: date
 : 653 - 110: **`event.hash`** :   Hash (perhaps logstash finger
 : 654 - 13: type: keyword
 : 655 - 43: example: 123456789012345678901234567890ABCD
 : 656 - 51: **`event.id`** :   Unique ID to describe the event
 : 657 - 13: type: keyword
 : 658 - 17: example: 8a4f500d
 : 659 - 426: **`event.ingested`** :   Timestamp when an event a
 : 660 - 10: type: date
 : 661 - 33: example: 2016-05-23T08:05:35.101Z
 : 662 - 595: **`event.kind`** :   This is one of four ECS Categ
 : 663 - 13: type: keyword
 : 664 - 14: example: alert
 : 665 - 246: **`event.module`** :   Name of the module this dat
 : 666 - 13: type: keyword
 : 667 - 15: example: apache
 : 668 - 437: **`event.original`** :   Raw text message of entir
 : 669 - 13: type: keyword
 : 670 - 21: Field is not indexed.
 : 671 - 913: **`event.outcome`** :   This is one of four ECS Ca
 : 672 - 13: type: keyword
 : 673 - 16: example: success
 : 674 - 315: **`event.provider`** :   Source of the event. Even
 : 675 - 13: type: keyword
 : 676 - 15: example: kernel
 : 677 - 418: **`event.reason`** :   Reason why this event happe
 : 678 - 13: type: keyword
 : 679 - 41: example: Terminated an unexpected process
 : 680 - 230: **`event.reference`** :   Reference URL linking to
 : 681 - 13: type: keyword
 : 682 - 50: example: https://system.example.com/event/#0001234
 : 683 - 128: **`event.risk_score`** :   Risk score or priority 
 : 684 - 11: type: float
 : 685 - 242: **`event.risk_score_norm`** :   Normalized risk sc
 : 686 - 11: type: float
 : 687 - 207: **`event.sequence`** :   Sequence number of the ev
 : 688 - 10: type: long
 : 689 - 14: format: string
 : 690 - 576: **`event.severity`** :   The numeric severity of t
 : 691 - 10: type: long
 : 692 - 10: example: 7
 : 693 - 14: format: string
 : 694 - 115: **`event.start`** :   event.start contains the dat
 : 695 - 10: type: date
 : 696 - 329: **`event.timezone`** :   This field should be popu
 : 697 - 13: type: keyword
 : 698 - 435: **`event.type`** :   This is one of four ECS Categ
 : 699 - 13: type: keyword
 : 700 - 299: **`event.url`** :   URL linking to an external sys
 : 701 - 13: type: keyword
 : 702 - 80: example: https://mysystem.example.com/alert/5271de
 : 703 - 15: ## faas [_faas]
 : 704 - 99: The user fields describe information about the fun
 : 705 - 77: **`faas.coldstart`** :   Boolean value indicating 
 : 706 - 13: type: boolean
 : 707 - 76: **`faas.execution`** :   The execution ID of the c
 : 708 - 13: type: keyword
 : 709 - 45: example: af9d5aa4-a685-4c5f-a22b-444f80b3cc28
 : 710 - 58: **`faas.trigger`** :   Details about the function 
 : 711 - 12: type: nested
 : 712 - 86: **`faas.trigger.request_id`** :   The ID of the tr
 : 713 - 13: type: keyword
 : 714 - 18: example: 123456789
 : 715 - 133: **`faas.trigger.type`** :   The trigger for the fu
 : 716 - 13: type: keyword
 : 717 - 13: example: http
 : 718 - 17: ## file [_file_2]
 : 719 - 352: A file is defined as a set of information that has
 : 720 - 113: **`file.accessed`** :   Last time the file was acc
 : 721 - 10: type: date
 : 722 - 254: **`file.attributes`** :   Array of file attributes
 : 723 - 13: type: keyword
 : 724 - 31: example: ["readonly", "system"]
 : 725 - 227: **`file.code_signature.digest_algorithm`** :   The
 : 726 - 13: type: keyword
 : 727 - 15: example: sha256
 : 728 - 82: **`file.code_signature.exists`** :   Boolean to ca
 : 729 - 13: type: boolean
 : 730 - 13: example: true
 : 731 - 198: **`file.code_signature.signing_id`** :   The ident
 : 732 - 13: type: keyword
 : 733 - 28: example: com.apple.xpc.proxy
 : 734 - 261: **`file.code_signature.status`** :   Additional in
 : 735 - 13: type: keyword
 : 736 - 29: example: ERROR_UNTRUSTED_ROOT
 : 737 - 74: **`file.code_signature.subject_name`** :   Subject
 : 738 - 13: type: keyword
 : 739 - 30: example: Microsoft Corporation
 : 740 - 191: **`file.code_signature.team_id`** :   The team ide
 : 741 - 13: type: keyword
 : 742 - 19: example: EQHXZ8M8AV
 : 743 - 103: **`file.code_signature.timestamp`** :   Date and t
 : 744 - 10: type: date
 : 745 - 29: example: 2021-01-01T12:10:30Z
 : 746 - 234: **`file.code_signature.trusted`** :   Stores the t
 : 747 - 13: type: boolean
 : 748 - 13: example: true
 : 749 - 169: **`file.code_signature.valid`** :   Boolean to cap
 : 750 - 13: type: boolean
 : 751 - 13: example: true
 : 752 - 97: **`file.created`** :   File creation time. Note th
 : 753 - 10: type: date
 : 754 - 230: **`file.ctime`** :   Last time the file attributes
 : 755 - 10: type: date
 : 756 - 60: **`file.device`** :   Device that is the source of
 : 757 - 13: type: keyword
 : 758 - 12: example: sda
 : 759 - 115: **`file.directory`** :   Directory where the file 
 : 760 - 13: type: keyword
 : 761 - 20: example: /home/alice
 : 762 - 165: **`file.drive_letter`** :   Drive letter where the
 : 763 - 13: type: keyword
 : 764 - 10: example: C
 : 765 - 69: **`file.elf.architecture`** :   Machine architectu
 : 766 - 13: type: keyword
 : 767 - 15: example: x86-64
 : 768 - 56: **`file.elf.byte_order`** :   Byte sequence of ELF
 : 769 - 13: type: keyword
 : 770 - 22: example: Little Endian
 : 771 - 53: **`file.elf.cpu_type`** :   CPU type of the ELF fi
 : 772 - 13: type: keyword
 : 773 - 14: example: Intel
 : 774 - 165: **`file.elf.creation_date`** :   Extracted when po
 : 775 - 10: type: date
 : 776 - 68: **`file.elf.exports`** :   List of exported elemen
 : 777 - 15: type: flattened
 : 778 - 92: **`file.elf.header.abi_version`** :   Version of t
 : 779 - 13: type: keyword
 : 780 - 61: **`file.elf.header.class`** :   Header class of th
 : 781 - 13: type: keyword
 : 782 - 60: **`file.elf.header.data`** :   Data table of the E
 : 783 - 13: type: keyword
 : 784 - 71: **`file.elf.header.entrypoint`** :   Header entryp
 : 785 - 10: type: long
 : 786 - 14: format: string
 : 787 - 70: **`file.elf.header.object_version`** :   "0x1" for
 : 788 - 13: type: keyword
 : 789 - 84: **`file.elf.header.os_abi`** :   Application Binar
 : 790 - 13: type: keyword
 : 791 - 59: **`file.elf.header.type`** :   Header type of the 
 : 792 - 13: type: keyword
 : 793 - 60: **`file.elf.header.version`** :   Version of the E
 : 794 - 13: type: keyword
 : 795 - 68: **`file.elf.imports`** :   List of imported elemen
 : 796 - 15: type: flattened
 : 797 - 196: **`file.elf.sections`** :   An array containing an
 : 798 - 12: type: nested
 : 799 - 84: **`file.elf.sections.chi2`** :   Chi-square probab
 : 800 - 10: type: long
 : 801 - 14: format: number
 : 802 - 81: **`file.elf.sections.entropy`** :   Shannon entrop
 : 803 - 10: type: long
 : 804 - 14: format: number
 : 805 - 57: **`file.elf.sections.flags`** :   ELF Section List
 : 806 - 13: type: keyword
 : 807 - 55: **`file.elf.sections.name`** :   ELF Section List 
 : 808 - 13: type: keyword
 : 809 - 68: **`file.elf.sections.physical_offset`** :   ELF Se
 : 810 - 13: type: keyword
 : 811 - 73: **`file.elf.sections.physical_size`** :   ELF Sect
 : 812 - 10: type: long
 : 813 - 13: format: bytes
 : 814 - 55: **`file.elf.sections.type`** :   ELF Section List 
 : 815 - 13: type: keyword
 : 816 - 77: **`file.elf.sections.virtual_address`** :   ELF Se
 : 817 - 10: type: long
 : 818 - 14: format: string
 : 819 - 71: **`file.elf.sections.virtual_size`** :   ELF Secti
 : 820 - 10: type: long
 : 821 - 14: format: string
 : 822 - 196: **`file.elf.segments`** :   An array containing an
 : 823 - 12: type: nested
 : 824 - 65: **`file.elf.segments.sections`** :   ELF object se
 : 825 - 13: type: keyword
 : 826 - 57: **`file.elf.segments.type`** :   ELF object segmen
 : 827 - 13: type: keyword
 : 828 - 85: **`file.elf.shared_libraries`** :   List of shared
 : 829 - 13: type: keyword
 : 830 - 62: **`file.elf.telfhash`** :   telfhash symbol hash f
 : 831 - 13: type: keyword
 : 832 - 197: **`file.extension`** :   File extension, excluding
 : 833 - 13: type: keyword
 : 834 - 12: example: png
 : 835 - 787: **`file.fork_name`** :   A fork is additional data
 : 836 - 13: type: keyword
 : 837 - 23: example: Zone.Identifer
 : 838 - 54: **`file.gid`** :   Primary group ID (GID) of the f
 : 839 - 13: type: keyword
 : 840 - 13: example: 1001
 : 841 - 52: **`file.group`** :   Primary group name of the fil
 : 842 - 13: type: keyword
 : 843 - 14: example: alice
 : 844 - 33: **`file.hash.md5`** :   MD5 hash.
 : 845 - 13: type: keyword
 : 846 - 35: **`file.hash.sha1`** :   SHA1 hash.
 : 847 - 13: type: keyword
 : 848 - 39: **`file.hash.sha256`** :   SHA256 hash.
 : 849 - 13: type: keyword
 : 850 - 39: **`file.hash.sha512`** :   SHA512 hash.
 : 851 - 13: type: keyword
 : 852 - 39: **`file.hash.ssdeep`** :   SSDEEP hash.
 : 853 - 13: type: keyword
 : 854 - 67: **`file.inode`** :   Inode representing the file i
 : 855 - 13: type: keyword
 : 856 - 15: example: 256383
 : 857 - 214: **`file.mime_type`** :   MIME type should identify
 : 858 - 13: type: keyword
 : 859 - 61: **`file.mode`** :   Mode of the file in octal repr
 : 860 - 13: type: keyword
 : 861 - 13: example: 0640
 : 862 - 61: **`file.mtime`** :   Last time the file content wa
 : 863 - 10: type: date
 : 864 - 84: **`file.name`** :   Name of the file including the
 : 865 - 13: type: keyword
 : 866 - 20: example: example.png
 : 867 - 43: **`file.owner`** :   File owner’s username.
 : 868 - 13: type: keyword
 : 869 - 14: example: alice
 : 870 - 121: **`file.path`** :   Full path to the file, includi
 : 871 - 13: type: keyword
 : 872 - 32: example: /home/alice/example.png
 : 873 - 46: **`file.path.text`** :   type: match_only_text
 : 874 - 68: **`file.pe.architecture`** :   CPU architecture ta
 : 875 - 13: type: keyword
 : 876 - 12: example: x64
 : 877 - 86: **`file.pe.company`** :   Internal company name of
 : 878 - 13: type: keyword
 : 879 - 30: example: Microsoft Corporation
 : 880 - 89: **`file.pe.description`** :   Internal description
 : 881 - 13: type: keyword
 : 882 - 14: example: Paint
 : 883 - 86: **`file.pe.file_version`** :   Internal version of
 : 884 - 13: type: keyword
 : 885 - 23: example: 6.3.9600.17415
 : 886 - 358: **`file.pe.imphash`** :   A hash of the imports in
 : 887 - 13: type: keyword
 : 888 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 889 - 89: **`file.pe.original_file_name`** :   Internal name
 : 890 - 13: type: keyword
 : 891 - 20: example: MSPAINT.EXE
 : 892 - 86: **`file.pe.product`** :   Internal product name of
 : 893 - 13: type: keyword
 : 894 - 45: example: Microsoft® Windows® Operating System
 : 895 - 81: **`file.size`** :   File size in bytes. Only relev
 : 896 - 10: type: long
 : 897 - 14: example: 16384
 : 898 - 52: **`file.target_path`** :   Target path for symlink
 : 899 - 13: type: keyword
 : 900 - 53: **`file.target_path.text`** :   type: match_only_t
 : 901 - 54: **`file.type`** :   File type (file, dir, or symli
 : 902 - 13: type: keyword
 : 903 - 13: example: file
 : 904 - 84: **`file.uid`** :   The user ID (UID) or security i
 : 905 - 13: type: keyword
 : 906 - 13: example: 1001
 : 907 - 223: **`file.x509.alternative_names`** :   List of subj
 : 908 - 13: type: keyword
 : 909 - 21: example: *.elastic.co
 : 910 - 97: **`file.x509.issuer.common_name`** :   List of com
 : 911 - 13: type: keyword
 : 912 - 46: example: Example SHA2 High Assurance Server CA
 : 913 - 58: **`file.x509.issuer.country`** :   List of country
 : 914 - 13: type: keyword
 : 915 - 11: example: US
 : 916 - 103: **`file.x509.issuer.distinguished_name`** :   Dist
 : 917 - 13: type: keyword
 : 918 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 919 - 62: **`file.x509.issuer.locality`** :   List of locali
 : 920 - 13: type: keyword
 : 921 - 22: example: Mountain View
 : 922 - 99: **`file.x509.issuer.organization`** :   List of or
 : 923 - 13: type: keyword
 : 924 - 20: example: Example Inc
 : 925 - 114: **`file.x509.issuer.organizational_unit`** :   Lis
 : 926 - 13: type: keyword
 : 927 - 24: example: www.example.com
 : 928 - 90: **`file.x509.issuer.state_or_province`** :   List 
 : 929 - 13: type: keyword
 : 930 - 19: example: California
 : 931 - 90: **`file.x509.not_after`** :   Time at which the ce
 : 932 - 10: type: date
 : 933 - 34: example: 2020-07-16 03:15:39+00:00
 : 934 - 87: **`file.x509.not_before`** :   Time at which the c
 : 935 - 10: type: date
 : 936 - 34: example: 2019-08-16 01:40:25+00:00
 : 937 - 83: **`file.x509.public_key_algorithm`** :   Algorithm
 : 938 - 13: type: keyword
 : 939 - 12: example: RSA
 : 940 - 123: **`file.x509.public_key_curve`** :   The curve use
 : 941 - 13: type: keyword
 : 942 - 17: example: nistp521
 : 943 - 107: **`file.x509.public_key_exponent`** :   Exponent u
 : 944 - 10: type: long
 : 945 - 14: example: 65537
 : 946 - 21: Field is not indexed.
 : 947 - 77: **`file.x509.public_key_size`** :   The size of th
 : 948 - 10: type: long
 : 949 - 13: example: 2048
 : 950 - 203: **`file.x509.serial_number`** :   Unique serial nu
 : 951 - 13: type: keyword
 : 952 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 953 - 226: **`file.x509.signature_algorithm`** :   Identifier
 : 954 - 13: type: keyword
 : 955 - 19: example: SHA256-RSA
 : 956 - 77: **`file.x509.subject.common_name`** :   List of co
 : 957 - 13: type: keyword
 : 958 - 34: example: shared.global.example.net
 : 959 - 58: **`file.x509.subject.country`** :   List of countr
 : 960 - 13: type: keyword
 : 961 - 11: example: US
 : 962 - 105: **`file.x509.subject.distinguished_name`** :   Dis
 : 963 - 13: type: keyword
 : 964 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 965 - 63: **`file.x509.subject.locality`** :   List of local
 : 966 - 13: type: keyword
 : 967 - 22: example: San Francisco
 : 968 - 78: **`file.x509.subject.organization`** :   List of o
 : 969 - 13: type: keyword
 : 970 - 22: example: Example, Inc.
 : 971 - 93: **`file.x509.subject.organizational_unit`** :   Li
 : 972 - 13: type: keyword
 : 973 - 91: **`file.x509.subject.state_or_province`** :   List
 : 974 - 13: type: keyword
 : 975 - 19: example: California
 : 976 - 58: **`file.x509.version_number`** :   Version of x509
 : 977 - 13: type: keyword
 : 978 - 10: example: 3
 : 979 - 13: ## geo [_geo]
 : 980 - 169: Geo fields can carry data about a specific locatio
 : 981 - 34: **`geo.city_name`** :   City name.
 : 982 - 13: type: keyword
 : 983 - 17: example: Montreal
 : 984 - 75: **`geo.continent_code`** :   Two-letter code repre
 : 985 - 13: type: keyword
 : 986 - 11: example: NA
 : 987 - 51: **`geo.continent_name`** :   Name of the continent
 : 988 - 13: type: keyword
 : 989 - 22: example: North America
 : 990 - 48: **`geo.country_iso_code`** :   Country ISO code.
 : 991 - 13: type: keyword
 : 992 - 11: example: CA
 : 993 - 40: **`geo.country_name`** :   Country name.
 : 994 - 13: type: keyword
 : 995 - 15: example: Canada
 : 996 - 46: **`geo.location`** :   Longitude and latitude.
 : 997 - 15: type: geo_point
 : 998 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 999 - 262: **`geo.name`** :   User-defined description of a l
 : 1000 - 13: type: keyword
 : 1001 - 18: example: boston-dc
 : 1002 - 191: **`geo.postal_code`** :   Postal code associated w
 : 1003 - 13: type: keyword
 : 1004 - 14: example: 94040
 : 1005 - 46: **`geo.region_iso_code`** :   Region ISO code.
 : 1006 - 13: type: keyword
 : 1007 - 14: example: CA-QC
 : 1008 - 38: **`geo.region_name`** :   Region name.
 : 1009 - 13: type: keyword
 : 1010 - 15: example: Quebec
 : 1011 - 82: **`geo.timezone`** :   The time zone of the locati
 : 1012 - 13: type: keyword
 : 1013 - 39: example: America/Argentina/Buenos_Aires
 : 1014 - 19: ## group [_group_3]
 : 1015 - 78: The group fields are meant to represent groups tha
 : 1016 - 124: **`group.domain`** :   Name of the directory the g
 : 1017 - 13: type: keyword
 : 1018 - 74: **`group.id`** :   Unique identifier for the group
 : 1019 - 13: type: keyword
 : 1020 - 39: **`group.name`** :   Name of the group.
 : 1021 - 13: type: keyword
 : 1022 - 15: ## hash [_hash]
 : 1023 - 508: The hash fields represent different bitwise hash a
 : 1024 - 28: **`hash.md5`** :   MD5 hash.
 : 1025 - 13: type: keyword
 : 1026 - 30: **`hash.sha1`** :   SHA1 hash.
 : 1027 - 13: type: keyword
 : 1028 - 34: **`hash.sha256`** :   SHA256 hash.
 : 1029 - 13: type: keyword
 : 1030 - 34: **`hash.sha512`** :   SHA512 hash.
 : 1031 - 13: type: keyword
 : 1032 - 34: **`hash.ssdeep`** :   SSDEEP hash.
 : 1033 - 13: type: keyword
 : 1034 - 15: ## host [_host]
 : 1035 - 274: A host is defined as a general computing instance.
 : 1036 - 58: **`host.architecture`** :   Operating system archi
 : 1037 - 13: type: keyword
 : 1038 - 15: example: x86_64
 : 1039 - 239: **`host.cpu.usage`** :   Percent CPU used which is
 : 1040 - 18: type: scaled_float
 : 1041 - 144: **`host.disk.read.bytes`** :   The total number of
 : 1042 - 10: type: long
 : 1043 - 148: **`host.disk.write.bytes`** :   The total number o
 : 1044 - 10: type: long
 : 1045 - 232: **`host.domain`** :   Name of the domain of which 
 : 1046 - 13: type: keyword
 : 1047 - 16: example: CONTOSO
 : 1048 - 39: **`host.geo.city_name`** :   City name.
 : 1049 - 13: type: keyword
 : 1050 - 17: example: Montreal
 : 1051 - 80: **`host.geo.continent_code`** :   Two-letter code 
 : 1052 - 13: type: keyword
 : 1053 - 11: example: NA
 : 1054 - 56: **`host.geo.continent_name`** :   Name of the cont
 : 1055 - 13: type: keyword
 : 1056 - 22: example: North America
 : 1057 - 53: **`host.geo.country_iso_code`** :   Country ISO co
 : 1058 - 13: type: keyword
 : 1059 - 11: example: CA
 : 1060 - 45: **`host.geo.country_name`** :   Country name.
 : 1061 - 13: type: keyword
 : 1062 - 15: example: Canada
 : 1063 - 51: **`host.geo.location`** :   Longitude and latitude
 : 1064 - 15: type: geo_point
 : 1065 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 1066 - 267: **`host.geo.name`** :   User-defined description o
 : 1067 - 13: type: keyword
 : 1068 - 18: example: boston-dc
 : 1069 - 196: **`host.geo.postal_code`** :   Postal code associa
 : 1070 - 13: type: keyword
 : 1071 - 14: example: 94040
 : 1072 - 51: **`host.geo.region_iso_code`** :   Region ISO code
 : 1073 - 13: type: keyword
 : 1074 - 14: example: CA-QC
 : 1075 - 43: **`host.geo.region_name`** :   Region name.
 : 1076 - 13: type: keyword
 : 1077 - 15: example: Quebec
 : 1078 - 87: **`host.geo.timezone`** :   The time zone of the l
 : 1079 - 13: type: keyword
 : 1080 - 39: example: America/Argentina/Buenos_Aires
 : 1081 - 123: **`host.hostname`** :   Hostname of the host. It n
 : 1082 - 13: type: keyword
 : 1083 - 163: **`host.id`** :   Unique host id. As hostname is n
 : 1084 - 13: type: keyword
 : 1085 - 36: **`host.ip`** :   Host ip addresses.
 : 1086 - 8: type: ip
 : 1087 - 271: **`host.mac`** :   Host MAC addresses. The notatio
 : 1088 - 13: type: keyword
 : 1089 - 51: example: ["00-00-5E-00-53-23", "00-00-5E-00-53-24"
 : 1090 - 198: **`host.name`** :   Name of the host. It can conta
 : 1091 - 13: type: keyword
 : 1092 - 144: **`host.network.egress.bytes`** :   The number of 
 : 1093 - 10: type: long
 : 1094 - 148: **`host.network.egress.packets`** :   The number o
 : 1095 - 10: type: long
 : 1096 - 145: **`host.network.ingress.bytes`** :   The number of
 : 1097 - 10: type: long
 : 1098 - 149: **`host.network.ingress.packets`** :   The number 
 : 1099 - 10: type: long
 : 1100 - 78: **`host.os.family`** :   OS family (such as redhat
 : 1101 - 13: type: keyword
 : 1102 - 15: example: debian
 : 1103 - 81: **`host.os.full`** :   Operating system name, incl
 : 1104 - 13: type: keyword
 : 1105 - 22: example: Mac OS Mojave
 : 1106 - 49: **`host.os.full.text`** :   type: match_only_text
 : 1107 - 73: **`host.os.kernel`** :   Operating system kernel v
 : 1108 - 13: type: keyword
 : 1109 - 26: example: 4.4.0-112-generic
 : 1110 - 66: **`host.os.name`** :   Operating system name, with
 : 1111 - 13: type: keyword
 : 1112 - 17: example: Mac OS X
 : 1113 - 49: **`host.os.name.text`** :   type: match_only_text
 : 1114 - 84: **`host.os.platform`** :   Operating system platfo
 : 1115 - 13: type: keyword
 : 1116 - 15: example: darwin
 : 1117 - 370: **`host.os.type`** :   Use the `os.type` field to 
 : 1118 - 13: type: keyword
 : 1119 - 14: example: macos
 : 1120 - 67: **`host.os.version`** :   Operating system version
 : 1121 - 13: type: keyword
 : 1122 - 16: example: 10.14.1
 : 1123 - 203: **`host.type`** :   Type of host. For Cloud provid
 : 1124 - 13: type: keyword
 : 1125 - 51: **`host.uptime`** :   Seconds the host has been up
 : 1126 - 10: type: long
 : 1127 - 13: example: 1325
 : 1128 - 15: ## http [_http]
 : 1129 - 89: Fields related to HTTP activity. Use the `url` fie
 : 1130 - 68: **`http.request.body.bytes`** :   Size in bytes of
 : 1131 - 10: type: long
 : 1132 - 12: example: 887
 : 1133 - 13: format: bytes
 : 1134 - 63: **`http.request.body.content`** :   The full HTTP 
 : 1135 - 14: type: wildcard
 : 1136 - 20: example: Hello world
 : 1137 - 62: **`http.request.body.content.text`** :   type: mat
 : 1138 - 83: **`http.request.bytes`** :   Total size in bytes o
 : 1139 - 10: type: long
 : 1140 - 13: example: 1437
 : 1141 - 13: format: bytes
 : 1142 - 232: **`http.request.id`** :   A unique identifier for 
 : 1143 - 13: type: keyword
 : 1144 - 45: example: 123e4567-e89b-12d3-a456-426614174000
 : 1145 - 197: **`http.request.method`** :   HTTP request method.
 : 1146 - 13: type: keyword
 : 1147 - 13: example: POST
 : 1148 - 318: **`http.request.mime_type`** :   Mime type of the 
 : 1149 - 13: type: keyword
 : 1150 - 18: example: image/gif
 : 1151 - 63: **`http.request.referrer`** :   Referrer for this 
 : 1152 - 13: type: keyword
 : 1153 - 34: example: https://blog.example.com/
 : 1154 - 70: **`http.response.body.bytes`** :   Size in bytes o
 : 1155 - 10: type: long
 : 1156 - 12: example: 887
 : 1157 - 13: format: bytes
 : 1158 - 65: **`http.response.body.content`** :   The full HTTP
 : 1159 - 14: type: wildcard
 : 1160 - 20: example: Hello world
 : 1161 - 63: **`http.response.body.content.text`** :   type: ma
 : 1162 - 85: **`http.response.bytes`** :   Total size in bytes 
 : 1163 - 10: type: long
 : 1164 - 13: example: 1437
 : 1165 - 13: format: bytes
 : 1166 - 312: **`http.response.mime_type`** :   Mime type of the
 : 1167 - 13: type: keyword
 : 1168 - 18: example: image/gif
 : 1169 - 62: **`http.response.status_code`** :   HTTP response 
 : 1170 - 10: type: long
 : 1171 - 12: example: 404
 : 1172 - 14: format: string
 : 1173 - 36: **`http.version`** :   HTTP version.
 : 1174 - 13: type: keyword
 : 1175 - 12: example: 1.1
 : 1176 - 25: ## interface [_interface]
 : 1177 - 350: The interface fields are used to record ingress an
 : 1178 - 170: **`interface.alias`** :   Interface alias as repor
 : 1179 - 13: type: keyword
 : 1180 - 16: example: outside
 : 1181 - 93: **`interface.id`** :   Interface ID as reported by
 : 1182 - 13: type: keyword
 : 1183 - 11: example: 10
 : 1184 - 66: **`interface.name`** :   Interface name as reporte
 : 1185 - 13: type: keyword
 : 1186 - 13: example: eth0
 : 1187 - 13: ## log [_log]
 : 1188 - 379: Details about the event’s logging mechanism or log
 : 1189 - 220: **`log.file.path`** :   Full path to the log file 
 : 1190 - 13: type: keyword
 : 1191 - 31: example: /var/log/fun-times.log
 : 1192 - 336: **`log.level`** :   Original log level of the log 
 : 1193 - 13: type: keyword
 : 1194 - 14: example: error
 : 1195 - 159: **`log.logger`** :   The name of the logger inside
 : 1196 - 13: type: keyword
 : 1197 - 46: example: org.elasticsearch.bootstrap.Bootstrap
 : 1198 - 117: **`log.origin.file.line`** :   The line number of 
 : 1199 - 10: type: long
 : 1200 - 11: example: 42
 : 1201 - 232: **`log.origin.file.name`** :   The name of the fil
 : 1202 - 13: type: keyword
 : 1203 - 23: example: Bootstrap.java
 : 1204 - 96: **`log.origin.function`** :   The name of the func
 : 1205 - 13: type: keyword
 : 1206 - 13: example: init
 : 1207 - 125: **`log.syslog`** :   The Syslog metadata of the ev
 : 1208 - 12: type: object
 : 1209 - 177: **`log.syslog.facility.code`** :   The Syslog nume
 : 1210 - 10: type: long
 : 1211 - 11: example: 23
 : 1212 - 14: format: string
 : 1213 - 97: **`log.syslog.facility.name`** :   The Syslog text
 : 1214 - 13: type: keyword
 : 1215 - 15: example: local7
 : 1216 - 227: **`log.syslog.priority`** :   Syslog numeric prior
 : 1217 - 10: type: long
 : 1218 - 12: example: 135
 : 1219 - 14: format: string
 : 1220 - 389: **`log.syslog.severity.code`** :   The Syslog nume
 : 1221 - 10: type: long
 : 1222 - 10: example: 3
 : 1223 - 368: **`log.syslog.severity.name`** :   The Syslog nume
 : 1224 - 13: type: keyword
 : 1225 - 14: example: Error
 : 1226 - 21: ## network [_network]
 : 1227 - 199: The network is defined as the communication path o
 : 1228 - 453: **`network.application`** :   When a specific appl
 : 1229 - 13: type: keyword
 : 1230 - 12: example: aim
 : 1231 - 150: **`network.bytes`** :   Total bytes transferred in
 : 1232 - 10: type: long
 : 1233 - 12: example: 368
 : 1234 - 13: format: bytes
 : 1235 - 242: **`network.community_id`** :   A hash of source an
 : 1236 - 13: type: keyword
 : 1237 - 39: example: 1:hO+sN4H+MG5MY/8hIrXPqc4ZQz0=
 : 1238 - 157: **`network.direction`** :   Direction of the netwo
 : 1239 - 672: When mapping events from a host-based monitoring c
 : 1240 - 13: type: keyword
 : 1241 - 16: example: inbound
 : 1242 - 87: **`network.forwarded_ip`** :   Host IP address whe
 : 1243 - 8: type: ip
 : 1244 - 18: example: 192.1.1.2
 : 1245 - 249: **`network.iana_number`** :   IANA Protocol Number
 : 1246 - 13: type: keyword
 : 1247 - 10: example: 6
 : 1248 - 341: **`network.inner`** :   Network.inner fields are a
 : 1249 - 12: type: object
 : 1250 - 68: **`network.inner.vlan.id`** :   VLAN ID as reporte
 : 1251 - 13: type: keyword
 : 1252 - 11: example: 10
 : 1253 - 81: **`network.inner.vlan.name`** :   Optional VLAN na
 : 1254 - 13: type: keyword
 : 1255 - 16: example: outside
 : 1256 - 76: **`network.name`** :   Name given by operators to 
 : 1257 - 13: type: keyword
 : 1258 - 19: example: Guest Wifi
 : 1259 - 160: **`network.packets`** :   Total packets transferre
 : 1260 - 10: type: long
 : 1261 - 11: example: 24
 : 1262 - 192: **`network.protocol`** :   In the OSI Model this w
 : 1263 - 13: type: keyword
 : 1264 - 13: example: http
 : 1265 - 204: **`network.transport`** :   Same as network.iana_n
 : 1266 - 13: type: keyword
 : 1267 - 12: example: tcp
 : 1268 - 162: **`network.type`** :   In the OSI Model this would
 : 1269 - 13: type: keyword
 : 1270 - 13: example: ipv4
 : 1271 - 62: **`network.vlan.id`** :   VLAN ID as reported by t
 : 1272 - 13: type: keyword
 : 1273 - 11: example: 10
 : 1274 - 75: **`network.vlan.name`** :   Optional VLAN name as 
 : 1275 - 13: type: keyword
 : 1276 - 16: example: outside
 : 1277 - 23: ## observer [_observer]
 : 1278 - 770: An observer is defined as a special network, secur
 : 1279 - 267: **`observer.egress`** :   Observer.egress holds in
 : 1280 - 12: type: object
 : 1281 - 186: **`observer.egress.interface.alias`** :   Interfac
 : 1282 - 13: type: keyword
 : 1283 - 16: example: outside
 : 1284 - 109: **`observer.egress.interface.id`** :   Interface I
 : 1285 - 13: type: keyword
 : 1286 - 11: example: 10
 : 1287 - 82: **`observer.egress.interface.name`** :   Interface
 : 1288 - 13: type: keyword
 : 1289 - 13: example: eth0
 : 1290 - 70: **`observer.egress.vlan.id`** :   VLAN ID as repor
 : 1291 - 13: type: keyword
 : 1292 - 11: example: 10
 : 1293 - 83: **`observer.egress.vlan.name`** :   Optional VLAN 
 : 1294 - 13: type: keyword
 : 1295 - 16: example: outside
 : 1296 - 191: **`observer.egress.zone`** :   Network zone of out
 : 1297 - 13: type: keyword
 : 1298 - 24: example: Public_Internet
 : 1299 - 43: **`observer.geo.city_name`** :   City name.
 : 1300 - 13: type: keyword
 : 1301 - 17: example: Montreal
 : 1302 - 84: **`observer.geo.continent_code`** :   Two-letter c
 : 1303 - 13: type: keyword
 : 1304 - 11: example: NA
 : 1305 - 60: **`observer.geo.continent_name`** :   Name of the 
 : 1306 - 13: type: keyword
 : 1307 - 22: example: North America
 : 1308 - 57: **`observer.geo.country_iso_code`** :   Country IS
 : 1309 - 13: type: keyword
 : 1310 - 11: example: CA
 : 1311 - 49: **`observer.geo.country_name`** :   Country name.
 : 1312 - 13: type: keyword
 : 1313 - 15: example: Canada
 : 1314 - 55: **`observer.geo.location`** :   Longitude and lati
 : 1315 - 15: type: geo_point
 : 1316 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 1317 - 271: **`observer.geo.name`** :   User-defined descripti
 : 1318 - 13: type: keyword
 : 1319 - 18: example: boston-dc
 : 1320 - 200: **`observer.geo.postal_code`** :   Postal code ass
 : 1321 - 13: type: keyword
 : 1322 - 14: example: 94040
 : 1323 - 55: **`observer.geo.region_iso_code`** :   Region ISO 
 : 1324 - 13: type: keyword
 : 1325 - 14: example: CA-QC
 : 1326 - 47: **`observer.geo.region_name`** :   Region name.
 : 1327 - 13: type: keyword
 : 1328 - 15: example: Quebec
 : 1329 - 91: **`observer.geo.timezone`** :   The time zone of t
 : 1330 - 13: type: keyword
 : 1331 - 39: example: America/Argentina/Buenos_Aires
 : 1332 - 53: **`observer.hostname`** :   Hostname of the observ
 : 1333 - 13: type: keyword
 : 1334 - 270: **`observer.ingress`** :   Observer.ingress holds 
 : 1335 - 12: type: object
 : 1336 - 187: **`observer.ingress.interface.alias`** :   Interfa
 : 1337 - 13: type: keyword
 : 1338 - 16: example: outside
 : 1339 - 110: **`observer.ingress.interface.id`** :   Interface 
 : 1340 - 13: type: keyword
 : 1341 - 11: example: 10
 : 1342 - 83: **`observer.ingress.interface.name`** :   Interfac
 : 1343 - 13: type: keyword
 : 1344 - 13: example: eth0
 : 1345 - 71: **`observer.ingress.vlan.id`** :   VLAN ID as repo
 : 1346 - 13: type: keyword
 : 1347 - 11: example: 10
 : 1348 - 84: **`observer.ingress.vlan.name`** :   Optional VLAN
 : 1349 - 13: type: keyword
 : 1350 - 16: example: outside
 : 1351 - 188: **`observer.ingress.zone`** :   Network zone of in
 : 1352 - 13: type: keyword
 : 1353 - 12: example: DMZ
 : 1354 - 51: **`observer.ip`** :   IP addresses of the observer
 : 1355 - 8: type: ip
 : 1356 - 286: **`observer.mac`** :   MAC addresses of the observ
 : 1357 - 13: type: keyword
 : 1358 - 51: example: ["00-00-5E-00-53-23", "00-00-5E-00-53-24"
 : 1359 - 260: **`observer.name`** :   Custom name of the observe
 : 1360 - 13: type: keyword
 : 1361 - 18: example: 1_proxySG
 : 1362 - 82: **`observer.os.family`** :   OS family (such as re
 : 1363 - 13: type: keyword
 : 1364 - 15: example: debian
 : 1365 - 85: **`observer.os.full`** :   Operating system name, 
 : 1366 - 13: type: keyword
 : 1367 - 22: example: Mac OS Mojave
 : 1368 - 53: **`observer.os.full.text`** :   type: match_only_t
 : 1369 - 77: **`observer.os.kernel`** :   Operating system kern
 : 1370 - 13: type: keyword
 : 1371 - 26: example: 4.4.0-112-generic
 : 1372 - 70: **`observer.os.name`** :   Operating system name, 
 : 1373 - 13: type: keyword
 : 1374 - 17: example: Mac OS X
 : 1375 - 53: **`observer.os.name.text`** :   type: match_only_t
 : 1376 - 88: **`observer.os.platform`** :   Operating system pl
 : 1377 - 13: type: keyword
 : 1378 - 15: example: darwin
 : 1379 - 374: **`observer.os.type`** :   Use the `os.type` field
 : 1380 - 13: type: keyword
 : 1381 - 14: example: macos
 : 1382 - 71: **`observer.os.version`** :   Operating system ver
 : 1383 - 13: type: keyword
 : 1384 - 16: example: 10.14.1
 : 1385 - 60: **`observer.product`** :   The product name of the
 : 1386 - 13: type: keyword
 : 1387 - 13: example: s200
 : 1388 - 56: **`observer.serial_number`** :   Observer serial n
 : 1389 - 13: type: keyword
 : 1390 - 228: **`observer.type`** :   The type of the observer t
 : 1391 - 13: type: keyword
 : 1392 - 17: example: firewall
 : 1393 - 54: **`observer.vendor`** :   Vendor name of the obser
 : 1394 - 13: type: keyword
 : 1395 - 17: example: Symantec
 : 1396 - 44: **`observer.version`** :   Observer version.
 : 1397 - 13: type: keyword
 : 1398 - 31: ## orchestrator [_orchestrator]
 : 1399 - 84: Fields that describe the resources which container
 : 1400 - 81: **`orchestrator.api_version`** :   API version bei
 : 1401 - 13: type: keyword
 : 1402 - 16: example: v1beta1
 : 1403 - 56: **`orchestrator.cluster.name`** :   Name of the cl
 : 1404 - 13: type: keyword
 : 1405 - 77: **`orchestrator.cluster.url`** :   URL of the API 
 : 1406 - 13: type: keyword
 : 1407 - 66: **`orchestrator.cluster.version`** :   The version
 : 1408 - 13: type: keyword
 : 1409 - 79: **`orchestrator.namespace`** :   Namespace in whic
 : 1410 - 13: type: keyword
 : 1411 - 20: example: kube-system
 : 1412 - 110: **`orchestrator.organization`** :   Organization a
 : 1413 - 13: type: keyword
 : 1414 - 16: example: elastic
 : 1415 - 75: **`orchestrator.resource.name`** :   Name of the r
 : 1416 - 13: type: keyword
 : 1417 - 23: example: test-pod-cdcws
 : 1418 - 71: **`orchestrator.resource.type`** :   Type of resou
 : 1419 - 13: type: keyword
 : 1420 - 16: example: service
 : 1421 - 95: **`orchestrator.type`** :   Orchestrator cluster t
 : 1422 - 13: type: keyword
 : 1423 - 19: example: kubernetes
 : 1424 - 31: ## organization [_organization]
 : 1425 - 207: The organization fields enrich data with informati
 : 1426 - 65: **`organization.id`** :   Unique identifier for th
 : 1427 - 13: type: keyword
 : 1428 - 46: **`organization.name`** :   Organization name.
 : 1429 - 13: type: keyword
 : 1430 - 54: **`organization.name.text`** :   type: match_only_
 : 1431 - 11: ## os [_os]
 : 1432 - 61: The OS fields contain information about the operat
 : 1433 - 73: **`os.family`** :   OS family (such as redhat, deb
 : 1434 - 13: type: keyword
 : 1435 - 15: example: debian
 : 1436 - 76: **`os.full`** :   Operating system name, including
 : 1437 - 13: type: keyword
 : 1438 - 22: example: Mac OS Mojave
 : 1439 - 44: **`os.full.text`** :   type: match_only_text
 : 1440 - 68: **`os.kernel`** :   Operating system kernel versio
 : 1441 - 13: type: keyword
 : 1442 - 26: example: 4.4.0-112-generic
 : 1443 - 61: **`os.name`** :   Operating system name, without t
 : 1444 - 13: type: keyword
 : 1445 - 17: example: Mac OS X
 : 1446 - 44: **`os.name.text`** :   type: match_only_text
 : 1447 - 79: **`os.platform`** :   Operating system platform (s
 : 1448 - 13: type: keyword
 : 1449 - 15: example: darwin
 : 1450 - 365: **`os.type`** :   Use the `os.type` field to categ
 : 1451 - 13: type: keyword
 : 1452 - 14: example: macos
 : 1453 - 62: **`os.version`** :   Operating system version as a
 : 1454 - 13: type: keyword
 : 1455 - 16: example: 10.14.1
 : 1456 - 21: ## package [_package]
 : 1457 - 214: These fields contain information about an installe
 : 1458 - 52: **`package.architecture`** :   Package architectur
 : 1459 - 13: type: keyword
 : 1460 - 15: example: x86_64
 : 1461 - 162: **`package.build_version`** :   Additional informa
 : 1462 - 13: type: keyword
 : 1463 - 49: example: 36f4f7e89dd61b0988b12ee000b98966867710cd
 : 1464 - 78: **`package.checksum`** :   Checksum of the install
 : 1465 - 13: type: keyword
 : 1466 - 41: example: 68b329da9893e34099c7d8ad5cb9c940
 : 1467 - 57: **`package.description`** :   Description of the p
 : 1468 - 13: type: keyword
 : 1469 - 86: example: Open source programming language to build
 : 1470 - 98: **`package.install_scope`** :   Indicating how the
 : 1471 - 13: type: keyword
 : 1472 - 15: example: global
 : 1473 - 60: **`package.installed`** :   Time when package was 
 : 1474 - 10: type: date
 : 1475 - 187: **`package.license`** :   License under which the 
 : 1476 - 13: type: keyword
 : 1477 - 27: example: Apache License 2.0
 : 1478 - 35: **`package.name`** :   Package name
 : 1479 - 13: type: keyword
 : 1480 - 11: example: go
 : 1481 - 59: **`package.path`** :   Path where the package is i
 : 1482 - 13: type: keyword
 : 1483 - 37: example: /usr/local/Cellar/go/1.12.9/
 : 1484 - 101: **`package.reference`** :   Home page or reference
 : 1485 - 13: type: keyword
 : 1486 - 27: example: https://golang.org
 : 1487 - 45: **`package.size`** :   Package size in bytes.
 : 1488 - 10: type: long
 : 1489 - 14: example: 62231
 : 1490 - 14: format: string
 : 1491 - 169: **`package.type`** :   Type of package. This shoul
 : 1492 - 13: type: keyword
 : 1493 - 12: example: rpm
 : 1494 - 41: **`package.version`** :   Package version
 : 1495 - 13: type: keyword
 : 1496 - 15: example: 1.12.9
 : 1497 - 11: ## pe [_pe]
 : 1498 - 63: These fields contain Windows Portable Executable (
 : 1499 - 63: **`pe.architecture`** :   CPU architecture target 
 : 1500 - 13: type: keyword
 : 1501 - 12: example: x64
 : 1502 - 81: **`pe.company`** :   Internal company name of the 
 : 1503 - 13: type: keyword
 : 1504 - 30: example: Microsoft Corporation
 : 1505 - 84: **`pe.description`** :   Internal description of t
 : 1506 - 13: type: keyword
 : 1507 - 14: example: Paint
 : 1508 - 81: **`pe.file_version`** :   Internal version of the 
 : 1509 - 13: type: keyword
 : 1510 - 23: example: 6.3.9600.17415
 : 1511 - 353: **`pe.imphash`** :   A hash of the imports in a PE
 : 1512 - 13: type: keyword
 : 1513 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 1514 - 84: **`pe.original_file_name`** :   Internal name of t
 : 1515 - 13: type: keyword
 : 1516 - 20: example: MSPAINT.EXE
 : 1517 - 81: **`pe.product`** :   Internal product name of the 
 : 1518 - 13: type: keyword
 : 1519 - 45: example: Microsoft® Windows® Operating System
 : 1520 - 23: ## process [_process_2]
 : 1521 - 251: These fields contain information about a process. 
 : 1522 - 151: **`process.args`** :   Array of process arguments,
 : 1523 - 13: type: keyword
 : 1524 - 52: example: ["/usr/bin/ssh", "-l", "user", "10.0.0.16
 : 1525 - 246: **`process.args_count`** :   Length of the process
 : 1526 - 10: type: long
 : 1527 - 10: example: 4
 : 1528 - 230: **`process.code_signature.digest_algorithm`** :   
 : 1529 - 13: type: keyword
 : 1530 - 15: example: sha256
 : 1531 - 85: **`process.code_signature.exists`** :   Boolean to
 : 1532 - 13: type: boolean
 : 1533 - 13: example: true
 : 1534 - 201: **`process.code_signature.signing_id`** :   The id
 : 1535 - 13: type: keyword
 : 1536 - 28: example: com.apple.xpc.proxy
 : 1537 - 264: **`process.code_signature.status`** :   Additional
 : 1538 - 13: type: keyword
 : 1539 - 29: example: ERROR_UNTRUSTED_ROOT
 : 1540 - 77: **`process.code_signature.subject_name`** :   Subj
 : 1541 - 13: type: keyword
 : 1542 - 30: example: Microsoft Corporation
 : 1543 - 194: **`process.code_signature.team_id`** :   The team 
 : 1544 - 13: type: keyword
 : 1545 - 19: example: EQHXZ8M8AV
 : 1546 - 106: **`process.code_signature.timestamp`** :   Date an
 : 1547 - 10: type: date
 : 1548 - 29: example: 2021-01-01T12:10:30Z
 : 1549 - 237: **`process.code_signature.trusted`** :   Stores th
 : 1550 - 13: type: boolean
 : 1551 - 13: example: true
 : 1552 - 172: **`process.code_signature.valid`** :   Boolean to 
 : 1553 - 13: type: boolean
 : 1554 - 13: example: true
 : 1555 - 205: **`process.command_line`** :   Full command line t
 : 1556 - 14: type: wildcard
 : 1557 - 39: example: /usr/bin/ssh -l user 10.0.0.16
 : 1558 - 57: **`process.command_line.text`** :   type: match_on
 : 1559 - 72: **`process.elf.architecture`** :   Machine archite
 : 1560 - 13: type: keyword
 : 1561 - 15: example: x86-64
 : 1562 - 59: **`process.elf.byte_order`** :   Byte sequence of 
 : 1563 - 13: type: keyword
 : 1564 - 22: example: Little Endian
 : 1565 - 56: **`process.elf.cpu_type`** :   CPU type of the ELF
 : 1566 - 13: type: keyword
 : 1567 - 14: example: Intel
 : 1568 - 168: **`process.elf.creation_date`** :   Extracted when
 : 1569 - 10: type: date
 : 1570 - 71: **`process.elf.exports`** :   List of exported ele
 : 1571 - 15: type: flattened
 : 1572 - 95: **`process.elf.header.abi_version`** :   Version o
 : 1573 - 13: type: keyword
 : 1574 - 64: **`process.elf.header.class`** :   Header class of
 : 1575 - 13: type: keyword
 : 1576 - 63: **`process.elf.header.data`** :   Data table of th
 : 1577 - 13: type: keyword
 : 1578 - 74: **`process.elf.header.entrypoint`** :   Header ent
 : 1579 - 10: type: long
 : 1580 - 14: format: string
 : 1581 - 73: **`process.elf.header.object_version`** :   "0x1" 
 : 1582 - 13: type: keyword
 : 1583 - 87: **`process.elf.header.os_abi`** :   Application Bi
 : 1584 - 13: type: keyword
 : 1585 - 62: **`process.elf.header.type`** :   Header type of t
 : 1586 - 13: type: keyword
 : 1587 - 63: **`process.elf.header.version`** :   Version of th
 : 1588 - 13: type: keyword
 : 1589 - 71: **`process.elf.imports`** :   List of imported ele
 : 1590 - 15: type: flattened
 : 1591 - 199: **`process.elf.sections`** :   An array containing
 : 1592 - 12: type: nested
 : 1593 - 87: **`process.elf.sections.chi2`** :   Chi-square pro
 : 1594 - 10: type: long
 : 1595 - 14: format: number
 : 1596 - 84: **`process.elf.sections.entropy`** :   Shannon ent
 : 1597 - 10: type: long
 : 1598 - 14: format: number
 : 1599 - 60: **`process.elf.sections.flags`** :   ELF Section L
 : 1600 - 13: type: keyword
 : 1601 - 58: **`process.elf.sections.name`** :   ELF Section Li
 : 1602 - 13: type: keyword
 : 1603 - 71: **`process.elf.sections.physical_offset`** :   ELF
 : 1604 - 13: type: keyword
 : 1605 - 76: **`process.elf.sections.physical_size`** :   ELF S
 : 1606 - 10: type: long
 : 1607 - 13: format: bytes
 : 1608 - 58: **`process.elf.sections.type`** :   ELF Section Li
 : 1609 - 13: type: keyword
 : 1610 - 80: **`process.elf.sections.virtual_address`** :   ELF
 : 1611 - 10: type: long
 : 1612 - 14: format: string
 : 1613 - 74: **`process.elf.sections.virtual_size`** :   ELF Se
 : 1614 - 10: type: long
 : 1615 - 14: format: string
 : 1616 - 199: **`process.elf.segments`** :   An array containing
 : 1617 - 12: type: nested
 : 1618 - 68: **`process.elf.segments.sections`** :   ELF object
 : 1619 - 13: type: keyword
 : 1620 - 60: **`process.elf.segments.type`** :   ELF object seg
 : 1621 - 13: type: keyword
 : 1622 - 88: **`process.elf.shared_libraries`** :   List of sha
 : 1623 - 13: type: keyword
 : 1624 - 65: **`process.elf.telfhash`** :   telfhash symbol has
 : 1625 - 13: type: keyword
 : 1626 - 49: **`process.end`** :   The time the process ended.
 : 1627 - 10: type: date
 : 1628 - 33: example: 2016-05-23T08:05:34.853Z
 : 1629 - 454: **`process.entity_id`** :   Unique identifier for 
 : 1630 - 13: type: keyword
 : 1631 - 24: example: c2c455d9f99375d
 : 1632 - 69: **`process.executable`** :   Absolute path to the 
 : 1633 - 13: type: keyword
 : 1634 - 21: example: /usr/bin/ssh
 : 1635 - 55: **`process.executable.text`** :   type: match_only
 : 1636 - 177: **`process.exit_code`** :   The exit code of the p
 : 1637 - 10: type: long
 : 1638 - 12: example: 137
 : 1639 - 36: **`process.hash.md5`** :   MD5 hash.
 : 1640 - 13: type: keyword
 : 1641 - 38: **`process.hash.sha1`** :   SHA1 hash.
 : 1642 - 13: type: keyword
 : 1643 - 42: **`process.hash.sha256`** :   SHA256 hash.
 : 1644 - 13: type: keyword
 : 1645 - 42: **`process.hash.sha512`** :   SHA512 hash.
 : 1646 - 13: type: keyword
 : 1647 - 42: **`process.hash.ssdeep`** :   SSDEEP hash.
 : 1648 - 13: type: keyword
 : 1649 - 78: **`process.name`** :   Process name. Sometimes cal
 : 1650 - 13: type: keyword
 : 1651 - 12: example: ssh
 : 1652 - 49: **`process.name.text`** :   type: match_only_text
 : 1653 - 158: **`process.parent.args`** :   Array of process arg
 : 1654 - 13: type: keyword
 : 1655 - 52: example: ["/usr/bin/ssh", "-l", "user", "10.0.0.16
 : 1656 - 253: **`process.parent.args_count`** :   Length of the 
 : 1657 - 10: type: long
 : 1658 - 10: example: 4
 : 1659 - 237: **`process.parent.code_signature.digest_algorithm`
 : 1660 - 13: type: keyword
 : 1661 - 15: example: sha256
 : 1662 - 92: **`process.parent.code_signature.exists`** :   Boo
 : 1663 - 13: type: boolean
 : 1664 - 13: example: true
 : 1665 - 208: **`process.parent.code_signature.signing_id`** :  
 : 1666 - 13: type: keyword
 : 1667 - 28: example: com.apple.xpc.proxy
 : 1668 - 271: **`process.parent.code_signature.status`** :   Add
 : 1669 - 13: type: keyword
 : 1670 - 29: example: ERROR_UNTRUSTED_ROOT
 : 1671 - 84: **`process.parent.code_signature.subject_name`** :
 : 1672 - 13: type: keyword
 : 1673 - 30: example: Microsoft Corporation
 : 1674 - 201: **`process.parent.code_signature.team_id`** :   Th
 : 1675 - 13: type: keyword
 : 1676 - 19: example: EQHXZ8M8AV
 : 1677 - 113: **`process.parent.code_signature.timestamp`** :   
 : 1678 - 10: type: date
 : 1679 - 29: example: 2021-01-01T12:10:30Z
 : 1680 - 244: **`process.parent.code_signature.trusted`** :   St
 : 1681 - 13: type: boolean
 : 1682 - 13: example: true
 : 1683 - 179: **`process.parent.code_signature.valid`** :   Bool
 : 1684 - 13: type: boolean
 : 1685 - 13: example: true
 : 1686 - 212: **`process.parent.command_line`** :   Full command
 : 1687 - 14: type: wildcard
 : 1688 - 39: example: /usr/bin/ssh -l user 10.0.0.16
 : 1689 - 64: **`process.parent.command_line.text`** :   type: m
 : 1690 - 79: **`process.parent.elf.architecture`** :   Machine 
 : 1691 - 13: type: keyword
 : 1692 - 15: example: x86-64
 : 1693 - 66: **`process.parent.elf.byte_order`** :   Byte seque
 : 1694 - 13: type: keyword
 : 1695 - 22: example: Little Endian
 : 1696 - 63: **`process.parent.elf.cpu_type`** :   CPU type of 
 : 1697 - 13: type: keyword
 : 1698 - 14: example: Intel
 : 1699 - 175: **`process.parent.elf.creation_date`** :   Extract
 : 1700 - 10: type: date
 : 1701 - 78: **`process.parent.elf.exports`** :   List of expor
 : 1702 - 15: type: flattened
 : 1703 - 102: **`process.parent.elf.header.abi_version`** :   Ve
 : 1704 - 13: type: keyword
 : 1705 - 71: **`process.parent.elf.header.class`** :   Header c
 : 1706 - 13: type: keyword
 : 1707 - 70: **`process.parent.elf.header.data`** :   Data tabl
 : 1708 - 13: type: keyword
 : 1709 - 81: **`process.parent.elf.header.entrypoint`** :   Hea
 : 1710 - 10: type: long
 : 1711 - 14: format: string
 : 1712 - 80: **`process.parent.elf.header.object_version`** :  
 : 1713 - 13: type: keyword
 : 1714 - 94: **`process.parent.elf.header.os_abi`** :   Applica
 : 1715 - 13: type: keyword
 : 1716 - 69: **`process.parent.elf.header.type`** :   Header ty
 : 1717 - 13: type: keyword
 : 1718 - 70: **`process.parent.elf.header.version`** :   Versio
 : 1719 - 13: type: keyword
 : 1720 - 78: **`process.parent.elf.imports`** :   List of impor
 : 1721 - 15: type: flattened
 : 1722 - 206: **`process.parent.elf.sections`** :   An array con
 : 1723 - 12: type: nested
 : 1724 - 94: **`process.parent.elf.sections.chi2`** :   Chi-squ
 : 1725 - 10: type: long
 : 1726 - 14: format: number
 : 1727 - 91: **`process.parent.elf.sections.entropy`** :   Shan
 : 1728 - 10: type: long
 : 1729 - 14: format: number
 : 1730 - 67: **`process.parent.elf.sections.flags`** :   ELF Se
 : 1731 - 13: type: keyword
 : 1732 - 65: **`process.parent.elf.sections.name`** :   ELF Sec
 : 1733 - 13: type: keyword
 : 1734 - 78: **`process.parent.elf.sections.physical_offset`** 
 : 1735 - 13: type: keyword
 : 1736 - 83: **`process.parent.elf.sections.physical_size`** : 
 : 1737 - 10: type: long
 : 1738 - 13: format: bytes
 : 1739 - 65: **`process.parent.elf.sections.type`** :   ELF Sec
 : 1740 - 13: type: keyword
 : 1741 - 87: **`process.parent.elf.sections.virtual_address`** 
 : 1742 - 10: type: long
 : 1743 - 14: format: string
 : 1744 - 81: **`process.parent.elf.sections.virtual_size`** :  
 : 1745 - 10: type: long
 : 1746 - 14: format: string
 : 1747 - 206: **`process.parent.elf.segments`** :   An array con
 : 1748 - 12: type: nested
 : 1749 - 75: **`process.parent.elf.segments.sections`** :   ELF
 : 1750 - 13: type: keyword
 : 1751 - 67: **`process.parent.elf.segments.type`** :   ELF obj
 : 1752 - 13: type: keyword
 : 1753 - 95: **`process.parent.elf.shared_libraries`** :   List
 : 1754 - 13: type: keyword
 : 1755 - 72: **`process.parent.elf.telfhash`** :   telfhash sym
 : 1756 - 13: type: keyword
 : 1757 - 56: **`process.parent.end`** :   The time the process 
 : 1758 - 10: type: date
 : 1759 - 33: example: 2016-05-23T08:05:34.853Z
 : 1760 - 461: **`process.parent.entity_id`** :   Unique identifi
 : 1761 - 13: type: keyword
 : 1762 - 24: example: c2c455d9f99375d
 : 1763 - 76: **`process.parent.executable`** :   Absolute path 
 : 1764 - 13: type: keyword
 : 1765 - 21: example: /usr/bin/ssh
 : 1766 - 62: **`process.parent.executable.text`** :   type: mat
 : 1767 - 184: **`process.parent.exit_code`** :   The exit code o
 : 1768 - 10: type: long
 : 1769 - 12: example: 137
 : 1770 - 43: **`process.parent.hash.md5`** :   MD5 hash.
 : 1771 - 13: type: keyword
 : 1772 - 45: **`process.parent.hash.sha1`** :   SHA1 hash.
 : 1773 - 13: type: keyword
 : 1774 - 49: **`process.parent.hash.sha256`** :   SHA256 hash.
 : 1775 - 13: type: keyword
 : 1776 - 49: **`process.parent.hash.sha512`** :   SHA512 hash.
 : 1777 - 13: type: keyword
 : 1778 - 49: **`process.parent.hash.ssdeep`** :   SSDEEP hash.
 : 1779 - 13: type: keyword
 : 1780 - 85: **`process.parent.name`** :   Process name. Someti
 : 1781 - 13: type: keyword
 : 1782 - 12: example: ssh
 : 1783 - 56: **`process.parent.name.text`** :   type: match_onl
 : 1784 - 78: **`process.parent.pe.architecture`** :   CPU archi
 : 1785 - 13: type: keyword
 : 1786 - 12: example: x64
 : 1787 - 96: **`process.parent.pe.company`** :   Internal compa
 : 1788 - 13: type: keyword
 : 1789 - 30: example: Microsoft Corporation
 : 1790 - 99: **`process.parent.pe.description`** :   Internal d
 : 1791 - 13: type: keyword
 : 1792 - 14: example: Paint
 : 1793 - 96: **`process.parent.pe.file_version`** :   Internal 
 : 1794 - 13: type: keyword
 : 1795 - 23: example: 6.3.9600.17415
 : 1796 - 368: **`process.parent.pe.imphash`** :   A hash of the 
 : 1797 - 13: type: keyword
 : 1798 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 1799 - 99: **`process.parent.pe.original_file_name`** :   Int
 : 1800 - 13: type: keyword
 : 1801 - 20: example: MSPAINT.EXE
 : 1802 - 96: **`process.parent.pe.product`** :   Internal produ
 : 1803 - 13: type: keyword
 : 1804 - 45: example: Microsoft® Windows® Operating System
 : 1805 - 90: **`process.parent.pgid`** :   Identifier of the gr
 : 1806 - 10: type: long
 : 1807 - 14: format: string
 : 1808 - 40: **`process.parent.pid`** :   Process id.
 : 1809 - 10: type: long
 : 1810 - 13: example: 4242
 : 1811 - 14: format: string
 : 1812 - 60: **`process.parent.start`** :   The time the proces
 : 1813 - 10: type: date
 : 1814 - 33: example: 2016-05-23T08:05:34.853Z
 : 1815 - 45: **`process.parent.thread.id`** :   Thread ID.
 : 1816 - 10: type: long
 : 1817 - 13: example: 4242
 : 1818 - 14: format: string
 : 1819 - 49: **`process.parent.thread.name`** :   Thread name.
 : 1820 - 13: type: keyword
 : 1821 - 17: example: thread-0
 : 1822 - 194: **`process.parent.title`** :   Process title. The 
 : 1823 - 13: type: keyword
 : 1824 - 57: **`process.parent.title.text`** :   type: match_on
 : 1825 - 64: **`process.parent.uptime`** :   Seconds the proces
 : 1826 - 10: type: long
 : 1827 - 13: example: 1325
 : 1828 - 80: **`process.parent.working_directory`** :   The wor
 : 1829 - 13: type: keyword
 : 1830 - 20: example: /home/alice
 : 1831 - 69: **`process.parent.working_directory.text`** :   ty
 : 1832 - 71: **`process.pe.architecture`** :   CPU architecture
 : 1833 - 13: type: keyword
 : 1834 - 12: example: x64
 : 1835 - 89: **`process.pe.company`** :   Internal company name
 : 1836 - 13: type: keyword
 : 1837 - 30: example: Microsoft Corporation
 : 1838 - 92: **`process.pe.description`** :   Internal descript
 : 1839 - 13: type: keyword
 : 1840 - 14: example: Paint
 : 1841 - 89: **`process.pe.file_version`** :   Internal version
 : 1842 - 13: type: keyword
 : 1843 - 23: example: 6.3.9600.17415
 : 1844 - 361: **`process.pe.imphash`** :   A hash of the imports
 : 1845 - 13: type: keyword
 : 1846 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 1847 - 92: **`process.pe.original_file_name`** :   Internal n
 : 1848 - 13: type: keyword
 : 1849 - 20: example: MSPAINT.EXE
 : 1850 - 89: **`process.pe.product`** :   Internal product name
 : 1851 - 13: type: keyword
 : 1852 - 45: example: Microsoft® Windows® Operating System
 : 1853 - 83: **`process.pgid`** :   Identifier of the group of 
 : 1854 - 10: type: long
 : 1855 - 14: format: string
 : 1856 - 33: **`process.pid`** :   Process id.
 : 1857 - 10: type: long
 : 1858 - 13: example: 4242
 : 1859 - 14: format: string
 : 1860 - 53: **`process.start`** :   The time the process start
 : 1861 - 10: type: date
 : 1862 - 33: example: 2016-05-23T08:05:34.853Z
 : 1863 - 38: **`process.thread.id`** :   Thread ID.
 : 1864 - 10: type: long
 : 1865 - 13: example: 4242
 : 1866 - 14: format: string
 : 1867 - 42: **`process.thread.name`** :   Thread name.
 : 1868 - 13: type: keyword
 : 1869 - 17: example: thread-0
 : 1870 - 187: **`process.title`** :   Process title. The proctit
 : 1871 - 13: type: keyword
 : 1872 - 50: **`process.title.text`** :   type: match_only_text
 : 1873 - 57: **`process.uptime`** :   Seconds the process has b
 : 1874 - 10: type: long
 : 1875 - 13: example: 1325
 : 1876 - 73: **`process.working_directory`** :   The working di
 : 1877 - 13: type: keyword
 : 1878 - 20: example: /home/alice
 : 1879 - 62: **`process.working_directory.text`** :   type: mat
 : 1880 - 23: ## registry [_registry]
 : 1881 - 46: Fields related to Windows Registry operations.
 : 1882 - 306: **`registry.data.bytes`** :   Original bytes writt
 : 1883 - 13: type: keyword
 : 1884 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
 : 1885 - 430: **`registry.data.strings`** :   Content when writi
 : 1886 - 14: type: wildcard
 : 1887 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
 : 1888 - 73: **`registry.data.type`** :   Standard registry typ
 : 1889 - 13: type: keyword
 : 1890 - 15: example: REG_SZ
 : 1891 - 54: **`registry.hive`** :   Abbreviated name for the h
 : 1892 - 13: type: keyword
 : 1893 - 13: example: HKLM
 : 1894 - 50: **`registry.key`** :   Hive-relative path of keys.
 : 1895 - 13: type: keyword
 : 1896 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
 : 1897 - 64: **`registry.path`** :   Full path, including hive,
 : 1898 - 13: type: keyword
 : 1899 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
 : 1900 - 51: **`registry.value`** :   Name of the value written
 : 1901 - 13: type: keyword
 : 1902 - 17: example: Debugger
 : 1903 - 21: ## related [_related]
 : 1904 - 541: This field set is meant to facilitate pivoting aro
 : 1905 - 227: **`related.hash`** :   All the hashes seen on your
 : 1906 - 13: type: keyword
 : 1907 - 163: **`related.hosts`** :   All hostnames or other hos
 : 1908 - 13: type: keyword
 : 1909 - 55: **`related.ip`** :   All of the IPs seen on your e
 : 1910 - 8: type: ip
 : 1911 - 86: **`related.user`** :   All the user names or other
 : 1912 - 13: type: keyword
 : 1913 - 15: ## rule [_rule]
 : 1914 - 365: Rule fields are used to capture the specifics of a
 : 1915 - 129: **`rule.author`** :   Name, organization, or pseud
 : 1916 - 13: type: keyword
 : 1917 - 22: example: ["Star-Lord"]
 : 1918 - 117: **`rule.category`** :   A categorization value key
 : 1919 - 13: type: keyword
 : 1920 - 35: example: Attempted Information Leak
 : 1921 - 76: **`rule.description`** :   The description of the 
 : 1922 - 13: type: keyword
 : 1923 - 64: example: Block requests to public DNS over HTTPS /
 : 1924 - 142: **`rule.id`** :   A rule ID that is unique within 
 : 1925 - 13: type: keyword
 : 1926 - 12: example: 101
 : 1927 - 110: **`rule.license`** :   Name of the license under w
 : 1928 - 13: type: keyword
 : 1929 - 19: example: Apache 2.0
 : 1930 - 75: **`rule.name`** :   The name of the rule or signat
 : 1931 - 13: type: keyword
 : 1932 - 27: example: BLOCK_DNS_over_TLS
 : 1933 - 273: **`rule.reference`** :   Reference URL to addition
 : 1934 - 13: type: keyword
 : 1935 - 51: example: https://en.wikipedia.org/wiki/DNS_over_TL
 : 1936 - 136: **`rule.ruleset`** :   Name of the ruleset, policy
 : 1937 - 13: type: keyword
 : 1938 - 34: example: Standard_Protocol_Filters
 : 1939 - 163: **`rule.uuid`** :   A rule ID that is unique withi
 : 1940 - 13: type: keyword
 : 1941 - 19: example: 1100110011
 : 1942 - 82: **`rule.version`** :   The version / revision of t
 : 1943 - 13: type: keyword
 : 1944 - 12: example: 1.1
 : 1945 - 19: ## server [_server]
 : 1946 - 890: A Server is defined as the responder in a network 
 : 1947 - 290: **`server.address`** :   Some event server address
 : 1948 - 13: type: keyword
 : 1949 - 161: **`server.as.number`** :   Unique number allocated
 : 1950 - 10: type: long
 : 1951 - 14: example: 15169
 : 1952 - 56: **`server.as.organization.name`** :   Organization
 : 1953 - 13: type: keyword
 : 1954 - 19: example: Google LLC
 : 1955 - 64: **`server.as.organization.name.text`** :   type: m
 : 1956 - 64: **`server.bytes`** :   Bytes sent from the server 
 : 1957 - 10: type: long
 : 1958 - 12: example: 184
 : 1959 - 13: format: bytes
 : 1960 - 228: **`server.domain`** :   The domain name of the ser
 : 1961 - 13: type: keyword
 : 1962 - 24: example: foo.example.com
 : 1963 - 41: **`server.geo.city_name`** :   City name.
 : 1964 - 13: type: keyword
 : 1965 - 17: example: Montreal
 : 1966 - 82: **`server.geo.continent_code`** :   Two-letter cod
 : 1967 - 13: type: keyword
 : 1968 - 11: example: NA
 : 1969 - 58: **`server.geo.continent_name`** :   Name of the co
 : 1970 - 13: type: keyword
 : 1971 - 22: example: North America
 : 1972 - 55: **`server.geo.country_iso_code`** :   Country ISO 
 : 1973 - 13: type: keyword
 : 1974 - 11: example: CA
 : 1975 - 47: **`server.geo.country_name`** :   Country name.
 : 1976 - 13: type: keyword
 : 1977 - 15: example: Canada
 : 1978 - 53: **`server.geo.location`** :   Longitude and latitu
 : 1979 - 15: type: geo_point
 : 1980 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 1981 - 269: **`server.geo.name`** :   User-defined description
 : 1982 - 13: type: keyword
 : 1983 - 18: example: boston-dc
 : 1984 - 198: **`server.geo.postal_code`** :   Postal code assoc
 : 1985 - 13: type: keyword
 : 1986 - 14: example: 94040
 : 1987 - 53: **`server.geo.region_iso_code`** :   Region ISO co
 : 1988 - 13: type: keyword
 : 1989 - 14: example: CA-QC
 : 1990 - 45: **`server.geo.region_name`** :   Region name.
 : 1991 - 13: type: keyword
 : 1992 - 15: example: Quebec
 : 1993 - 89: **`server.geo.timezone`** :   The time zone of the
 : 1994 - 13: type: keyword
 : 1995 - 39: example: America/Argentina/Buenos_Aires
 : 1996 - 60: **`server.ip`** :   IP address of the server (IPv4
 : 1997 - 8: type: ip
 : 1998 - 280: **`server.mac`** :   MAC address of the server. Th
 : 1999 - 13: type: keyword
 : 2000 - 26: example: 00-00-5E-00-53-23
 : 2001 - 161: **`server.nat.ip`** :   Translated ip of destinati
 : 2002 - 8: type: ip
 : 2003 - 165: **`server.nat.port`** :   Translated port of desti
 : 2004 - 10: type: long
 : 2005 - 14: format: string
 : 2006 - 68: **`server.packets`** :   Packets sent from the ser
 : 2007 - 10: type: long
 : 2008 - 11: example: 12
 : 2009 - 41: **`server.port`** :   Port of the server.
 : 2010 - 10: type: long
 : 2011 - 14: format: string
 : 2012 - 391: **`server.registered_domain`** :   The highest reg
 : 2013 - 13: type: keyword
 : 2014 - 20: example: example.com
 : 2015 - 557: **`server.subdomain`** :   The subdomain portion o
 : 2016 - 13: type: keyword
 : 2017 - 13: example: east
 : 2018 - 424: **`server.top_level_domain`** :   The effective to
 : 2019 - 13: type: keyword
 : 2020 - 14: example: co.uk
 : 2021 - 129: **`server.user.domain`** :   Name of the directory
 : 2022 - 13: type: keyword
 : 2023 - 47: **`server.user.email`** :   User email address.
 : 2024 - 13: type: keyword
 : 2025 - 63: **`server.user.full_name`** :   User’s full name, 
 : 2026 - 13: type: keyword
 : 2027 - 24: example: Albert Einstein
 : 2028 - 58: **`server.user.full_name.text`** :   type: match_o
 : 2029 - 136: **`server.user.group.domain`** :   Name of the dir
 : 2030 - 13: type: keyword
 : 2031 - 86: **`server.user.group.id`** :   Unique identifier f
 : 2032 - 13: type: keyword
 : 2033 - 51: **`server.user.group.name`** :   Name of the group
 : 2034 - 13: type: keyword
 : 2035 - 187: **`server.user.hash`** :   Unique user hash to cor
 : 2036 - 13: type: keyword
 : 2037 - 55: **`server.user.id`** :   Unique identifier of the 
 : 2038 - 13: type: keyword
 : 2039 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 2040 - 59: **`server.user.name`** :   Short name or login of 
 : 2041 - 13: type: keyword
 : 2042 - 19: example: a.einstein
 : 2043 - 53: **`server.user.name.text`** :   type: match_only_t
 : 2044 - 73: **`server.user.roles`** :   Array of user roles at
 : 2045 - 13: type: keyword
 : 2046 - 43: example: ["kibana_admin", "reporting_user"]
 : 2047 - 21: ## service [_service]
 : 2048 - 163: The service fields describe the service for or fro
 : 2049 - 178: **`service.address`** :   Address where data about
 : 2050 - 13: type: keyword
 : 2051 - 24: example: 172.26.0.2:5432
 : 2052 - 317: **`service.environment`** :   Identifies the envir
 : 2053 - 13: type: keyword
 : 2054 - 19: example: production
 : 2055 - 153: **`service.ephemeral_id`** :   Ephemeral identifie
 : 2056 - 13: type: keyword
 : 2057 - 17: example: 8a4f500f
 : 2058 - 471: **`service.id`** :   Unique identifier of the runn
 : 2059 - 13: type: keyword
 : 2060 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
 : 2061 - 415: **`service.name`** :   Name of the service data is
 : 2062 - 13: type: keyword
 : 2063 - 30: example: elasticsearch-metrics
 : 2064 - 668: **`service.node.name`** :   Name of a service node
 : 2065 - 13: type: keyword
 : 2066 - 28: example: instance-0000000016
 : 2067 - 185: **`service.origin.address`** :   Address where dat
 : 2068 - 13: type: keyword
 : 2069 - 24: example: 172.26.0.2:5432
 : 2070 - 324: **`service.origin.environment`** :   Identifies th
 : 2071 - 13: type: keyword
 : 2072 - 19: example: production
 : 2073 - 160: **`service.origin.ephemeral_id`** :   Ephemeral id
 : 2074 - 13: type: keyword
 : 2075 - 17: example: 8a4f500f
 : 2076 - 478: **`service.origin.id`** :   Unique identifier of t
 : 2077 - 13: type: keyword
 : 2078 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
 : 2079 - 422: **`service.origin.name`** :   Name of the service 
 : 2080 - 13: type: keyword
 : 2081 - 30: example: elasticsearch-metrics
 : 2082 - 675: **`service.origin.node.name`** :   Name of a servi
 : 2083 - 13: type: keyword
 : 2084 - 28: example: instance-0000000016
 : 2085 - 60: **`service.origin.state`** :   Current state of th
 : 2086 - 13: type: keyword
 : 2087 - 265: **`service.origin.type`** :   The type of the serv
 : 2088 - 13: type: keyword
 : 2089 - 22: example: elasticsearch
 : 2090 - 160: **`service.origin.version`** :   Version of the se
 : 2091 - 13: type: keyword
 : 2092 - 14: example: 3.2.4
 : 2093 - 53: **`service.state`** :   Current state of the servi
 : 2094 - 13: type: keyword
 : 2095 - 185: **`service.target.address`** :   Address where dat
 : 2096 - 13: type: keyword
 : 2097 - 24: example: 172.26.0.2:5432
 : 2098 - 324: **`service.target.environment`** :   Identifies th
 : 2099 - 13: type: keyword
 : 2100 - 19: example: production
 : 2101 - 160: **`service.target.ephemeral_id`** :   Ephemeral id
 : 2102 - 13: type: keyword
 : 2103 - 17: example: 8a4f500f
 : 2104 - 478: **`service.target.id`** :   Unique identifier of t
 : 2105 - 13: type: keyword
 : 2106 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
 : 2107 - 422: **`service.target.name`** :   Name of the service 
 : 2108 - 13: type: keyword
 : 2109 - 30: example: elasticsearch-metrics
 : 2110 - 675: **`service.target.node.name`** :   Name of a servi
 : 2111 - 13: type: keyword
 : 2112 - 28: example: instance-0000000016
 : 2113 - 60: **`service.target.state`** :   Current state of th
 : 2114 - 13: type: keyword
 : 2115 - 265: **`service.target.type`** :   The type of the serv
 : 2116 - 13: type: keyword
 : 2117 - 22: example: elasticsearch
 : 2118 - 160: **`service.target.version`** :   Version of the se
 : 2119 - 13: type: keyword
 : 2120 - 14: example: 3.2.4
 : 2121 - 258: **`service.type`** :   The type of the service dat
 : 2122 - 13: type: keyword
 : 2123 - 22: example: elasticsearch
 : 2124 - 153: **`service.version`** :   Version of the service t
 : 2125 - 13: type: keyword
 : 2126 - 14: example: 3.2.4
 : 2127 - 21: ## source [_source_2]
 : 2128 - 573: Source fields capture details about the sender of 
 : 2129 - 290: **`source.address`** :   Some event source address
 : 2130 - 13: type: keyword
 : 2131 - 161: **`source.as.number`** :   Unique number allocated
 : 2132 - 10: type: long
 : 2133 - 14: example: 15169
 : 2134 - 56: **`source.as.organization.name`** :   Organization
 : 2135 - 13: type: keyword
 : 2136 - 19: example: Google LLC
 : 2137 - 64: **`source.as.organization.name.text`** :   type: m
 : 2138 - 69: **`source.bytes`** :   Bytes sent from the source 
 : 2139 - 10: type: long
 : 2140 - 12: example: 184
 : 2141 - 13: format: bytes
 : 2142 - 228: **`source.domain`** :   The domain name of the sou
 : 2143 - 13: type: keyword
 : 2144 - 24: example: foo.example.com
 : 2145 - 41: **`source.geo.city_name`** :   City name.
 : 2146 - 13: type: keyword
 : 2147 - 17: example: Montreal
 : 2148 - 82: **`source.geo.continent_code`** :   Two-letter cod
 : 2149 - 13: type: keyword
 : 2150 - 11: example: NA
 : 2151 - 58: **`source.geo.continent_name`** :   Name of the co
 : 2152 - 13: type: keyword
 : 2153 - 22: example: North America
 : 2154 - 55: **`source.geo.country_iso_code`** :   Country ISO 
 : 2155 - 13: type: keyword
 : 2156 - 11: example: CA
 : 2157 - 47: **`source.geo.country_name`** :   Country name.
 : 2158 - 13: type: keyword
 : 2159 - 15: example: Canada
 : 2160 - 53: **`source.geo.location`** :   Longitude and latitu
 : 2161 - 15: type: geo_point
 : 2162 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 2163 - 269: **`source.geo.name`** :   User-defined description
 : 2164 - 13: type: keyword
 : 2165 - 18: example: boston-dc
 : 2166 - 198: **`source.geo.postal_code`** :   Postal code assoc
 : 2167 - 13: type: keyword
 : 2168 - 14: example: 94040
 : 2169 - 53: **`source.geo.region_iso_code`** :   Region ISO co
 : 2170 - 13: type: keyword
 : 2171 - 14: example: CA-QC
 : 2172 - 45: **`source.geo.region_name`** :   Region name.
 : 2173 - 13: type: keyword
 : 2174 - 15: example: Quebec
 : 2175 - 89: **`source.geo.timezone`** :   The time zone of the
 : 2176 - 13: type: keyword
 : 2177 - 39: example: America/Argentina/Buenos_Aires
 : 2178 - 60: **`source.ip`** :   IP address of the source (IPv4
 : 2179 - 8: type: ip
 : 2180 - 280: **`source.mac`** :   MAC address of the source. Th
 : 2181 - 13: type: keyword
 : 2182 - 26: example: 00-00-5E-00-53-23
 : 2183 - 173: **`source.nat.ip`** :   Translated ip of source ba
 : 2184 - 8: type: ip
 : 2185 - 165: **`source.nat.port`** :   Translated port of sourc
 : 2186 - 10: type: long
 : 2187 - 14: format: string
 : 2188 - 73: **`source.packets`** :   Packets sent from the sou
 : 2189 - 10: type: long
 : 2190 - 11: example: 12
 : 2191 - 41: **`source.port`** :   Port of the source.
 : 2192 - 10: type: long
 : 2193 - 14: format: string
 : 2194 - 391: **`source.registered_domain`** :   The highest reg
 : 2195 - 13: type: keyword
 : 2196 - 20: example: example.com
 : 2197 - 557: **`source.subdomain`** :   The subdomain portion o
 : 2198 - 13: type: keyword
 : 2199 - 13: example: east
 : 2200 - 424: **`source.top_level_domain`** :   The effective to
 : 2201 - 13: type: keyword
 : 2202 - 14: example: co.uk
 : 2203 - 129: **`source.user.domain`** :   Name of the directory
 : 2204 - 13: type: keyword
 : 2205 - 47: **`source.user.email`** :   User email address.
 : 2206 - 13: type: keyword
 : 2207 - 63: **`source.user.full_name`** :   User’s full name, 
 : 2208 - 13: type: keyword
 : 2209 - 24: example: Albert Einstein
 : 2210 - 58: **`source.user.full_name.text`** :   type: match_o
 : 2211 - 136: **`source.user.group.domain`** :   Name of the dir
 : 2212 - 13: type: keyword
 : 2213 - 86: **`source.user.group.id`** :   Unique identifier f
 : 2214 - 13: type: keyword
 : 2215 - 51: **`source.user.group.name`** :   Name of the group
 : 2216 - 13: type: keyword
 : 2217 - 187: **`source.user.hash`** :   Unique user hash to cor
 : 2218 - 13: type: keyword
 : 2219 - 55: **`source.user.id`** :   Unique identifier of the 
 : 2220 - 13: type: keyword
 : 2221 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 2222 - 59: **`source.user.name`** :   Short name or login of 
 : 2223 - 13: type: keyword
 : 2224 - 19: example: a.einstein
 : 2225 - 53: **`source.user.name.text`** :   type: match_only_t
 : 2226 - 73: **`source.user.roles`** :   Array of user roles at
 : 2227 - 13: type: keyword
 : 2228 - 43: example: ["kibana_admin", "reporting_user"]
 : 2229 - 19: ## threat [_threat]
 : 2230 - 495: Fields to classify events and alerts according to 
 : 2231 - 137: **`threat.enrichments`** :   A list of associated 
 : 2232 - 12: type: nested
 : 2233 - 99: **`threat.enrichments.indicator`** :   Object cont
 : 2234 - 12: type: object
 : 2235 - 183: **`threat.enrichments.indicator.as.number`** :   U
 : 2236 - 10: type: long
 : 2237 - 14: example: 15169
 : 2238 - 78: **`threat.enrichments.indicator.as.organization.na
 : 2239 - 13: type: keyword
 : 2240 - 19: example: Google LLC
 : 2241 - 86: **`threat.enrichments.indicator.as.organization.na
 : 2242 - 314: **`threat.enrichments.indicator.confidence`** :   
 : 2243 - 13: type: keyword
 : 2244 - 15: example: Medium
 : 2245 - 104: **`threat.enrichments.indicator.description`** :  
 : 2246 - 13: type: keyword
 : 2247 - 58: example: IP x.x.x.x was observed delivering the An
 : 2248 - 131: **`threat.enrichments.indicator.email.address`** :
 : 2249 - 13: type: keyword
 : 2250 - 28: example: `phish@example.com`
 : 2251 - 142: **`threat.enrichments.indicator.file.accessed`** :
 : 2252 - 10: type: date
 : 2253 - 283: **`threat.enrichments.indicator.file.attributes`**
 : 2254 - 13: type: keyword
 : 2255 - 31: example: ["readonly", "system"]
 : 2256 - 256: **`threat.enrichments.indicator.file.code_signatur
 : 2257 - 13: type: keyword
 : 2258 - 15: example: sha256
 : 2259 - 111: **`threat.enrichments.indicator.file.code_signatur
 : 2260 - 13: type: boolean
 : 2261 - 13: example: true
 : 2262 - 227: **`threat.enrichments.indicator.file.code_signatur
 : 2263 - 13: type: keyword
 : 2264 - 28: example: com.apple.xpc.proxy
 : 2265 - 290: **`threat.enrichments.indicator.file.code_signatur
 : 2266 - 13: type: keyword
 : 2267 - 29: example: ERROR_UNTRUSTED_ROOT
 : 2268 - 103: **`threat.enrichments.indicator.file.code_signatur
 : 2269 - 13: type: keyword
 : 2270 - 30: example: Microsoft Corporation
 : 2271 - 220: **`threat.enrichments.indicator.file.code_signatur
 : 2272 - 13: type: keyword
 : 2273 - 19: example: EQHXZ8M8AV
 : 2274 - 132: **`threat.enrichments.indicator.file.code_signatur
 : 2275 - 10: type: date
 : 2276 - 29: example: 2021-01-01T12:10:30Z
 : 2277 - 263: **`threat.enrichments.indicator.file.code_signatur
 : 2278 - 13: type: boolean
 : 2279 - 13: example: true
 : 2280 - 198: **`threat.enrichments.indicator.file.code_signatur
 : 2281 - 13: type: boolean
 : 2282 - 13: example: true
 : 2283 - 126: **`threat.enrichments.indicator.file.created`** : 
 : 2284 - 10: type: date
 : 2285 - 259: **`threat.enrichments.indicator.file.ctime`** :   
 : 2286 - 10: type: date
 : 2287 - 89: **`threat.enrichments.indicator.file.device`** :  
 : 2288 - 13: type: keyword
 : 2289 - 12: example: sda
 : 2290 - 144: **`threat.enrichments.indicator.file.directory`** 
 : 2291 - 13: type: keyword
 : 2292 - 20: example: /home/alice
 : 2293 - 194: **`threat.enrichments.indicator.file.drive_letter`
 : 2294 - 13: type: keyword
 : 2295 - 10: example: C
 : 2296 - 98: **`threat.enrichments.indicator.file.elf.architect
 : 2297 - 13: type: keyword
 : 2298 - 15: example: x86-64
 : 2299 - 85: **`threat.enrichments.indicator.file.elf.byte_orde
 : 2300 - 13: type: keyword
 : 2301 - 22: example: Little Endian
 : 2302 - 82: **`threat.enrichments.indicator.file.elf.cpu_type`
 : 2303 - 13: type: keyword
 : 2304 - 14: example: Intel
 : 2305 - 194: **`threat.enrichments.indicator.file.elf.creation_
 : 2306 - 10: type: date
 : 2307 - 97: **`threat.enrichments.indicator.file.elf.exports`*
 : 2308 - 15: type: flattened
 : 2309 - 121: **`threat.enrichments.indicator.file.elf.header.ab
 : 2310 - 13: type: keyword
 : 2311 - 90: **`threat.enrichments.indicator.file.elf.header.cl
 : 2312 - 13: type: keyword
 : 2313 - 89: **`threat.enrichments.indicator.file.elf.header.da
 : 2314 - 13: type: keyword
 : 2315 - 100: **`threat.enrichments.indicator.file.elf.header.en
 : 2316 - 10: type: long
 : 2317 - 14: format: string
 : 2318 - 99: **`threat.enrichments.indicator.file.elf.header.ob
 : 2319 - 13: type: keyword
 : 2320 - 113: **`threat.enrichments.indicator.file.elf.header.os
 : 2321 - 13: type: keyword
 : 2322 - 88: **`threat.enrichments.indicator.file.elf.header.ty
 : 2323 - 13: type: keyword
 : 2324 - 89: **`threat.enrichments.indicator.file.elf.header.ve
 : 2325 - 13: type: keyword
 : 2326 - 97: **`threat.enrichments.indicator.file.elf.imports`*
 : 2327 - 15: type: flattened
 : 2328 - 225: **`threat.enrichments.indicator.file.elf.sections`
 : 2329 - 12: type: nested
 : 2330 - 113: **`threat.enrichments.indicator.file.elf.sections.
 : 2331 - 10: type: long
 : 2332 - 14: format: number
 : 2333 - 110: **`threat.enrichments.indicator.file.elf.sections.
 : 2334 - 10: type: long
 : 2335 - 14: format: number
 : 2336 - 86: **`threat.enrichments.indicator.file.elf.sections.
 : 2337 - 13: type: keyword
 : 2338 - 84: **`threat.enrichments.indicator.file.elf.sections.
 : 2339 - 13: type: keyword
 : 2340 - 97: **`threat.enrichments.indicator.file.elf.sections.
 : 2341 - 13: type: keyword
 : 2342 - 102: **`threat.enrichments.indicator.file.elf.sections.
 : 2343 - 10: type: long
 : 2344 - 13: format: bytes
 : 2345 - 84: **`threat.enrichments.indicator.file.elf.sections.
 : 2346 - 13: type: keyword
 : 2347 - 106: **`threat.enrichments.indicator.file.elf.sections.
 : 2348 - 10: type: long
 : 2349 - 14: format: string
 : 2350 - 100: **`threat.enrichments.indicator.file.elf.sections.
 : 2351 - 10: type: long
 : 2352 - 14: format: string
 : 2353 - 225: **`threat.enrichments.indicator.file.elf.segments`
 : 2354 - 12: type: nested
 : 2355 - 94: **`threat.enrichments.indicator.file.elf.segments.
 : 2356 - 13: type: keyword
 : 2357 - 86: **`threat.enrichments.indicator.file.elf.segments.
 : 2358 - 13: type: keyword
 : 2359 - 114: **`threat.enrichments.indicator.file.elf.shared_li
 : 2360 - 13: type: keyword
 : 2361 - 91: **`threat.enrichments.indicator.file.elf.telfhash`
 : 2362 - 13: type: keyword
 : 2363 - 226: **`threat.enrichments.indicator.file.extension`** 
 : 2364 - 13: type: keyword
 : 2365 - 12: example: png
 : 2366 - 816: **`threat.enrichments.indicator.file.fork_name`** 
 : 2367 - 13: type: keyword
 : 2368 - 23: example: Zone.Identifer
 : 2369 - 83: **`threat.enrichments.indicator.file.gid`** :   Pr
 : 2370 - 13: type: keyword
 : 2371 - 13: example: 1001
 : 2372 - 81: **`threat.enrichments.indicator.file.group`** :   
 : 2373 - 13: type: keyword
 : 2374 - 14: example: alice
 : 2375 - 62: **`threat.enrichments.indicator.file.hash.md5`** :
 : 2376 - 13: type: keyword
 : 2377 - 64: **`threat.enrichments.indicator.file.hash.sha1`** 
 : 2378 - 13: type: keyword
 : 2379 - 68: **`threat.enrichments.indicator.file.hash.sha256`*
 : 2380 - 13: type: keyword
 : 2381 - 68: **`threat.enrichments.indicator.file.hash.sha512`*
 : 2382 - 13: type: keyword
 : 2383 - 68: **`threat.enrichments.indicator.file.hash.ssdeep`*
 : 2384 - 13: type: keyword
 : 2385 - 96: **`threat.enrichments.indicator.file.inode`** :   
 : 2386 - 13: type: keyword
 : 2387 - 15: example: 256383
 : 2388 - 243: **`threat.enrichments.indicator.file.mime_type`** 
 : 2389 - 13: type: keyword
 : 2390 - 90: **`threat.enrichments.indicator.file.mode`** :   M
 : 2391 - 13: type: keyword
 : 2392 - 13: example: 0640
 : 2393 - 90: **`threat.enrichments.indicator.file.mtime`** :   
 : 2394 - 10: type: date
 : 2395 - 113: **`threat.enrichments.indicator.file.name`** :   N
 : 2396 - 13: type: keyword
 : 2397 - 20: example: example.png
 : 2398 - 72: **`threat.enrichments.indicator.file.owner`** :   
 : 2399 - 13: type: keyword
 : 2400 - 14: example: alice
 : 2401 - 150: **`threat.enrichments.indicator.file.path`** :   F
 : 2402 - 13: type: keyword
 : 2403 - 32: example: /home/alice/example.png
 : 2404 - 75: **`threat.enrichments.indicator.file.path.text`** 
 : 2405 - 97: **`threat.enrichments.indicator.file.pe.architectu
 : 2406 - 13: type: keyword
 : 2407 - 12: example: x64
 : 2408 - 115: **`threat.enrichments.indicator.file.pe.company`**
 : 2409 - 13: type: keyword
 : 2410 - 30: example: Microsoft Corporation
 : 2411 - 118: **`threat.enrichments.indicator.file.pe.descriptio
 : 2412 - 13: type: keyword
 : 2413 - 14: example: Paint
 : 2414 - 115: **`threat.enrichments.indicator.file.pe.file_versi
 : 2415 - 13: type: keyword
 : 2416 - 23: example: 6.3.9600.17415
 : 2417 - 387: **`threat.enrichments.indicator.file.pe.imphash`**
 : 2418 - 13: type: keyword
 : 2419 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 2420 - 118: **`threat.enrichments.indicator.file.pe.original_f
 : 2421 - 13: type: keyword
 : 2422 - 20: example: MSPAINT.EXE
 : 2423 - 115: **`threat.enrichments.indicator.file.pe.product`**
 : 2424 - 13: type: keyword
 : 2425 - 45: example: Microsoft® Windows® Operating System
 : 2426 - 110: **`threat.enrichments.indicator.file.size`** :   F
 : 2427 - 10: type: long
 : 2428 - 14: example: 16384
 : 2429 - 81: **`threat.enrichments.indicator.file.target_path`*
 : 2430 - 13: type: keyword
 : 2431 - 82: **`threat.enrichments.indicator.file.target_path.t
 : 2432 - 83: **`threat.enrichments.indicator.file.type`** :   F
 : 2433 - 13: type: keyword
 : 2434 - 13: example: file
 : 2435 - 113: **`threat.enrichments.indicator.file.uid`** :   Th
 : 2436 - 13: type: keyword
 : 2437 - 13: example: 1001
 : 2438 - 252: **`threat.enrichments.indicator.file.x509.alternat
 : 2439 - 13: type: keyword
 : 2440 - 21: example: *.elastic.co
 : 2441 - 126: **`threat.enrichments.indicator.file.x509.issuer.c
 : 2442 - 13: type: keyword
 : 2443 - 46: example: Example SHA2 High Assurance Server CA
 : 2444 - 87: **`threat.enrichments.indicator.file.x509.issuer.c
 : 2445 - 13: type: keyword
 : 2446 - 11: example: US
 : 2447 - 132: **`threat.enrichments.indicator.file.x509.issuer.d
 : 2448 - 13: type: keyword
 : 2449 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 2450 - 91: **`threat.enrichments.indicator.file.x509.issuer.l
 : 2451 - 13: type: keyword
 : 2452 - 22: example: Mountain View
 : 2453 - 128: **`threat.enrichments.indicator.file.x509.issuer.o
 : 2454 - 13: type: keyword
 : 2455 - 20: example: Example Inc
 : 2456 - 143: **`threat.enrichments.indicator.file.x509.issuer.o
 : 2457 - 13: type: keyword
 : 2458 - 24: example: www.example.com
 : 2459 - 119: **`threat.enrichments.indicator.file.x509.issuer.s
 : 2460 - 13: type: keyword
 : 2461 - 19: example: California
 : 2462 - 119: **`threat.enrichments.indicator.file.x509.not_afte
 : 2463 - 10: type: date
 : 2464 - 34: example: 2020-07-16 03:15:39+00:00
 : 2465 - 116: **`threat.enrichments.indicator.file.x509.not_befo
 : 2466 - 10: type: date
 : 2467 - 34: example: 2019-08-16 01:40:25+00:00
 : 2468 - 112: **`threat.enrichments.indicator.file.x509.public_k
 : 2469 - 13: type: keyword
 : 2470 - 12: example: RSA
 : 2471 - 152: **`threat.enrichments.indicator.file.x509.public_k
 : 2472 - 13: type: keyword
 : 2473 - 17: example: nistp521
 : 2474 - 136: **`threat.enrichments.indicator.file.x509.public_k
 : 2475 - 10: type: long
 : 2476 - 14: example: 65537
 : 2477 - 21: Field is not indexed.
 : 2478 - 106: **`threat.enrichments.indicator.file.x509.public_k
 : 2479 - 10: type: long
 : 2480 - 13: example: 2048
 : 2481 - 232: **`threat.enrichments.indicator.file.x509.serial_n
 : 2482 - 13: type: keyword
 : 2483 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 2484 - 255: **`threat.enrichments.indicator.file.x509.signatur
 : 2485 - 13: type: keyword
 : 2486 - 19: example: SHA256-RSA
 : 2487 - 106: **`threat.enrichments.indicator.file.x509.subject.
 : 2488 - 13: type: keyword
 : 2489 - 34: example: shared.global.example.net
 : 2490 - 87: **`threat.enrichments.indicator.file.x509.subject.
 : 2491 - 13: type: keyword
 : 2492 - 11: example: US
 : 2493 - 134: **`threat.enrichments.indicator.file.x509.subject.
 : 2494 - 13: type: keyword
 : 2495 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 2496 - 92: **`threat.enrichments.indicator.file.x509.subject.
 : 2497 - 13: type: keyword
 : 2498 - 22: example: San Francisco
 : 2499 - 107: **`threat.enrichments.indicator.file.x509.subject.
 : 2500 - 13: type: keyword
 : 2501 - 22: example: Example, Inc.
 : 2502 - 122: **`threat.enrichments.indicator.file.x509.subject.
 : 2503 - 13: type: keyword
 : 2504 - 120: **`threat.enrichments.indicator.file.x509.subject.
 : 2505 - 13: type: keyword
 : 2506 - 19: example: California
 : 2507 - 87: **`threat.enrichments.indicator.file.x509.version_
 : 2508 - 13: type: keyword
 : 2509 - 10: example: 3
 : 2510 - 132: **`threat.enrichments.indicator.first_seen`** :   
 : 2511 - 10: type: date
 : 2512 - 33: example: 2020-11-05T17:25:47.000Z
 : 2513 - 63: **`threat.enrichments.indicator.geo.city_name`** :
 : 2514 - 13: type: keyword
 : 2515 - 17: example: Montreal
 : 2516 - 104: **`threat.enrichments.indicator.geo.continent_code
 : 2517 - 13: type: keyword
 : 2518 - 11: example: NA
 : 2519 - 80: **`threat.enrichments.indicator.geo.continent_name
 : 2520 - 13: type: keyword
 : 2521 - 22: example: North America
 : 2522 - 77: **`threat.enrichments.indicator.geo.country_iso_co
 : 2523 - 13: type: keyword
 : 2524 - 11: example: CA
 : 2525 - 69: **`threat.enrichments.indicator.geo.country_name`*
 : 2526 - 13: type: keyword
 : 2527 - 15: example: Canada
 : 2528 - 75: **`threat.enrichments.indicator.geo.location`** : 
 : 2529 - 15: type: geo_point
 : 2530 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 2531 - 291: **`threat.enrichments.indicator.geo.name`** :   Us
 : 2532 - 13: type: keyword
 : 2533 - 18: example: boston-dc
 : 2534 - 220: **`threat.enrichments.indicator.geo.postal_code`**
 : 2535 - 13: type: keyword
 : 2536 - 14: example: 94040
 : 2537 - 75: **`threat.enrichments.indicator.geo.region_iso_cod
 : 2538 - 13: type: keyword
 : 2539 - 14: example: CA-QC
 : 2540 - 67: **`threat.enrichments.indicator.geo.region_name`**
 : 2541 - 13: type: keyword
 : 2542 - 15: example: Quebec
 : 2543 - 111: **`threat.enrichments.indicator.geo.timezone`** : 
 : 2544 - 13: type: keyword
 : 2545 - 39: example: America/Argentina/Buenos_Aires
 : 2546 - 117: **`threat.enrichments.indicator.ip`** :   Identifi
 : 2547 - 8: type: ip
 : 2548 - 16: example: 1.2.3.4
 : 2549 - 130: **`threat.enrichments.indicator.last_seen`** :   T
 : 2550 - 10: type: date
 : 2551 - 33: example: 2020-11-05T17:25:47.000Z
 : 2552 - 145: **`threat.enrichments.indicator.marking.tlp`** :  
 : 2553 - 13: type: keyword
 : 2554 - 14: example: White
 : 2555 - 139: **`threat.enrichments.indicator.modified_at`** :  
 : 2556 - 10: type: date
 : 2557 - 33: example: 2020-11-05T17:25:47.000Z
 : 2558 - 119: **`threat.enrichments.indicator.port`** :   Identi
 : 2559 - 10: type: long
 : 2560 - 12: example: 443
 : 2561 - 85: **`threat.enrichments.indicator.provider`** :   Th
 : 2562 - 13: type: keyword
 : 2563 - 20: example: lrz_urlhaus
 : 2564 - 118: **`threat.enrichments.indicator.reference`** :   R
 : 2565 - 13: type: keyword
 : 2566 - 53: example: https://system.example.com/indicator/0001
 : 2567 - 335: **`threat.enrichments.indicator.registry.data.byte
 : 2568 - 13: type: keyword
 : 2569 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
 : 2570 - 459: **`threat.enrichments.indicator.registry.data.stri
 : 2571 - 14: type: wildcard
 : 2572 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
 : 2573 - 102: **`threat.enrichments.indicator.registry.data.type
 : 2574 - 13: type: keyword
 : 2575 - 15: example: REG_SZ
 : 2576 - 83: **`threat.enrichments.indicator.registry.hive`** :
 : 2577 - 13: type: keyword
 : 2578 - 13: example: HKLM
 : 2579 - 79: **`threat.enrichments.indicator.registry.key`** : 
 : 2580 - 13: type: keyword
 : 2581 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
 : 2582 - 93: **`threat.enrichments.indicator.registry.path`** :
 : 2583 - 13: type: keyword
 : 2584 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
 : 2585 - 80: **`threat.enrichments.indicator.registry.value`** 
 : 2586 - 13: type: keyword
 : 2587 - 17: example: Debugger
 : 2588 - 126: **`threat.enrichments.indicator.scanner_stats`** :
 : 2589 - 10: type: long
 : 2590 - 10: example: 4
 : 2591 - 120: **`threat.enrichments.indicator.sightings`** :   N
 : 2592 - 10: type: long
 : 2593 - 11: example: 20
 : 2594 - 340: **`threat.enrichments.indicator.type`** :   Type o
 : 2595 - 13: type: keyword
 : 2596 - 18: example: ipv4-addr
 : 2597 - 397: **`threat.enrichments.indicator.url.domain`** :   
 : 2598 - 13: type: keyword
 : 2599 - 23: example: www.elastic.co
 : 2600 - 453: **`threat.enrichments.indicator.url.extension`** :
 : 2601 - 13: type: keyword
 : 2602 - 12: example: png
 : 2603 - 138: **`threat.enrichments.indicator.url.fragment`** : 
 : 2604 - 13: type: keyword
 : 2605 - 198: **`threat.enrichments.indicator.url.full`** :   If
 : 2606 - 14: type: wildcard
 : 2607 - 62: example: https://www.elastic.co:443/search?q=elast
 : 2608 - 74: **`threat.enrichments.indicator.url.full.text`** :
 : 2609 - 320: **`threat.enrichments.indicator.url.original`** : 
 : 2610 - 14: type: wildcard
 : 2611 - 89: example: https://www.elastic.co:443/search?q=elast
 : 2612 - 78: **`threat.enrichments.indicator.url.original.text`
 : 2613 - 76: **`threat.enrichments.indicator.url.password`** : 
 : 2614 - 13: type: keyword
 : 2615 - 87: **`threat.enrichments.indicator.url.path`** :   Pa
 : 2616 - 14: type: wildcard
 : 2617 - 81: **`threat.enrichments.indicator.url.port`** :   Po
 : 2618 - 10: type: long
 : 2619 - 12: example: 443
 : 2620 - 14: format: string
 : 2621 - 377: **`threat.enrichments.indicator.url.query`** :   T
 : 2622 - 13: type: keyword
 : 2623 - 414: **`threat.enrichments.indicator.url.registered_dom
 : 2624 - 13: type: keyword
 : 2625 - 20: example: example.com
 : 2626 - 130: **`threat.enrichments.indicator.url.scheme`** :   
 : 2627 - 13: type: keyword
 : 2628 - 14: example: https
 : 2629 - 583: **`threat.enrichments.indicator.url.subdomain`** :
 : 2630 - 13: type: keyword
 : 2631 - 13: example: east
 : 2632 - 450: **`threat.enrichments.indicator.url.top_level_doma
 : 2633 - 13: type: keyword
 : 2634 - 14: example: co.uk
 : 2635 - 76: **`threat.enrichments.indicator.url.username`** : 
 : 2636 - 13: type: keyword
 : 2637 - 247: **`threat.enrichments.indicator.x509.alternative_n
 : 2638 - 13: type: keyword
 : 2639 - 21: example: *.elastic.co
 : 2640 - 121: **`threat.enrichments.indicator.x509.issuer.common
 : 2641 - 13: type: keyword
 : 2642 - 46: example: Example SHA2 High Assurance Server CA
 : 2643 - 82: **`threat.enrichments.indicator.x509.issuer.countr
 : 2644 - 13: type: keyword
 : 2645 - 11: example: US
 : 2646 - 127: **`threat.enrichments.indicator.x509.issuer.distin
 : 2647 - 13: type: keyword
 : 2648 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 2649 - 86: **`threat.enrichments.indicator.x509.issuer.locali
 : 2650 - 13: type: keyword
 : 2651 - 22: example: Mountain View
 : 2652 - 123: **`threat.enrichments.indicator.x509.issuer.organi
 : 2653 - 13: type: keyword
 : 2654 - 20: example: Example Inc
 : 2655 - 138: **`threat.enrichments.indicator.x509.issuer.organi
 : 2656 - 13: type: keyword
 : 2657 - 24: example: www.example.com
 : 2658 - 114: **`threat.enrichments.indicator.x509.issuer.state_
 : 2659 - 13: type: keyword
 : 2660 - 19: example: California
 : 2661 - 114: **`threat.enrichments.indicator.x509.not_after`** 
 : 2662 - 10: type: date
 : 2663 - 34: example: 2020-07-16 03:15:39+00:00
 : 2664 - 111: **`threat.enrichments.indicator.x509.not_before`**
 : 2665 - 10: type: date
 : 2666 - 34: example: 2019-08-16 01:40:25+00:00
 : 2667 - 107: **`threat.enrichments.indicator.x509.public_key_al
 : 2668 - 13: type: keyword
 : 2669 - 12: example: RSA
 : 2670 - 147: **`threat.enrichments.indicator.x509.public_key_cu
 : 2671 - 13: type: keyword
 : 2672 - 17: example: nistp521
 : 2673 - 131: **`threat.enrichments.indicator.x509.public_key_ex
 : 2674 - 10: type: long
 : 2675 - 14: example: 65537
 : 2676 - 21: Field is not indexed.
 : 2677 - 101: **`threat.enrichments.indicator.x509.public_key_si
 : 2678 - 10: type: long
 : 2679 - 13: example: 2048
 : 2680 - 227: **`threat.enrichments.indicator.x509.serial_number
 : 2681 - 13: type: keyword
 : 2682 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 2683 - 250: **`threat.enrichments.indicator.x509.signature_alg
 : 2684 - 13: type: keyword
 : 2685 - 19: example: SHA256-RSA
 : 2686 - 101: **`threat.enrichments.indicator.x509.subject.commo
 : 2687 - 13: type: keyword
 : 2688 - 34: example: shared.global.example.net
 : 2689 - 82: **`threat.enrichments.indicator.x509.subject.count
 : 2690 - 13: type: keyword
 : 2691 - 11: example: US
 : 2692 - 129: **`threat.enrichments.indicator.x509.subject.disti
 : 2693 - 13: type: keyword
 : 2694 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 2695 - 87: **`threat.enrichments.indicator.x509.subject.local
 : 2696 - 13: type: keyword
 : 2697 - 22: example: San Francisco
 : 2698 - 102: **`threat.enrichments.indicator.x509.subject.organ
 : 2699 - 13: type: keyword
 : 2700 - 22: example: Example, Inc.
 : 2701 - 117: **`threat.enrichments.indicator.x509.subject.organ
 : 2702 - 13: type: keyword
 : 2703 - 115: **`threat.enrichments.indicator.x509.subject.state
 : 2704 - 13: type: keyword
 : 2705 - 19: example: California
 : 2706 - 82: **`threat.enrichments.indicator.x509.version_numbe
 : 2707 - 13: type: keyword
 : 2708 - 10: example: 3
 : 2709 - 141: **`threat.enrichments.matched.atomic`** :   Identi
 : 2710 - 13: type: keyword
 : 2711 - 23: example: bad-domain.com
 : 2712 - 147: **`threat.enrichments.matched.field`** :   Identif
 : 2713 - 13: type: keyword
 : 2714 - 25: example: file.hash.sha256
 : 2715 - 105: **`threat.enrichments.matched.id`** :   Identifies
 : 2716 - 13: type: keyword
 : 2717 - 45: example: ff93aee5-86a1-4a61-b0e6-0cdc313d01b5
 : 2718 - 111: **`threat.enrichments.matched.index`** :   Identif
 : 2719 - 13: type: keyword
 : 2720 - 41: example: filebeat-8.0.0-2021.05.23-000011
 : 2721 - 132: **`threat.enrichments.matched.type`** :   Identifi
 : 2722 - 13: type: keyword
 : 2723 - 29: example: indicator_match_rule
 : 2724 - 270: **`threat.framework`** :   Name of the threat fram
 : 2725 - 13: type: keyword
 : 2726 - 21: example: MITRE ATT&CK
 : 2727 - 221: **`threat.group.alias`** :   The alias(es) of the 
 : 2728 - 13: type: keyword
 : 2729 - 31: example: [ "Magecart Group 6" ]
 : 2730 - 204: **`threat.group.id`** :   The id of the group for 
 : 2731 - 13: type: keyword
 : 2732 - 14: example: G0037
 : 2733 - 210: **`threat.group.name`** :   The name of the group 
 : 2734 - 13: type: keyword
 : 2735 - 13: example: FIN6
 : 2736 - 233: **`threat.group.reference`** :   The reference URL
 : 2737 - 13: type: keyword
 : 2738 - 47: example: https://attack.mitre.org/groups/G0037/
 : 2739 - 171: **`threat.indicator.as.number`** :   Unique number
 : 2740 - 10: type: long
 : 2741 - 14: example: 15169
 : 2742 - 66: **`threat.indicator.as.organization.name`** :   Or
 : 2743 - 13: type: keyword
 : 2744 - 19: example: Google LLC
 : 2745 - 74: **`threat.indicator.as.organization.name.text`** :
 : 2746 - 302: **`threat.indicator.confidence`** :   Identifies t
 : 2747 - 13: type: keyword
 : 2748 - 15: example: Medium
 : 2749 - 92: **`threat.indicator.description`** :   Describes t
 : 2750 - 13: type: keyword
 : 2751 - 58: example: IP x.x.x.x was observed delivering the An
 : 2752 - 119: **`threat.indicator.email.address`** :   Identifie
 : 2753 - 13: type: keyword
 : 2754 - 28: example: `phish@example.com`
 : 2755 - 130: **`threat.indicator.file.accessed`** :   Last time
 : 2756 - 10: type: date
 : 2757 - 271: **`threat.indicator.file.attributes`** :   Array o
 : 2758 - 13: type: keyword
 : 2759 - 31: example: ["readonly", "system"]
 : 2760 - 244: **`threat.indicator.file.code_signature.digest_alg
 : 2761 - 13: type: keyword
 : 2762 - 15: example: sha256
 : 2763 - 99: **`threat.indicator.file.code_signature.exists`** 
 : 2764 - 13: type: boolean
 : 2765 - 13: example: true
 : 2766 - 215: **`threat.indicator.file.code_signature.signing_id
 : 2767 - 13: type: keyword
 : 2768 - 28: example: com.apple.xpc.proxy
 : 2769 - 278: **`threat.indicator.file.code_signature.status`** 
 : 2770 - 13: type: keyword
 : 2771 - 29: example: ERROR_UNTRUSTED_ROOT
 : 2772 - 91: **`threat.indicator.file.code_signature.subject_na
 : 2773 - 13: type: keyword
 : 2774 - 30: example: Microsoft Corporation
 : 2775 - 208: **`threat.indicator.file.code_signature.team_id`**
 : 2776 - 13: type: keyword
 : 2777 - 19: example: EQHXZ8M8AV
 : 2778 - 120: **`threat.indicator.file.code_signature.timestamp`
 : 2779 - 10: type: date
 : 2780 - 29: example: 2021-01-01T12:10:30Z
 : 2781 - 251: **`threat.indicator.file.code_signature.trusted`**
 : 2782 - 13: type: boolean
 : 2783 - 13: example: true
 : 2784 - 186: **`threat.indicator.file.code_signature.valid`** :
 : 2785 - 13: type: boolean
 : 2786 - 13: example: true
 : 2787 - 114: **`threat.indicator.file.created`** :   File creat
 : 2788 - 10: type: date
 : 2789 - 247: **`threat.indicator.file.ctime`** :   Last time th
 : 2790 - 10: type: date
 : 2791 - 77: **`threat.indicator.file.device`** :   Device that
 : 2792 - 13: type: keyword
 : 2793 - 12: example: sda
 : 2794 - 132: **`threat.indicator.file.directory`** :   Director
 : 2795 - 13: type: keyword
 : 2796 - 20: example: /home/alice
 : 2797 - 182: **`threat.indicator.file.drive_letter`** :   Drive
 : 2798 - 13: type: keyword
 : 2799 - 10: example: C
 : 2800 - 86: **`threat.indicator.file.elf.architecture`** :   M
 : 2801 - 13: type: keyword
 : 2802 - 15: example: x86-64
 : 2803 - 73: **`threat.indicator.file.elf.byte_order`** :   Byt
 : 2804 - 13: type: keyword
 : 2805 - 22: example: Little Endian
 : 2806 - 70: **`threat.indicator.file.elf.cpu_type`** :   CPU t
 : 2807 - 13: type: keyword
 : 2808 - 14: example: Intel
 : 2809 - 182: **`threat.indicator.file.elf.creation_date`** :   
 : 2810 - 10: type: date
 : 2811 - 85: **`threat.indicator.file.elf.exports`** :   List o
 : 2812 - 15: type: flattened
 : 2813 - 109: **`threat.indicator.file.elf.header.abi_version`**
 : 2814 - 13: type: keyword
 : 2815 - 78: **`threat.indicator.file.elf.header.class`** :   H
 : 2816 - 13: type: keyword
 : 2817 - 77: **`threat.indicator.file.elf.header.data`** :   Da
 : 2818 - 13: type: keyword
 : 2819 - 88: **`threat.indicator.file.elf.header.entrypoint`** 
 : 2820 - 10: type: long
 : 2821 - 14: format: string
 : 2822 - 87: **`threat.indicator.file.elf.header.object_version
 : 2823 - 13: type: keyword
 : 2824 - 101: **`threat.indicator.file.elf.header.os_abi`** :   
 : 2825 - 13: type: keyword
 : 2826 - 76: **`threat.indicator.file.elf.header.type`** :   He
 : 2827 - 13: type: keyword
 : 2828 - 77: **`threat.indicator.file.elf.header.version`** :  
 : 2829 - 13: type: keyword
 : 2830 - 85: **`threat.indicator.file.elf.imports`** :   List o
 : 2831 - 15: type: flattened
 : 2832 - 213: **`threat.indicator.file.elf.sections`** :   An ar
 : 2833 - 12: type: nested
 : 2834 - 101: **`threat.indicator.file.elf.sections.chi2`** :   
 : 2835 - 10: type: long
 : 2836 - 14: format: number
 : 2837 - 98: **`threat.indicator.file.elf.sections.entropy`** :
 : 2838 - 10: type: long
 : 2839 - 14: format: number
 : 2840 - 74: **`threat.indicator.file.elf.sections.flags`** :  
 : 2841 - 13: type: keyword
 : 2842 - 72: **`threat.indicator.file.elf.sections.name`** :   
 : 2843 - 13: type: keyword
 : 2844 - 85: **`threat.indicator.file.elf.sections.physical_off
 : 2845 - 13: type: keyword
 : 2846 - 90: **`threat.indicator.file.elf.sections.physical_siz
 : 2847 - 10: type: long
 : 2848 - 13: format: bytes
 : 2849 - 72: **`threat.indicator.file.elf.sections.type`** :   
 : 2850 - 13: type: keyword
 : 2851 - 94: **`threat.indicator.file.elf.sections.virtual_addr
 : 2852 - 10: type: long
 : 2853 - 14: format: string
 : 2854 - 88: **`threat.indicator.file.elf.sections.virtual_size
 : 2855 - 10: type: long
 : 2856 - 14: format: string
 : 2857 - 213: **`threat.indicator.file.elf.segments`** :   An ar
 : 2858 - 12: type: nested
 : 2859 - 82: **`threat.indicator.file.elf.segments.sections`** 
 : 2860 - 13: type: keyword
 : 2861 - 74: **`threat.indicator.file.elf.segments.type`** :   
 : 2862 - 13: type: keyword
 : 2863 - 102: **`threat.indicator.file.elf.shared_libraries`** :
 : 2864 - 13: type: keyword
 : 2865 - 79: **`threat.indicator.file.elf.telfhash`** :   telfh
 : 2866 - 13: type: keyword
 : 2867 - 214: **`threat.indicator.file.extension`** :   File ext
 : 2868 - 13: type: keyword
 : 2869 - 12: example: png
 : 2870 - 804: **`threat.indicator.file.fork_name`** :   A fork i
 : 2871 - 13: type: keyword
 : 2872 - 23: example: Zone.Identifer
 : 2873 - 71: **`threat.indicator.file.gid`** :   Primary group 
 : 2874 - 13: type: keyword
 : 2875 - 13: example: 1001
 : 2876 - 69: **`threat.indicator.file.group`** :   Primary grou
 : 2877 - 13: type: keyword
 : 2878 - 14: example: alice
 : 2879 - 50: **`threat.indicator.file.hash.md5`** :   MD5 hash.
 : 2880 - 13: type: keyword
 : 2881 - 52: **`threat.indicator.file.hash.sha1`** :   SHA1 has
 : 2882 - 13: type: keyword
 : 2883 - 56: **`threat.indicator.file.hash.sha256`** :   SHA256
 : 2884 - 13: type: keyword
 : 2885 - 56: **`threat.indicator.file.hash.sha512`** :   SHA512
 : 2886 - 13: type: keyword
 : 2887 - 56: **`threat.indicator.file.hash.ssdeep`** :   SSDEEP
 : 2888 - 13: type: keyword
 : 2889 - 84: **`threat.indicator.file.inode`** :   Inode repres
 : 2890 - 13: type: keyword
 : 2891 - 15: example: 256383
 : 2892 - 231: **`threat.indicator.file.mime_type`** :   MIME typ
 : 2893 - 13: type: keyword
 : 2894 - 78: **`threat.indicator.file.mode`** :   Mode of the f
 : 2895 - 13: type: keyword
 : 2896 - 13: example: 0640
 : 2897 - 78: **`threat.indicator.file.mtime`** :   Last time th
 : 2898 - 10: type: date
 : 2899 - 101: **`threat.indicator.file.name`** :   Name of the f
 : 2900 - 13: type: keyword
 : 2901 - 20: example: example.png
 : 2902 - 60: **`threat.indicator.file.owner`** :   File owner’s
 : 2903 - 13: type: keyword
 : 2904 - 14: example: alice
 : 2905 - 138: **`threat.indicator.file.path`** :   Full path to 
 : 2906 - 13: type: keyword
 : 2907 - 32: example: /home/alice/example.png
 : 2908 - 63: **`threat.indicator.file.path.text`** :   type: ma
 : 2909 - 85: **`threat.indicator.file.pe.architecture`** :   CP
 : 2910 - 13: type: keyword
 : 2911 - 12: example: x64
 : 2912 - 103: **`threat.indicator.file.pe.company`** :   Interna
 : 2913 - 13: type: keyword
 : 2914 - 30: example: Microsoft Corporation
 : 2915 - 106: **`threat.indicator.file.pe.description`** :   Int
 : 2916 - 13: type: keyword
 : 2917 - 14: example: Paint
 : 2918 - 103: **`threat.indicator.file.pe.file_version`** :   In
 : 2919 - 13: type: keyword
 : 2920 - 23: example: 6.3.9600.17415
 : 2921 - 375: **`threat.indicator.file.pe.imphash`** :   A hash 
 : 2922 - 13: type: keyword
 : 2923 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
 : 2924 - 106: **`threat.indicator.file.pe.original_file_name`** 
 : 2925 - 13: type: keyword
 : 2926 - 20: example: MSPAINT.EXE
 : 2927 - 103: **`threat.indicator.file.pe.product`** :   Interna
 : 2928 - 13: type: keyword
 : 2929 - 45: example: Microsoft® Windows® Operating System
 : 2930 - 98: **`threat.indicator.file.size`** :   File size in 
 : 2931 - 10: type: long
 : 2932 - 14: example: 16384
 : 2933 - 69: **`threat.indicator.file.target_path`** :   Target
 : 2934 - 13: type: keyword
 : 2935 - 70: **`threat.indicator.file.target_path.text`** :   t
 : 2936 - 71: **`threat.indicator.file.type`** :   File type (fi
 : 2937 - 13: type: keyword
 : 2938 - 13: example: file
 : 2939 - 101: **`threat.indicator.file.uid`** :   The user ID (U
 : 2940 - 13: type: keyword
 : 2941 - 13: example: 1001
 : 2942 - 240: **`threat.indicator.file.x509.alternative_names`**
 : 2943 - 13: type: keyword
 : 2944 - 21: example: *.elastic.co
 : 2945 - 114: **`threat.indicator.file.x509.issuer.common_name`*
 : 2946 - 13: type: keyword
 : 2947 - 46: example: Example SHA2 High Assurance Server CA
 : 2948 - 75: **`threat.indicator.file.x509.issuer.country`** : 
 : 2949 - 13: type: keyword
 : 2950 - 11: example: US
 : 2951 - 120: **`threat.indicator.file.x509.issuer.distinguished
 : 2952 - 13: type: keyword
 : 2953 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 2954 - 79: **`threat.indicator.file.x509.issuer.locality`** :
 : 2955 - 13: type: keyword
 : 2956 - 22: example: Mountain View
 : 2957 - 116: **`threat.indicator.file.x509.issuer.organization`
 : 2958 - 13: type: keyword
 : 2959 - 20: example: Example Inc
 : 2960 - 131: **`threat.indicator.file.x509.issuer.organizationa
 : 2961 - 13: type: keyword
 : 2962 - 24: example: www.example.com
 : 2963 - 107: **`threat.indicator.file.x509.issuer.state_or_prov
 : 2964 - 13: type: keyword
 : 2965 - 19: example: California
 : 2966 - 107: **`threat.indicator.file.x509.not_after`** :   Tim
 : 2967 - 10: type: date
 : 2968 - 34: example: 2020-07-16 03:15:39+00:00
 : 2969 - 104: **`threat.indicator.file.x509.not_before`** :   Ti
 : 2970 - 10: type: date
 : 2971 - 34: example: 2019-08-16 01:40:25+00:00
 : 2972 - 100: **`threat.indicator.file.x509.public_key_algorithm
 : 2973 - 13: type: keyword
 : 2974 - 12: example: RSA
 : 2975 - 140: **`threat.indicator.file.x509.public_key_curve`** 
 : 2976 - 13: type: keyword
 : 2977 - 17: example: nistp521
 : 2978 - 124: **`threat.indicator.file.x509.public_key_exponent`
 : 2979 - 10: type: long
 : 2980 - 14: example: 65537
 : 2981 - 21: Field is not indexed.
 : 2982 - 94: **`threat.indicator.file.x509.public_key_size`** :
 : 2983 - 10: type: long
 : 2984 - 13: example: 2048
 : 2985 - 220: **`threat.indicator.file.x509.serial_number`** :  
 : 2986 - 13: type: keyword
 : 2987 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 2988 - 243: **`threat.indicator.file.x509.signature_algorithm`
 : 2989 - 13: type: keyword
 : 2990 - 19: example: SHA256-RSA
 : 2991 - 94: **`threat.indicator.file.x509.subject.common_name`
 : 2992 - 13: type: keyword
 : 2993 - 34: example: shared.global.example.net
 : 2994 - 75: **`threat.indicator.file.x509.subject.country`** :
 : 2995 - 13: type: keyword
 : 2996 - 11: example: US
 : 2997 - 122: **`threat.indicator.file.x509.subject.distinguishe
 : 2998 - 13: type: keyword
 : 2999 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 3000 - 80: **`threat.indicator.file.x509.subject.locality`** 
 : 3001 - 13: type: keyword
 : 3002 - 22: example: San Francisco
 : 3003 - 95: **`threat.indicator.file.x509.subject.organization
 : 3004 - 13: type: keyword
 : 3005 - 22: example: Example, Inc.
 : 3006 - 110: **`threat.indicator.file.x509.subject.organization
 : 3007 - 13: type: keyword
 : 3008 - 108: **`threat.indicator.file.x509.subject.state_or_pro
 : 3009 - 13: type: keyword
 : 3010 - 19: example: California
 : 3011 - 75: **`threat.indicator.file.x509.version_number`** : 
 : 3012 - 13: type: keyword
 : 3013 - 10: example: 3
 : 3014 - 120: **`threat.indicator.first_seen`** :   The date and
 : 3015 - 10: type: date
 : 3016 - 33: example: 2020-11-05T17:25:47.000Z
 : 3017 - 51: **`threat.indicator.geo.city_name`** :   City name
 : 3018 - 13: type: keyword
 : 3019 - 17: example: Montreal
 : 3020 - 92: **`threat.indicator.geo.continent_code`** :   Two-
 : 3021 - 13: type: keyword
 : 3022 - 11: example: NA
 : 3023 - 68: **`threat.indicator.geo.continent_name`** :   Name
 : 3024 - 13: type: keyword
 : 3025 - 22: example: North America
 : 3026 - 65: **`threat.indicator.geo.country_iso_code`** :   Co
 : 3027 - 13: type: keyword
 : 3028 - 11: example: CA
 : 3029 - 57: **`threat.indicator.geo.country_name`** :   Countr
 : 3030 - 13: type: keyword
 : 3031 - 15: example: Canada
 : 3032 - 63: **`threat.indicator.geo.location`** :   Longitude 
 : 3033 - 15: type: geo_point
 : 3034 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
 : 3035 - 279: **`threat.indicator.geo.name`** :   User-defined d
 : 3036 - 13: type: keyword
 : 3037 - 18: example: boston-dc
 : 3038 - 208: **`threat.indicator.geo.postal_code`** :   Postal 
 : 3039 - 13: type: keyword
 : 3040 - 14: example: 94040
 : 3041 - 63: **`threat.indicator.geo.region_iso_code`** :   Reg
 : 3042 - 13: type: keyword
 : 3043 - 14: example: CA-QC
 : 3044 - 55: **`threat.indicator.geo.region_name`** :   Region 
 : 3045 - 13: type: keyword
 : 3046 - 15: example: Quebec
 : 3047 - 99: **`threat.indicator.geo.timezone`** :   The time z
 : 3048 - 13: type: keyword
 : 3049 - 39: example: America/Argentina/Buenos_Aires
 : 3050 - 105: **`threat.indicator.ip`** :   Identifies a threat 
 : 3051 - 8: type: ip
 : 3052 - 16: example: 1.2.3.4
 : 3053 - 118: **`threat.indicator.last_seen`** :   The date and 
 : 3054 - 10: type: date
 : 3055 - 33: example: 2020-11-05T17:25:47.000Z
 : 3056 - 133: **`threat.indicator.marking.tlp`** :   Traffic Lig
 : 3057 - 13: type: keyword
 : 3058 - 14: example: WHITE
 : 3059 - 127: **`threat.indicator.modified_at`** :   The date an
 : 3060 - 10: type: date
 : 3061 - 33: example: 2020-11-05T17:25:47.000Z
 : 3062 - 107: **`threat.indicator.port`** :   Identifies a threa
 : 3063 - 10: type: long
 : 3064 - 12: example: 443
 : 3065 - 73: **`threat.indicator.provider`** :   The name of th
 : 3066 - 13: type: keyword
 : 3067 - 20: example: lrz_urlhaus
 : 3068 - 106: **`threat.indicator.reference`** :   Reference URL
 : 3069 - 13: type: keyword
 : 3070 - 53: example: https://system.example.com/indicator/0001
 : 3071 - 323: **`threat.indicator.registry.data.bytes`** :   Ori
 : 3072 - 13: type: keyword
 : 3073 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
 : 3074 - 447: **`threat.indicator.registry.data.strings`** :   C
 : 3075 - 14: type: wildcard
 : 3076 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
 : 3077 - 90: **`threat.indicator.registry.data.type`** :   Stan
 : 3078 - 13: type: keyword
 : 3079 - 15: example: REG_SZ
 : 3080 - 71: **`threat.indicator.registry.hive`** :   Abbreviat
 : 3081 - 13: type: keyword
 : 3082 - 13: example: HKLM
 : 3083 - 67: **`threat.indicator.registry.key`** :   Hive-relat
 : 3084 - 13: type: keyword
 : 3085 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
 : 3086 - 81: **`threat.indicator.registry.path`** :   Full path
 : 3087 - 13: type: keyword
 : 3088 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
 : 3089 - 68: **`threat.indicator.registry.value`** :   Name of 
 : 3090 - 13: type: keyword
 : 3091 - 17: example: Debugger
 : 3092 - 114: **`threat.indicator.scanner_stats`** :   Count of 
 : 3093 - 10: type: long
 : 3094 - 10: example: 4
 : 3095 - 108: **`threat.indicator.sightings`** :   Number of tim
 : 3096 - 10: type: long
 : 3097 - 11: example: 20
 : 3098 - 328: **`threat.indicator.type`** :   Type of indicator 
 : 3099 - 13: type: keyword
 : 3100 - 18: example: ipv4-addr
 : 3101 - 385: **`threat.indicator.url.domain`** :   Domain of th
 : 3102 - 13: type: keyword
 : 3103 - 23: example: www.elastic.co
 : 3104 - 441: **`threat.indicator.url.extension`** :   The field
 : 3105 - 13: type: keyword
 : 3106 - 12: example: png
 : 3107 - 126: **`threat.indicator.url.fragment`** :   Portion of
 : 3108 - 13: type: keyword
 : 3109 - 186: **`threat.indicator.url.full`** :   If full URLs a
 : 3110 - 14: type: wildcard
 : 3111 - 62: example: https://www.elastic.co:443/search?q=elast
 : 3112 - 62: **`threat.indicator.url.full.text`** :   type: mat
 : 3113 - 308: **`threat.indicator.url.original`** :   Unmodified
 : 3114 - 14: type: wildcard
 : 3115 - 89: example: https://www.elastic.co:443/search?q=elast
 : 3116 - 66: **`threat.indicator.url.original.text`** :   type:
 : 3117 - 64: **`threat.indicator.url.password`** :   Password o
 : 3118 - 13: type: keyword
 : 3119 - 75: **`threat.indicator.url.path`** :   Path of the re
 : 3120 - 14: type: wildcard
 : 3121 - 69: **`threat.indicator.url.port`** :   Port of the re
 : 3122 - 10: type: long
 : 3123 - 12: example: 443
 : 3124 - 14: format: string
 : 3125 - 365: **`threat.indicator.url.query`** :   The query fie
 : 3126 - 13: type: keyword
 : 3127 - 402: **`threat.indicator.url.registered_domain`** :   T
 : 3128 - 13: type: keyword
 : 3129 - 20: example: example.com
 : 3130 - 118: **`threat.indicator.url.scheme`** :   Scheme of th
 : 3131 - 13: type: keyword
 : 3132 - 14: example: https
 : 3133 - 571: **`threat.indicator.url.subdomain`** :   The subdo
 : 3134 - 13: type: keyword
 : 3135 - 13: example: east
 : 3136 - 438: **`threat.indicator.url.top_level_domain`** :   Th
 : 3137 - 13: type: keyword
 : 3138 - 14: example: co.uk
 : 3139 - 64: **`threat.indicator.url.username`** :   Username o
 : 3140 - 13: type: keyword
 : 3141 - 235: **`threat.indicator.x509.alternative_names`** :   
 : 3142 - 13: type: keyword
 : 3143 - 21: example: *.elastic.co
 : 3144 - 109: **`threat.indicator.x509.issuer.common_name`** :  
 : 3145 - 13: type: keyword
 : 3146 - 46: example: Example SHA2 High Assurance Server CA
 : 3147 - 70: **`threat.indicator.x509.issuer.country`** :   Lis
 : 3148 - 13: type: keyword
 : 3149 - 11: example: US
 : 3150 - 115: **`threat.indicator.x509.issuer.distinguished_name
 : 3151 - 13: type: keyword
 : 3152 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 3153 - 74: **`threat.indicator.x509.issuer.locality`** :   Li
 : 3154 - 13: type: keyword
 : 3155 - 22: example: Mountain View
 : 3156 - 111: **`threat.indicator.x509.issuer.organization`** : 
 : 3157 - 13: type: keyword
 : 3158 - 20: example: Example Inc
 : 3159 - 126: **`threat.indicator.x509.issuer.organizational_uni
 : 3160 - 13: type: keyword
 : 3161 - 24: example: www.example.com
 : 3162 - 102: **`threat.indicator.x509.issuer.state_or_province`
 : 3163 - 13: type: keyword
 : 3164 - 19: example: California
 : 3165 - 102: **`threat.indicator.x509.not_after`** :   Time at 
 : 3166 - 10: type: date
 : 3167 - 34: example: 2020-07-16 03:15:39+00:00
 : 3168 - 99: **`threat.indicator.x509.not_before`** :   Time at
 : 3169 - 10: type: date
 : 3170 - 34: example: 2019-08-16 01:40:25+00:00
 : 3171 - 95: **`threat.indicator.x509.public_key_algorithm`** :
 : 3172 - 13: type: keyword
 : 3173 - 12: example: RSA
 : 3174 - 135: **`threat.indicator.x509.public_key_curve`** :   T
 : 3175 - 13: type: keyword
 : 3176 - 17: example: nistp521
 : 3177 - 119: **`threat.indicator.x509.public_key_exponent`** : 
 : 3178 - 10: type: long
 : 3179 - 14: example: 65537
 : 3180 - 21: Field is not indexed.
 : 3181 - 89: **`threat.indicator.x509.public_key_size`** :   Th
 : 3182 - 10: type: long
 : 3183 - 13: example: 2048
 : 3184 - 215: **`threat.indicator.x509.serial_number`** :   Uniq
 : 3185 - 13: type: keyword
 : 3186 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 3187 - 238: **`threat.indicator.x509.signature_algorithm`** : 
 : 3188 - 13: type: keyword
 : 3189 - 19: example: SHA256-RSA
 : 3190 - 89: **`threat.indicator.x509.subject.common_name`** : 
 : 3191 - 13: type: keyword
 : 3192 - 34: example: shared.global.example.net
 : 3193 - 70: **`threat.indicator.x509.subject.country`** :   Li
 : 3194 - 13: type: keyword
 : 3195 - 11: example: US
 : 3196 - 117: **`threat.indicator.x509.subject.distinguished_nam
 : 3197 - 13: type: keyword
 : 3198 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 3199 - 75: **`threat.indicator.x509.subject.locality`** :   L
 : 3200 - 13: type: keyword
 : 3201 - 22: example: San Francisco
 : 3202 - 90: **`threat.indicator.x509.subject.organization`** :
 : 3203 - 13: type: keyword
 : 3204 - 22: example: Example, Inc.
 : 3205 - 105: **`threat.indicator.x509.subject.organizational_un
 : 3206 - 13: type: keyword
 : 3207 - 103: **`threat.indicator.x509.subject.state_or_province
 : 3208 - 13: type: keyword
 : 3209 - 19: example: California
 : 3210 - 70: **`threat.indicator.x509.version_number`** :   Ver
 : 3211 - 13: type: keyword
 : 3212 - 10: example: 3
 : 3213 - 243: **`threat.software.alias`** :   The alias(es) of t
 : 3214 - 13: type: keyword
 : 3215 - 22: example: [ "X-Agent" ]
 : 3216 - 190: **`threat.software.id`** :   The id of the softwar
 : 3217 - 13: type: keyword
 : 3218 - 14: example: S0552
 : 3219 - 196: **`threat.software.name`** :   The name of the sof
 : 3220 - 13: type: keyword
 : 3221 - 15: example: AdFind
 : 3222 - 250: **`threat.software.platforms`** :   The platforms 
 : 3223 - 67: While not required, you can use a MITRE ATT&CK® so
 : 3224 - 13: type: keyword
 : 3225 - 22: example: [ "Windows" ]
 : 3226 - 219: **`threat.software.reference`** :   The reference 
 : 3227 - 13: type: keyword
 : 3228 - 49: example: https://attack.mitre.org/software/S0552/
 : 3229 - 165: **`threat.software.type`** :   The type of softwar
 : 3230 - 70: ``` While not required, you can use a MITRE ATT&CK
 : 3231 - 13: type: keyword
 : 3232 - 13: example: Tool
 : 3233 - 161: **`threat.tactic.id`** :   The id of tactic used b
 : 3234 - 13: type: keyword
 : 3235 - 15: example: TA0002
 : 3236 - 173: **`threat.tactic.name`** :   Name of the type of t
 : 3237 - 13: type: keyword
 : 3238 - 18: example: Execution
 : 3239 - 179: **`threat.tactic.reference`** :   The reference ur
 : 3240 - 13: type: keyword
 : 3241 - 49: example: https://attack.mitre.org/tactics/TA0002/
 : 3242 - 172: **`threat.technique.id`** :   The id of technique 
 : 3243 - 13: type: keyword
 : 3244 - 14: example: T1059
 : 3245 - 176: **`threat.technique.name`** :   The name of techni
 : 3246 - 13: type: keyword
 : 3247 - 42: example: Command and Scripting Interpreter
 : 3248 - 58: **`threat.technique.name.text`** :   type: match_o
 : 3249 - 190: **`threat.technique.reference`** :   The reference
 : 3250 - 13: type: keyword
 : 3251 - 51: example: https://attack.mitre.org/techniques/T1059
 : 3252 - 200: **`threat.technique.subtechnique.id`** :   The ful
 : 3253 - 13: type: keyword
 : 3254 - 18: example: T1059.001
 : 3255 - 199: **`threat.technique.subtechnique.name`** :   The n
 : 3256 - 13: type: keyword
 : 3257 - 19: example: PowerShell
 : 3258 - 71: **`threat.technique.subtechnique.name.text`** :   
 : 3259 - 213: **`threat.technique.subtechnique.reference`** :   
 : 3260 - 13: type: keyword
 : 3261 - 55: example: https://attack.mitre.org/techniques/T1059
 : 3262 - 13: ## tls [_tls]
 : 3263 - 164: Fields related to a TLS connection. These fields f
 : 3264 - 85: **`tls.cipher`** :   String indicating the cipher 
 : 3265 - 13: type: keyword
 : 3266 - 46: example: TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
 : 3267 - 199: **`tls.client.certificate`** :   PEM-encoded stand
 : 3268 - 13: type: keyword
 : 3269 - 14: example: MII…​
 : 3270 - 252: **`tls.client.certificate_chain`** :   Array of PE
 : 3271 - 13: type: keyword
 : 3272 - 27: example: ["MII…​", "MII…​"]
 : 3273 - 228: **`tls.client.hash.md5`** :   Certificate fingerpr
 : 3274 - 13: type: keyword
 : 3275 - 41: example: 0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC
 : 3276 - 230: **`tls.client.hash.sha1`** :   Certificate fingerp
 : 3277 - 13: type: keyword
 : 3278 - 49: example: 9E393D93138888D288266C2D915214D1D1CCEB2A
 : 3279 - 234: **`tls.client.hash.sha256`** :   Certificate finge
 : 3280 - 13: type: keyword
 : 3281 - 73: example: 0687F666A054EF17A08E2F2162EAB4CBC0D265E1D
 : 3282 - 121: **`tls.client.issuer`** :   Distinguished name of 
 : 3283 - 13: type: keyword
 : 3284 - 71: example: CN=Example Root CA, OU=Infrastructure Tea
 : 3285 - 103: **`tls.client.ja3`** :   A hash that identifies cl
 : 3286 - 13: type: keyword
 : 3287 - 41: example: d4e5b18d6b55c71272893221c96ba240
 : 3288 - 106: **`tls.client.not_after`** :   Date/Time indicatin
 : 3289 - 10: type: date
 : 3290 - 33: example: 2021-01-01T00:00:00.000Z
 : 3291 - 103: **`tls.client.not_before`** :   Date/Time indicati
 : 3292 - 10: type: date
 : 3293 - 33: example: 1970-01-01T00:00:00.000Z
 : 3294 - 215: **`tls.client.server_name`** :   Also called an SN
 : 3295 - 13: type: keyword
 : 3296 - 23: example: www.elastic.co
 : 3297 - 108: **`tls.client.subject`** :   Distinguished name of
 : 3298 - 13: type: keyword
 : 3299 - 63: example: CN=myclient, OU=Documentation Team, DC=ex
 : 3300 - 102: **`tls.client.supported_ciphers`** :   Array of ci
 : 3301 - 13: type: keyword
 : 3302 - 99: example: ["TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
 : 3303 - 229: **`tls.client.x509.alternative_names`** :   List o
 : 3304 - 13: type: keyword
 : 3305 - 21: example: *.elastic.co
 : 3306 - 103: **`tls.client.x509.issuer.common_name`** :   List 
 : 3307 - 13: type: keyword
 : 3308 - 46: example: Example SHA2 High Assurance Server CA
 : 3309 - 64: **`tls.client.x509.issuer.country`** :   List of c
 : 3310 - 13: type: keyword
 : 3311 - 11: example: US
 : 3312 - 109: **`tls.client.x509.issuer.distinguished_name`** : 
 : 3313 - 13: type: keyword
 : 3314 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 3315 - 68: **`tls.client.x509.issuer.locality`** :   List of 
 : 3316 - 13: type: keyword
 : 3317 - 22: example: Mountain View
 : 3318 - 105: **`tls.client.x509.issuer.organization`** :   List
 : 3319 - 13: type: keyword
 : 3320 - 20: example: Example Inc
 : 3321 - 120: **`tls.client.x509.issuer.organizational_unit`** :
 : 3322 - 13: type: keyword
 : 3323 - 24: example: www.example.com
 : 3324 - 96: **`tls.client.x509.issuer.state_or_province`** :  
 : 3325 - 13: type: keyword
 : 3326 - 19: example: California
 : 3327 - 96: **`tls.client.x509.not_after`** :   Time at which 
 : 3328 - 10: type: date
 : 3329 - 34: example: 2020-07-16 03:15:39+00:00
 : 3330 - 93: **`tls.client.x509.not_before`** :   Time at which
 : 3331 - 10: type: date
 : 3332 - 34: example: 2019-08-16 01:40:25+00:00
 : 3333 - 89: **`tls.client.x509.public_key_algorithm`** :   Alg
 : 3334 - 13: type: keyword
 : 3335 - 12: example: RSA
 : 3336 - 129: **`tls.client.x509.public_key_curve`** :   The cur
 : 3337 - 13: type: keyword
 : 3338 - 17: example: nistp521
 : 3339 - 113: **`tls.client.x509.public_key_exponent`** :   Expo
 : 3340 - 10: type: long
 : 3341 - 14: example: 65537
 : 3342 - 21: Field is not indexed.
 : 3343 - 83: **`tls.client.x509.public_key_size`** :   The size
 : 3344 - 10: type: long
 : 3345 - 13: example: 2048
 : 3346 - 209: **`tls.client.x509.serial_number`** :   Unique ser
 : 3347 - 13: type: keyword
 : 3348 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 3349 - 232: **`tls.client.x509.signature_algorithm`** :   Iden
 : 3350 - 13: type: keyword
 : 3351 - 19: example: SHA256-RSA
 : 3352 - 83: **`tls.client.x509.subject.common_name`** :   List
 : 3353 - 13: type: keyword
 : 3354 - 34: example: shared.global.example.net
 : 3355 - 64: **`tls.client.x509.subject.country`** :   List of 
 : 3356 - 13: type: keyword
 : 3357 - 11: example: US
 : 3358 - 111: **`tls.client.x509.subject.distinguished_name`** :
 : 3359 - 13: type: keyword
 : 3360 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 3361 - 69: **`tls.client.x509.subject.locality`** :   List of
 : 3362 - 13: type: keyword
 : 3363 - 22: example: San Francisco
 : 3364 - 84: **`tls.client.x509.subject.organization`** :   Lis
 : 3365 - 13: type: keyword
 : 3366 - 22: example: Example, Inc.
 : 3367 - 99: **`tls.client.x509.subject.organizational_unit`** 
 : 3368 - 13: type: keyword
 : 3369 - 97: **`tls.client.x509.subject.state_or_province`** : 
 : 3370 - 13: type: keyword
 : 3371 - 19: example: California
 : 3372 - 64: **`tls.client.x509.version_number`** :   Version o
 : 3373 - 13: type: keyword
 : 3374 - 10: example: 3
 : 3375 - 91: **`tls.curve`** :   String indicating the curve us
 : 3376 - 13: type: keyword
 : 3377 - 18: example: secp256r1
 : 3378 - 128: **`tls.established`** :   Boolean flag indicating 
 : 3379 - 13: type: boolean
 : 3380 - 256: **`tls.next_protocol`** :   String indicating the 
 : 3381 - 13: type: keyword
 : 3382 - 17: example: http/1.1
 : 3383 - 114: **`tls.resumed`** :   Boolean flag indicating if t
 : 3384 - 13: type: boolean
 : 3385 - 199: **`tls.server.certificate`** :   PEM-encoded stand
 : 3386 - 13: type: keyword
 : 3387 - 14: example: MII…​
 : 3388 - 252: **`tls.server.certificate_chain`** :   Array of PE
 : 3389 - 13: type: keyword
 : 3390 - 27: example: ["MII…​", "MII…​"]
 : 3391 - 228: **`tls.server.hash.md5`** :   Certificate fingerpr
 : 3392 - 13: type: keyword
 : 3393 - 41: example: 0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC
 : 3394 - 230: **`tls.server.hash.sha1`** :   Certificate fingerp
 : 3395 - 13: type: keyword
 : 3396 - 49: example: 9E393D93138888D288266C2D915214D1D1CCEB2A
 : 3397 - 234: **`tls.server.hash.sha256`** :   Certificate finge
 : 3398 - 13: type: keyword
 : 3399 - 73: example: 0687F666A054EF17A08E2F2162EAB4CBC0D265E1D
 : 3400 - 99: **`tls.server.issuer`** :   Subject of the issuer 
 : 3401 - 13: type: keyword
 : 3402 - 71: example: CN=Example Root CA, OU=Infrastructure Tea
 : 3403 - 104: **`tls.server.ja3s`** :   A hash that identifies s
 : 3404 - 13: type: keyword
 : 3405 - 41: example: 394441ab65754e2207b1e1b457b3641d
 : 3406 - 106: **`tls.server.not_after`** :   Timestamp indicatin
 : 3407 - 10: type: date
 : 3408 - 33: example: 2021-01-01T00:00:00.000Z
 : 3409 - 103: **`tls.server.not_before`** :   Timestamp indicati
 : 3410 - 10: type: date
 : 3411 - 33: example: 1970-01-01T00:00:00.000Z
 : 3412 - 86: **`tls.server.subject`** :   Subject of the x.509 
 : 3413 - 13: type: keyword
 : 3414 - 71: example: CN=www.example.com, OU=Infrastructure Tea
 : 3415 - 229: **`tls.server.x509.alternative_names`** :   List o
 : 3416 - 13: type: keyword
 : 3417 - 21: example: *.elastic.co
 : 3418 - 103: **`tls.server.x509.issuer.common_name`** :   List 
 : 3419 - 13: type: keyword
 : 3420 - 46: example: Example SHA2 High Assurance Server CA
 : 3421 - 64: **`tls.server.x509.issuer.country`** :   List of c
 : 3422 - 13: type: keyword
 : 3423 - 11: example: US
 : 3424 - 109: **`tls.server.x509.issuer.distinguished_name`** : 
 : 3425 - 13: type: keyword
 : 3426 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 3427 - 68: **`tls.server.x509.issuer.locality`** :   List of 
 : 3428 - 13: type: keyword
 : 3429 - 22: example: Mountain View
 : 3430 - 105: **`tls.server.x509.issuer.organization`** :   List
 : 3431 - 13: type: keyword
 : 3432 - 20: example: Example Inc
 : 3433 - 120: **`tls.server.x509.issuer.organizational_unit`** :
 : 3434 - 13: type: keyword
 : 3435 - 24: example: www.example.com
 : 3436 - 96: **`tls.server.x509.issuer.state_or_province`** :  
 : 3437 - 13: type: keyword
 : 3438 - 19: example: California
 : 3439 - 96: **`tls.server.x509.not_after`** :   Time at which 
 : 3440 - 10: type: date
 : 3441 - 34: example: 2020-07-16 03:15:39+00:00
 : 3442 - 93: **`tls.server.x509.not_before`** :   Time at which
 : 3443 - 10: type: date
 : 3444 - 34: example: 2019-08-16 01:40:25+00:00
 : 3445 - 89: **`tls.server.x509.public_key_algorithm`** :   Alg
 : 3446 - 13: type: keyword
 : 3447 - 12: example: RSA
 : 3448 - 129: **`tls.server.x509.public_key_curve`** :   The cur
 : 3449 - 13: type: keyword
 : 3450 - 17: example: nistp521
 : 3451 - 113: **`tls.server.x509.public_key_exponent`** :   Expo
 : 3452 - 10: type: long
 : 3453 - 14: example: 65537
 : 3454 - 21: Field is not indexed.
 : 3455 - 83: **`tls.server.x509.public_key_size`** :   The size
 : 3456 - 10: type: long
 : 3457 - 13: example: 2048
 : 3458 - 209: **`tls.server.x509.serial_number`** :   Unique ser
 : 3459 - 13: type: keyword
 : 3460 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 3461 - 232: **`tls.server.x509.signature_algorithm`** :   Iden
 : 3462 - 13: type: keyword
 : 3463 - 19: example: SHA256-RSA
 : 3464 - 83: **`tls.server.x509.subject.common_name`** :   List
 : 3465 - 13: type: keyword
 : 3466 - 34: example: shared.global.example.net
 : 3467 - 64: **`tls.server.x509.subject.country`** :   List of 
 : 3468 - 13: type: keyword
 : 3469 - 11: example: US
 : 3470 - 111: **`tls.server.x509.subject.distinguished_name`** :
 : 3471 - 13: type: keyword
 : 3472 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 3473 - 69: **`tls.server.x509.subject.locality`** :   List of
 : 3474 - 13: type: keyword
 : 3475 - 22: example: San Francisco
 : 3476 - 84: **`tls.server.x509.subject.organization`** :   Lis
 : 3477 - 13: type: keyword
 : 3478 - 22: example: Example, Inc.
 : 3479 - 99: **`tls.server.x509.subject.organizational_unit`** 
 : 3480 - 13: type: keyword
 : 3481 - 97: **`tls.server.x509.subject.state_or_province`** : 
 : 3482 - 13: type: keyword
 : 3483 - 19: example: California
 : 3484 - 64: **`tls.server.x509.version_number`** :   Version o
 : 3485 - 13: type: keyword
 : 3486 - 10: example: 3
 : 3487 - 82: **`tls.version`** :   Numeric part of the version 
 : 3488 - 13: type: keyword
 : 3489 - 12: example: 1.2
 : 3490 - 94: **`tls.version_protocol`** :   Normalized lowercas
 : 3491 - 13: type: keyword
 : 3492 - 12: example: tls
 : 3493 - 190: **`span.id`** :   Unique identifier of the span wi
 : 3494 - 13: type: keyword
 : 3495 - 25: example: 3ff9a8981b7ccd5a
 : 3496 - 195: **`trace.id`** :   Unique identifier of the trace.
 : 3497 - 13: type: keyword
 : 3498 - 41: example: 4bf92f3577b34da6a3ce929d0e0e4736
 : 3499 - 193: **`transaction.id`** :   Unique identifier of the 
 : 3500 - 13: type: keyword
 : 3501 - 25: example: 00f067aa0ba902b7
 : 3502 - 13: ## url [_url]
 : 3503 - 125: URL fields provide support for complete or partial
 : 3504 - 368: **`url.domain`** :   Domain of the url, such as "w
 : 3505 - 13: type: keyword
 : 3506 - 23: example: www.elastic.co
 : 3507 - 424: **`url.extension`** :   The field contains the fil
 : 3508 - 13: type: keyword
 : 3509 - 12: example: png
 : 3510 - 109: **`url.fragment`** :   Portion of the url after th
 : 3511 - 13: type: keyword
 : 3512 - 169: **`url.full`** :   If full URLs are important to y
 : 3513 - 14: type: wildcard
 : 3514 - 62: example: https://www.elastic.co:443/search?q=elast
 : 3515 - 45: **`url.full.text`** :   type: match_only_text
 : 3516 - 291: **`url.original`** :   Unmodified original url as 
 : 3517 - 14: type: wildcard
 : 3518 - 89: example: https://www.elastic.co:443/search?q=elast
 : 3519 - 49: **`url.original.text`** :   type: match_only_text
 : 3520 - 47: **`url.password`** :   Password of the request.
 : 3521 - 13: type: keyword
 : 3522 - 58: **`url.path`** :   Path of the request, such as "/
 : 3523 - 14: type: wildcard
 : 3524 - 52: **`url.port`** :   Port of the request, such as 44
 : 3525 - 10: type: long
 : 3526 - 12: example: 443
 : 3527 - 14: format: string
 : 3528 - 348: **`url.query`** :   The query field describes the 
 : 3529 - 13: type: keyword
 : 3530 - 385: **`url.registered_domain`** :   The highest regist
 : 3531 - 13: type: keyword
 : 3532 - 20: example: example.com
 : 3533 - 101: **`url.scheme`** :   Scheme of the request, such a
 : 3534 - 13: type: keyword
 : 3535 - 14: example: https
 : 3536 - 554: **`url.subdomain`** :   The subdomain portion of a
 : 3537 - 13: type: keyword
 : 3538 - 13: example: east
 : 3539 - 421: **`url.top_level_domain`** :   The effective top l
 : 3540 - 13: type: keyword
 : 3541 - 14: example: co.uk
 : 3542 - 47: **`url.username`** :   Username of the request.
 : 3543 - 13: type: keyword
 : 3544 - 17: ## user [_user_2]
 : 3545 - 205: The user fields describe information about the use
 : 3546 - 130: **`user.changes.domain`** :   Name of the director
 : 3547 - 13: type: keyword
 : 3548 - 48: **`user.changes.email`** :   User email address.
 : 3549 - 13: type: keyword
 : 3550 - 64: **`user.changes.full_name`** :   User’s full name,
 : 3551 - 13: type: keyword
 : 3552 - 24: example: Albert Einstein
 : 3553 - 59: **`user.changes.full_name.text`** :   type: match_
 : 3554 - 137: **`user.changes.group.domain`** :   Name of the di
 : 3555 - 13: type: keyword
 : 3556 - 87: **`user.changes.group.id`** :   Unique identifier 
 : 3557 - 13: type: keyword
 : 3558 - 52: **`user.changes.group.name`** :   Name of the grou
 : 3559 - 13: type: keyword
 : 3560 - 188: **`user.changes.hash`** :   Unique user hash to co
 : 3561 - 13: type: keyword
 : 3562 - 56: **`user.changes.id`** :   Unique identifier of the
 : 3563 - 13: type: keyword
 : 3564 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 3565 - 60: **`user.changes.name`** :   Short name or login of
 : 3566 - 13: type: keyword
 : 3567 - 19: example: a.einstein
 : 3568 - 54: **`user.changes.name.text`** :   type: match_only_
 : 3569 - 74: **`user.changes.roles`** :   Array of user roles a
 : 3570 - 13: type: keyword
 : 3571 - 43: example: ["kibana_admin", "reporting_user"]
 : 3572 - 122: **`user.domain`** :   Name of the directory the us
 : 3573 - 13: type: keyword
 : 3574 - 132: **`user.effective.domain`** :   Name of the direct
 : 3575 - 13: type: keyword
 : 3576 - 50: **`user.effective.email`** :   User email address.
 : 3577 - 13: type: keyword
 : 3578 - 66: **`user.effective.full_name`** :   User’s full nam
 : 3579 - 13: type: keyword
 : 3580 - 24: example: Albert Einstein
 : 3581 - 61: **`user.effective.full_name.text`** :   type: matc
 : 3582 - 139: **`user.effective.group.domain`** :   Name of the 
 : 3583 - 13: type: keyword
 : 3584 - 89: **`user.effective.group.id`** :   Unique identifie
 : 3585 - 13: type: keyword
 : 3586 - 54: **`user.effective.group.name`** :   Name of the gr
 : 3587 - 13: type: keyword
 : 3588 - 190: **`user.effective.hash`** :   Unique user hash to 
 : 3589 - 13: type: keyword
 : 3590 - 58: **`user.effective.id`** :   Unique identifier of t
 : 3591 - 13: type: keyword
 : 3592 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 3593 - 62: **`user.effective.name`** :   Short name or login 
 : 3594 - 13: type: keyword
 : 3595 - 19: example: a.einstein
 : 3596 - 56: **`user.effective.name.text`** :   type: match_onl
 : 3597 - 76: **`user.effective.roles`** :   Array of user roles
 : 3598 - 13: type: keyword
 : 3599 - 43: example: ["kibana_admin", "reporting_user"]
 : 3600 - 40: **`user.email`** :   User email address.
 : 3601 - 13: type: keyword
 : 3602 - 56: **`user.full_name`** :   User’s full name, if avai
 : 3603 - 13: type: keyword
 : 3604 - 24: example: Albert Einstein
 : 3605 - 51: **`user.full_name.text`** :   type: match_only_tex
 : 3606 - 129: **`user.group.domain`** :   Name of the directory 
 : 3607 - 13: type: keyword
 : 3608 - 79: **`user.group.id`** :   Unique identifier for the 
 : 3609 - 13: type: keyword
 : 3610 - 44: **`user.group.name`** :   Name of the group.
 : 3611 - 13: type: keyword
 : 3612 - 180: **`user.hash`** :   Unique user hash to correlate 
 : 3613 - 13: type: keyword
 : 3614 - 48: **`user.id`** :   Unique identifier of the user.
 : 3615 - 13: type: keyword
 : 3616 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 3617 - 52: **`user.name`** :   Short name or login of the use
 : 3618 - 13: type: keyword
 : 3619 - 19: example: a.einstein
 : 3620 - 46: **`user.name.text`** :   type: match_only_text
 : 3621 - 66: **`user.roles`** :   Array of user roles at the ti
 : 3622 - 13: type: keyword
 : 3623 - 43: example: ["kibana_admin", "reporting_user"]
 : 3624 - 129: **`user.target.domain`** :   Name of the directory
 : 3625 - 13: type: keyword
 : 3626 - 47: **`user.target.email`** :   User email address.
 : 3627 - 13: type: keyword
 : 3628 - 63: **`user.target.full_name`** :   User’s full name, 
 : 3629 - 13: type: keyword
 : 3630 - 24: example: Albert Einstein
 : 3631 - 58: **`user.target.full_name.text`** :   type: match_o
 : 3632 - 136: **`user.target.group.domain`** :   Name of the dir
 : 3633 - 13: type: keyword
 : 3634 - 86: **`user.target.group.id`** :   Unique identifier f
 : 3635 - 13: type: keyword
 : 3636 - 51: **`user.target.group.name`** :   Name of the group
 : 3637 - 13: type: keyword
 : 3638 - 187: **`user.target.hash`** :   Unique user hash to cor
 : 3639 - 13: type: keyword
 : 3640 - 55: **`user.target.id`** :   Unique identifier of the 
 : 3641 - 13: type: keyword
 : 3642 - 57: example: S-1-5-21-202424912787-2692429404-23519567
 : 3643 - 59: **`user.target.name`** :   Short name or login of 
 : 3644 - 13: type: keyword
 : 3645 - 19: example: a.einstein
 : 3646 - 53: **`user.target.name.text`** :   type: match_only_t
 : 3647 - 73: **`user.target.roles`** :   Array of user roles at
 : 3648 - 13: type: keyword
 : 3649 - 43: example: ["kibana_admin", "reporting_user"]
 : 3650 - 27: ## user_agent [_user_agent]
 : 3651 - 140: The user_agent fields normally come from a browser
 : 3652 - 52: **`user_agent.device.name`** :   Name of the devic
 : 3653 - 13: type: keyword
 : 3654 - 15: example: iPhone
 : 3655 - 49: **`user_agent.name`** :   Name of the user agent.
 : 3656 - 13: type: keyword
 : 3657 - 15: example: Safari
 : 3658 - 57: **`user_agent.original`** :   Unparsed user_agent 
 : 3659 - 13: type: keyword
 : 3660 - 144: example: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 l
 : 3661 - 56: **`user_agent.original.text`** :   type: match_onl
 : 3662 - 84: **`user_agent.os.family`** :   OS family (such as 
 : 3663 - 13: type: keyword
 : 3664 - 15: example: debian
 : 3665 - 87: **`user_agent.os.full`** :   Operating system name
 : 3666 - 13: type: keyword
 : 3667 - 22: example: Mac OS Mojave
 : 3668 - 55: **`user_agent.os.full.text`** :   type: match_only
 : 3669 - 79: **`user_agent.os.kernel`** :   Operating system ke
 : 3670 - 13: type: keyword
 : 3671 - 26: example: 4.4.0-112-generic
 : 3672 - 72: **`user_agent.os.name`** :   Operating system name
 : 3673 - 13: type: keyword
 : 3674 - 17: example: Mac OS X
 : 3675 - 55: **`user_agent.os.name.text`** :   type: match_only
 : 3676 - 90: **`user_agent.os.platform`** :   Operating system 
 : 3677 - 13: type: keyword
 : 3678 - 15: example: darwin
 : 3679 - 376: **`user_agent.os.type`** :   Use the `os.type` fie
 : 3680 - 13: type: keyword
 : 3681 - 14: example: macos
 : 3682 - 73: **`user_agent.os.version`** :   Operating system v
 : 3683 - 13: type: keyword
 : 3684 - 16: example: 10.14.1
 : 3685 - 55: **`user_agent.version`** :   Version of the user a
 : 3686 - 13: type: keyword
 : 3687 - 13: example: 12.0
 : 3688 - 15: ## vlan [_vlan]
 : 3689 - 975: The VLAN fields are used to identify 802.1q tag(s)
 : 3690 - 54: **`vlan.id`** :   VLAN ID as reported by the obser
 : 3691 - 13: type: keyword
 : 3692 - 11: example: 10
 : 3693 - 67: **`vlan.name`** :   Optional VLAN name as reported
 : 3694 - 13: type: keyword
 : 3695 - 16: example: outside
 : 3696 - 33: ## vulnerability [_vulnerability]
 : 3697 - 97: The vulnerability fields describe information abou
 : 3698 - 285: **`vulnerability.category`** :   The type of syste
 : 3699 - 13: type: keyword
 : 3700 - 21: example: ["Firewall"]
 : 3701 - 138: **`vulnerability.classification`** :   The classif
 : 3702 - 13: type: keyword
 : 3703 - 13: example: CVSS
 : 3704 - 195: **`vulnerability.description`** :   The descriptio
 : 3705 - 13: type: keyword
 : 3706 - 70: example: In macOS before 2.12.6, there is a vulner
 : 3707 - 62: **`vulnerability.description.text`** :   type: mat
 : 3708 - 132: **`vulnerability.enumeration`** :   The type of id
 : 3709 - 13: type: keyword
 : 3710 - 12: example: CVE
 : 3711 - 223: **`vulnerability.id`** :   The identification (ID)
 : 3712 - 13: type: keyword
 : 3713 - 23: example: CVE-2019-00001
 : 3714 - 141: **`vulnerability.reference`** :   A resource that 
 : 3715 - 13: type: keyword
 : 3716 - 69: example: https://cve.mitre.org/cgi-bin/cvename.cgi
 : 3717 - 75: **`vulnerability.report_id`** :   The report or sc
 : 3718 - 13: type: keyword
 : 3719 - 22: example: 20191018.0001
 : 3720 - 84: **`vulnerability.scanner.vendor`** :   The name of
 : 3721 - 13: type: keyword
 : 3722 - 16: example: Tenable
 : 3723 - 364: **`vulnerability.score.base`** :   Scores can rang
 : 3724 - 11: type: float
 : 3725 - 12: example: 5.5
 : 3726 - 308: **`vulnerability.score.environmental`** :   Scores
 : 3727 - 11: type: float
 : 3728 - 12: example: 5.5
 : 3729 - 262: **`vulnerability.score.temporal`** :   Scores can 
 : 3730 - 11: type: float
 : 3731 - 513: **`vulnerability.score.version`** :   The National
 : 3732 - 13: type: keyword
 : 3733 - 12: example: 2.0
 : 3734 - 194: **`vulnerability.severity`** :   The severity of t
 : 3735 - 13: type: keyword
 : 3736 - 17: example: Critical
 : 3737 - 15: ## x509 [_x509]
 : 3738 - 609: This implements the common core fields for x509 ce
 : 3739 - 218: **`x509.alternative_names`** :   List of subject a
 : 3740 - 13: type: keyword
 : 3741 - 21: example: *.elastic.co
 : 3742 - 92: **`x509.issuer.common_name`** :   List of common n
 : 3743 - 13: type: keyword
 : 3744 - 46: example: Example SHA2 High Assurance Server CA
 : 3745 - 53: **`x509.issuer.country`** :   List of country © co
 : 3746 - 13: type: keyword
 : 3747 - 11: example: US
 : 3748 - 98: **`x509.issuer.distinguished_name`** :   Distingui
 : 3749 - 13: type: keyword
 : 3750 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
 : 3751 - 57: **`x509.issuer.locality`** :   List of locality na
 : 3752 - 13: type: keyword
 : 3753 - 22: example: Mountain View
 : 3754 - 94: **`x509.issuer.organization`** :   List of organiz
 : 3755 - 13: type: keyword
 : 3756 - 20: example: Example Inc
 : 3757 - 109: **`x509.issuer.organizational_unit`** :   List of 
 : 3758 - 13: type: keyword
 : 3759 - 24: example: www.example.com
 : 3760 - 85: **`x509.issuer.state_or_province`** :   List of st
 : 3761 - 13: type: keyword
 : 3762 - 19: example: California
 : 3763 - 85: **`x509.not_after`** :   Time at which the certifi
 : 3764 - 10: type: date
 : 3765 - 34: example: 2020-07-16 03:15:39+00:00
 : 3766 - 82: **`x509.not_before`** :   Time at which the certif
 : 3767 - 10: type: date
 : 3768 - 34: example: 2019-08-16 01:40:25+00:00
 : 3769 - 78: **`x509.public_key_algorithm`** :   Algorithm used
 : 3770 - 13: type: keyword
 : 3771 - 12: example: RSA
 : 3772 - 118: **`x509.public_key_curve`** :   The curve used by 
 : 3773 - 13: type: keyword
 : 3774 - 17: example: nistp521
 : 3775 - 102: **`x509.public_key_exponent`** :   Exponent used t
 : 3776 - 10: type: long
 : 3777 - 14: example: 65537
 : 3778 - 21: Field is not indexed.
 : 3779 - 72: **`x509.public_key_size`** :   The size of the pub
 : 3780 - 10: type: long
 : 3781 - 13: example: 2048
 : 3782 - 198: **`x509.serial_number`** :   Unique serial number 
 : 3783 - 13: type: keyword
 : 3784 - 33: example: 55FBB9C7DEBF09809D12CCAA
 : 3785 - 221: **`x509.signature_algorithm`** :   Identifier for 
 : 3786 - 13: type: keyword
 : 3787 - 19: example: SHA256-RSA
 : 3788 - 72: **`x509.subject.common_name`** :   List of common 
 : 3789 - 13: type: keyword
 : 3790 - 34: example: shared.global.example.net
 : 3791 - 53: **`x509.subject.country`** :   List of country © c
 : 3792 - 13: type: keyword
 : 3793 - 11: example: US
 : 3794 - 100: **`x509.subject.distinguished_name`** :   Distingu
 : 3795 - 13: type: keyword
 : 3796 - 92: example: C=US, ST=California, L=San Francisco, O=E
 : 3797 - 58: **`x509.subject.locality`** :   List of locality n
 : 3798 - 13: type: keyword
 : 3799 - 22: example: San Francisco
 : 3800 - 73: **`x509.subject.organization`** :   List of organi
 : 3801 - 13: type: keyword
 : 3802 - 22: example: Example, Inc.
 : 3803 - 88: **`x509.subject.organizational_unit`** :   List of
 : 3804 - 13: type: keyword
 : 3805 - 86: **`x509.subject.state_or_province`** :   List of s
 : 3806 - 13: type: keyword
 : 3807 - 19: example: California
 : 3808 - 53: **`x509.version_number`** :   Version of x509 form
 : 3809 - 13: type: keyword
 : 3810 - 10: example: 3