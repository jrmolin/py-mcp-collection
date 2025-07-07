 : 0 - 13: mapped_pages:
 : 1 - 82: - https://www.elastic.co/guide/en/beats/auditbeat/
 : 2 - 251401: # ECS fields [exported-fields-ecs]  This section d
   : 3 - 34: # ECS fields [exported-fields-ecs]
   : 4 - 124: This section defines Elastic Common Schema (ECS) f
   : 5 - 275: This is an exhaustive list, and fields listed here
   : 6 - 43: See the ECS reference for more information.
   : 7 - 342: **`@timestamp`** :   Date/time when the event orig
   : 8 - 10: type: date
   : 9 - 33: example: 2016-05-23T08:05:34.853Z
   : 10 - 14: required: True
   : 11 - 192: **`labels`** :   Custom key/value pairs. Can be us
   : 12 - 12: type: object
   : 13 - 56: example: {"application": "foo-bar", "env": "produc
   : 14 - 317: **`message`** :   For log events the message field
   : 15 - 21: type: match_only_text
   : 16 - 20: example: Hello World
   : 17 - 55: **`tags`** :   List of keywords used to tag each e
   : 18 - 13: type: keyword
   : 19 - 31: example: ["production", "env2"]
   : 20 - 1760: ## agent [_agent]  The agent fields contain the da
     : 21 - 17: ## agent [_agent]
     : 22 - 364: The agent fields contain the data about the softwa
     : 23 - 196: **`agent.build.original`** :   Extended build info
     : 24 - 13: type: keyword
     : 25 - 135: example: metricbeat version 7.6.0 (amd64), libbeat
     : 26 - 147: **`agent.ephemeral_id`** :   Ephemeral identifier 
     : 27 - 13: type: keyword
     : 28 - 17: example: 8a4f500f
     : 29 - 109: **`agent.id`** :   Unique identifier of this agent
     : 30 - 13: type: keyword
     : 31 - 17: example: 8a4f500d
     : 32 - 320: **`agent.name`** :   Custom name of the agent. Thi
     : 33 - 13: type: keyword
     : 34 - 12: example: foo
     : 35 - 230: **`agent.type`** :   Type of the agent. The agent 
     : 36 - 13: type: keyword
     : 37 - 17: example: filebeat
     : 38 - 45: **`agent.version`** :   Version of the agent.
     : 39 - 13: type: keyword
     : 40 - 18: example: 6.0.0-rc2
   : 41 - 614: ## as [_as]  An autonomous system (AS) is a collec
     : 42 - 11: ## as [_as]
     : 43 - 271: An autonomous system (AS) is a collection of conne
     : 44 - 154: **`as.number`** :   Unique number allocated to the
     : 45 - 10: type: long
     : 46 - 14: example: 15169
     : 47 - 49: **`as.organization.name`** :   Organization name.
     : 48 - 13: type: keyword
     : 49 - 19: example: Google LLC
     : 50 - 57: **`as.organization.name.text`** :   type: match_on
   : 51 - 7133: ## client [_client]  A client is defined as the in
     : 52 - 19: ## client [_client]
     : 53 - 896: A client is defined as the initiator of a network 
     : 54 - 290: **`client.address`** :   Some event client address
     : 55 - 13: type: keyword
     : 56 - 161: **`client.as.number`** :   Unique number allocated
     : 57 - 10: type: long
     : 58 - 14: example: 15169
     : 59 - 56: **`client.as.organization.name`** :   Organization
     : 60 - 13: type: keyword
     : 61 - 19: example: Google LLC
     : 62 - 64: **`client.as.organization.name.text`** :   type: m
     : 63 - 64: **`client.bytes`** :   Bytes sent from the client 
     : 64 - 10: type: long
     : 65 - 12: example: 184
     : 66 - 13: format: bytes
     : 67 - 228: **`client.domain`** :   The domain name of the cli
     : 68 - 13: type: keyword
     : 69 - 24: example: foo.example.com
     : 70 - 41: **`client.geo.city_name`** :   City name.
     : 71 - 13: type: keyword
     : 72 - 17: example: Montreal
     : 73 - 82: **`client.geo.continent_code`** :   Two-letter cod
     : 74 - 13: type: keyword
     : 75 - 11: example: NA
     : 76 - 58: **`client.geo.continent_name`** :   Name of the co
     : 77 - 13: type: keyword
     : 78 - 22: example: North America
     : 79 - 55: **`client.geo.country_iso_code`** :   Country ISO 
     : 80 - 13: type: keyword
     : 81 - 11: example: CA
     : 82 - 47: **`client.geo.country_name`** :   Country name.
     : 83 - 13: type: keyword
     : 84 - 15: example: Canada
     : 85 - 53: **`client.geo.location`** :   Longitude and latitu
     : 86 - 15: type: geo_point
     : 87 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 88 - 269: **`client.geo.name`** :   User-defined description
     : 89 - 13: type: keyword
     : 90 - 18: example: boston-dc
     : 91 - 198: **`client.geo.postal_code`** :   Postal code assoc
     : 92 - 13: type: keyword
     : 93 - 14: example: 94040
     : 94 - 53: **`client.geo.region_iso_code`** :   Region ISO co
     : 95 - 13: type: keyword
     : 96 - 14: example: CA-QC
     : 97 - 45: **`client.geo.region_name`** :   Region name.
     : 98 - 13: type: keyword
     : 99 - 15: example: Quebec
     : 100 - 89: **`client.geo.timezone`** :   The time zone of the
     : 101 - 13: type: keyword
     : 102 - 39: example: America/Argentina/Buenos_Aires
     : 103 - 60: **`client.ip`** :   IP address of the client (IPv4
     : 104 - 8: type: ip
     : 105 - 280: **`client.mac`** :   MAC address of the client. Th
     : 106 - 13: type: keyword
     : 107 - 26: example: 00-00-5E-00-53-23
     : 108 - 174: **`client.nat.ip`** :   Translated IP of source ba
     : 109 - 8: type: ip
     : 110 - 178: **`client.nat.port`** :   Translated port of sourc
     : 111 - 10: type: long
     : 112 - 14: format: string
     : 113 - 68: **`client.packets`** :   Packets sent from the cli
     : 114 - 10: type: long
     : 115 - 11: example: 12
     : 116 - 41: **`client.port`** :   Port of the client.
     : 117 - 10: type: long
     : 118 - 14: format: string
     : 119 - 391: **`client.registered_domain`** :   The highest reg
     : 120 - 13: type: keyword
     : 121 - 20: example: example.com
     : 122 - 557: **`client.subdomain`** :   The subdomain portion o
     : 123 - 13: type: keyword
     : 124 - 13: example: east
     : 125 - 424: **`client.top_level_domain`** :   The effective to
     : 126 - 13: type: keyword
     : 127 - 14: example: co.uk
     : 128 - 129: **`client.user.domain`** :   Name of the directory
     : 129 - 13: type: keyword
     : 130 - 47: **`client.user.email`** :   User email address.
     : 131 - 13: type: keyword
     : 132 - 63: **`client.user.full_name`** :   User’s full name, 
     : 133 - 13: type: keyword
     : 134 - 24: example: Albert Einstein
     : 135 - 58: **`client.user.full_name.text`** :   type: match_o
     : 136 - 136: **`client.user.group.domain`** :   Name of the dir
     : 137 - 13: type: keyword
     : 138 - 86: **`client.user.group.id`** :   Unique identifier f
     : 139 - 13: type: keyword
     : 140 - 51: **`client.user.group.name`** :   Name of the group
     : 141 - 13: type: keyword
     : 142 - 187: **`client.user.hash`** :   Unique user hash to cor
     : 143 - 13: type: keyword
     : 144 - 55: **`client.user.id`** :   Unique identifier of the 
     : 145 - 13: type: keyword
     : 146 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 147 - 59: **`client.user.name`** :   Short name or login of 
     : 148 - 13: type: keyword
     : 149 - 19: example: a.einstein
     : 150 - 53: **`client.user.name.text`** :   type: match_only_t
     : 151 - 73: **`client.user.roles`** :   Array of user roles at
     : 152 - 13: type: keyword
     : 153 - 43: example: ["kibana_admin", "reporting_user"]
   : 154 - 5499: ## cloud [_cloud]  Fields related to the cloud or 
     : 155 - 17: ## cloud [_cloud]
     : 156 - 73: Fields related to the cloud or infrastructure the 
     : 157 - 205: **`cloud.account.id`** :   The cloud account or or
     : 158 - 13: type: keyword
     : 159 - 21: example: 666777888999
     : 160 - 186: **`cloud.account.name`** :   The cloud account nam
     : 161 - 13: type: keyword
     : 162 - 20: example: elastic-dev
     : 163 - 104: **`cloud.availability_zone`** :   Availability zon
     : 164 - 13: type: keyword
     : 165 - 19: example: us-east-1c
     : 166 - 60: **`cloud.instance.id`** :   Instance ID of the hos
     : 167 - 13: type: keyword
     : 168 - 28: example: i-1234567890abcdef0
     : 169 - 64: **`cloud.instance.name`** :   Instance name of the
     : 170 - 13: type: keyword
     : 171 - 62: **`cloud.machine.type`** :   Machine type of the h
     : 172 - 13: type: keyword
     : 173 - 18: example: t2.medium
     : 174 - 212: **`cloud.origin.account.id`** :   The cloud accoun
     : 175 - 13: type: keyword
     : 176 - 21: example: 666777888999
     : 177 - 193: **`cloud.origin.account.name`** :   The cloud acco
     : 178 - 13: type: keyword
     : 179 - 20: example: elastic-dev
     : 180 - 111: **`cloud.origin.availability_zone`** :   Availabil
     : 181 - 13: type: keyword
     : 182 - 19: example: us-east-1c
     : 183 - 67: **`cloud.origin.instance.id`** :   Instance ID of 
     : 184 - 13: type: keyword
     : 185 - 28: example: i-1234567890abcdef0
     : 186 - 71: **`cloud.origin.instance.name`** :   Instance name
     : 187 - 13: type: keyword
     : 188 - 69: **`cloud.origin.machine.type`** :   Machine type o
     : 189 - 13: type: keyword
     : 190 - 18: example: t2.medium
     : 191 - 116: **`cloud.origin.project.id`** :   The cloud projec
     : 192 - 13: type: keyword
     : 193 - 19: example: my-project
     : 194 - 116: **`cloud.origin.project.name`** :   The cloud proj
     : 195 - 13: type: keyword
     : 196 - 19: example: my project
     : 197 - 112: **`cloud.origin.provider`** :   Name of the cloud 
     : 198 - 13: type: keyword
     : 199 - 12: example: aws
     : 200 - 89: **`cloud.origin.region`** :   Region in which this
     : 201 - 13: type: keyword
     : 202 - 18: example: us-east-1
     : 203 - 276: **`cloud.origin.service.name`** :   The cloud serv
     : 204 - 13: type: keyword
     : 205 - 15: example: lambda
     : 206 - 109: **`cloud.project.id`** :   The cloud project ident
     : 207 - 13: type: keyword
     : 208 - 19: example: my-project
     : 209 - 109: **`cloud.project.name`** :   The cloud project nam
     : 210 - 13: type: keyword
     : 211 - 19: example: my project
     : 212 - 105: **`cloud.provider`** :   Name of the cloud provide
     : 213 - 13: type: keyword
     : 214 - 12: example: aws
     : 215 - 82: **`cloud.region`** :   Region in which this host, 
     : 216 - 13: type: keyword
     : 217 - 18: example: us-east-1
     : 218 - 269: **`cloud.service.name`** :   The cloud service nam
     : 219 - 13: type: keyword
     : 220 - 15: example: lambda
     : 221 - 212: **`cloud.target.account.id`** :   The cloud accoun
     : 222 - 13: type: keyword
     : 223 - 21: example: 666777888999
     : 224 - 193: **`cloud.target.account.name`** :   The cloud acco
     : 225 - 13: type: keyword
     : 226 - 20: example: elastic-dev
     : 227 - 111: **`cloud.target.availability_zone`** :   Availabil
     : 228 - 13: type: keyword
     : 229 - 19: example: us-east-1c
     : 230 - 67: **`cloud.target.instance.id`** :   Instance ID of 
     : 231 - 13: type: keyword
     : 232 - 28: example: i-1234567890abcdef0
     : 233 - 71: **`cloud.target.instance.name`** :   Instance name
     : 234 - 13: type: keyword
     : 235 - 69: **`cloud.target.machine.type`** :   Machine type o
     : 236 - 13: type: keyword
     : 237 - 18: example: t2.medium
     : 238 - 116: **`cloud.target.project.id`** :   The cloud projec
     : 239 - 13: type: keyword
     : 240 - 19: example: my-project
     : 241 - 116: **`cloud.target.project.name`** :   The cloud proj
     : 242 - 13: type: keyword
     : 243 - 19: example: my project
     : 244 - 112: **`cloud.target.provider`** :   Name of the cloud 
     : 245 - 13: type: keyword
     : 246 - 12: example: aws
     : 247 - 89: **`cloud.target.region`** :   Region in which this
     : 248 - 13: type: keyword
     : 249 - 18: example: us-east-1
     : 250 - 276: **`cloud.target.service.name`** :   The cloud serv
     : 251 - 13: type: keyword
     : 252 - 15: example: lambda
   : 253 - 1950: ## code_signature [_code_signature]  These fields 
     : 254 - 35: ## code_signature [_code_signature]
     : 255 - 62: These fields contain information about binary code
     : 256 - 222: **`code_signature.digest_algorithm`** :   The hash
     : 257 - 13: type: keyword
     : 258 - 15: example: sha256
     : 259 - 77: **`code_signature.exists`** :   Boolean to capture
     : 260 - 13: type: boolean
     : 261 - 13: example: true
     : 262 - 193: **`code_signature.signing_id`** :   The identifier
     : 263 - 13: type: keyword
     : 264 - 28: example: com.apple.xpc.proxy
     : 265 - 256: **`code_signature.status`** :   Additional informa
     : 266 - 13: type: keyword
     : 267 - 29: example: ERROR_UNTRUSTED_ROOT
     : 268 - 69: **`code_signature.subject_name`** :   Subject name
     : 269 - 13: type: keyword
     : 270 - 30: example: Microsoft Corporation
     : 271 - 186: **`code_signature.team_id`** :   The team identifi
     : 272 - 13: type: keyword
     : 273 - 19: example: EQHXZ8M8AV
     : 274 - 98: **`code_signature.timestamp`** :   Date and time w
     : 275 - 10: type: date
     : 276 - 29: example: 2021-01-01T12:10:30Z
     : 277 - 229: **`code_signature.trusted`** :   Stores the trust 
     : 278 - 13: type: boolean
     : 279 - 13: example: true
     : 280 - 164: **`code_signature.valid`** :   Boolean to capture 
     : 281 - 13: type: boolean
     : 282 - 13: example: true
   : 283 - 1591: ## container [_container]  Container fields are us
     : 284 - 25: ## container [_container]
     : 285 - 178: Container fields are used for meta information abo
     : 286 - 142: **`container.cpu.usage`** :   Percent CPU used whi
     : 287 - 18: type: scaled_float
     : 288 - 149: **`container.disk.read.bytes`** :   The total numb
     : 289 - 10: type: long
     : 290 - 153: **`container.disk.write.bytes`** :   The total num
     : 291 - 10: type: long
     : 292 - 43: **`container.id`** :   Unique container id.
     : 293 - 13: type: keyword
     : 294 - 76: **`container.image.name`** :   Name of the image t
     : 295 - 13: type: keyword
     : 296 - 51: **`container.image.tag`** :   Container image tags
     : 297 - 13: type: keyword
     : 298 - 40: **`container.labels`** :   Image labels.
     : 299 - 12: type: object
     : 300 - 105: **`container.memory.usage`** :   Memory usage perc
     : 301 - 18: type: scaled_float
     : 302 - 40: **`container.name`** :   Container name.
     : 303 - 13: type: keyword
     : 304 - 154: **`container.network.egress.bytes`** :   The numbe
     : 305 - 10: type: long
     : 306 - 155: **`container.network.ingress.bytes`** :   The numb
     : 307 - 10: type: long
     : 308 - 60: **`container.runtime`** :   Runtime managing this 
     : 309 - 13: type: keyword
     : 310 - 15: example: docker
   : 311 - 2261: ## data_stream [_data_stream]  The data_stream fie
     : 312 - 29: ## data_stream [_data_stream]
     : 313 - 863: The data_stream fields take part in defining the n
     : 314 - 537: **`data_stream.dataset`** :   The field can contai
     : 315 - 22: type: constant_keyword
     : 316 - 21: example: nginx.access
     : 317 - 507: **`data_stream.namespace`** :   A user defined nam
     : 318 - 22: type: constant_keyword
     : 319 - 19: example: production
     : 320 - 186: **`data_stream.type`** :   An overarching type for
     : 321 - 22: type: constant_keyword
     : 322 - 13: example: logs
   : 323 - 7008: ## destination [_destination_2]  Destination field
     : 324 - 31: ## destination [_destination_2]
     : 325 - 580: Destination fields capture details about the recei
     : 326 - 300: **`destination.address`** :   Some event destinati
     : 327 - 13: type: keyword
     : 328 - 166: **`destination.as.number`** :   Unique number allo
     : 329 - 10: type: long
     : 330 - 14: example: 15169
     : 331 - 61: **`destination.as.organization.name`** :   Organiz
     : 332 - 13: type: keyword
     : 333 - 19: example: Google LLC
     : 334 - 69: **`destination.as.organization.name.text`** :   ty
     : 335 - 74: **`destination.bytes`** :   Bytes sent from the de
     : 336 - 10: type: long
     : 337 - 12: example: 184
     : 338 - 13: format: bytes
     : 339 - 238: **`destination.domain`** :   The domain name of th
     : 340 - 13: type: keyword
     : 341 - 24: example: foo.example.com
     : 342 - 46: **`destination.geo.city_name`** :   City name.
     : 343 - 13: type: keyword
     : 344 - 17: example: Montreal
     : 345 - 87: **`destination.geo.continent_code`** :   Two-lette
     : 346 - 13: type: keyword
     : 347 - 11: example: NA
     : 348 - 63: **`destination.geo.continent_name`** :   Name of t
     : 349 - 13: type: keyword
     : 350 - 22: example: North America
     : 351 - 60: **`destination.geo.country_iso_code`** :   Country
     : 352 - 13: type: keyword
     : 353 - 11: example: CA
     : 354 - 52: **`destination.geo.country_name`** :   Country nam
     : 355 - 13: type: keyword
     : 356 - 15: example: Canada
     : 357 - 58: **`destination.geo.location`** :   Longitude and l
     : 358 - 15: type: geo_point
     : 359 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 360 - 274: **`destination.geo.name`** :   User-defined descri
     : 361 - 13: type: keyword
     : 362 - 18: example: boston-dc
     : 363 - 203: **`destination.geo.postal_code`** :   Postal code 
     : 364 - 13: type: keyword
     : 365 - 14: example: 94040
     : 366 - 58: **`destination.geo.region_iso_code`** :   Region I
     : 367 - 13: type: keyword
     : 368 - 14: example: CA-QC
     : 369 - 50: **`destination.geo.region_name`** :   Region name.
     : 370 - 13: type: keyword
     : 371 - 15: example: Quebec
     : 372 - 94: **`destination.geo.timezone`** :   The time zone o
     : 373 - 13: type: keyword
     : 374 - 39: example: America/Argentina/Buenos_Aires
     : 375 - 70: **`destination.ip`** :   IP address of the destina
     : 376 - 8: type: ip
     : 377 - 290: **`destination.mac`** :   MAC address of the desti
     : 378 - 13: type: keyword
     : 379 - 26: example: 00-00-5E-00-53-23
     : 380 - 166: **`destination.nat.ip`** :   Translated ip of dest
     : 381 - 8: type: ip
     : 382 - 145: **`destination.nat.port`** :   Port the source ses
     : 383 - 10: type: long
     : 384 - 14: format: string
     : 385 - 78: **`destination.packets`** :   Packets sent from th
     : 386 - 10: type: long
     : 387 - 11: example: 12
     : 388 - 51: **`destination.port`** :   Port of the destination
     : 389 - 10: type: long
     : 390 - 14: format: string
     : 391 - 401: **`destination.registered_domain`** :   The highes
     : 392 - 13: type: keyword
     : 393 - 20: example: example.com
     : 394 - 562: **`destination.subdomain`** :   The subdomain port
     : 395 - 13: type: keyword
     : 396 - 13: example: east
     : 397 - 429: **`destination.top_level_domain`** :   The effecti
     : 398 - 13: type: keyword
     : 399 - 14: example: co.uk
     : 400 - 134: **`destination.user.domain`** :   Name of the dire
     : 401 - 13: type: keyword
     : 402 - 52: **`destination.user.email`** :   User email addres
     : 403 - 13: type: keyword
     : 404 - 68: **`destination.user.full_name`** :   User’s full n
     : 405 - 13: type: keyword
     : 406 - 24: example: Albert Einstein
     : 407 - 63: **`destination.user.full_name.text`** :   type: ma
     : 408 - 141: **`destination.user.group.domain`** :   Name of th
     : 409 - 13: type: keyword
     : 410 - 91: **`destination.user.group.id`** :   Unique identif
     : 411 - 13: type: keyword
     : 412 - 56: **`destination.user.group.name`** :   Name of the 
     : 413 - 13: type: keyword
     : 414 - 192: **`destination.user.hash`** :   Unique user hash t
     : 415 - 13: type: keyword
     : 416 - 60: **`destination.user.id`** :   Unique identifier of
     : 417 - 13: type: keyword
     : 418 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 419 - 64: **`destination.user.name`** :   Short name or logi
     : 420 - 13: type: keyword
     : 421 - 19: example: a.einstein
     : 422 - 58: **`destination.user.name.text`** :   type: match_o
     : 423 - 78: **`destination.user.roles`** :   Array of user rol
     : 424 - 13: type: keyword
     : 425 - 43: example: ["kibana_admin", "reporting_user"]
   : 426 - 3983: ## dll [_dll]  These fields contain information ab
     : 427 - 13: ## dll [_dll]
     : 428 - 88: These fields contain information about code librar
     : 429 - 312: Many operating systems refer to "shared code libra
     : 430 - 226: **`dll.code_signature.digest_algorithm`** :   The 
     : 431 - 13: type: keyword
     : 432 - 15: example: sha256
     : 433 - 81: **`dll.code_signature.exists`** :   Boolean to cap
     : 434 - 13: type: boolean
     : 435 - 13: example: true
     : 436 - 197: **`dll.code_signature.signing_id`** :   The identi
     : 437 - 13: type: keyword
     : 438 - 28: example: com.apple.xpc.proxy
     : 439 - 260: **`dll.code_signature.status`** :   Additional inf
     : 440 - 13: type: keyword
     : 441 - 29: example: ERROR_UNTRUSTED_ROOT
     : 442 - 73: **`dll.code_signature.subject_name`** :   Subject 
     : 443 - 13: type: keyword
     : 444 - 30: example: Microsoft Corporation
     : 445 - 190: **`dll.code_signature.team_id`** :   The team iden
     : 446 - 13: type: keyword
     : 447 - 19: example: EQHXZ8M8AV
     : 448 - 102: **`dll.code_signature.timestamp`** :   Date and ti
     : 449 - 10: type: date
     : 450 - 29: example: 2021-01-01T12:10:30Z
     : 451 - 233: **`dll.code_signature.trusted`** :   Stores the tr
     : 452 - 13: type: boolean
     : 453 - 13: example: true
     : 454 - 168: **`dll.code_signature.valid`** :   Boolean to capt
     : 455 - 13: type: boolean
     : 456 - 13: example: true
     : 457 - 32: **`dll.hash.md5`** :   MD5 hash.
     : 458 - 13: type: keyword
     : 459 - 34: **`dll.hash.sha1`** :   SHA1 hash.
     : 460 - 13: type: keyword
     : 461 - 38: **`dll.hash.sha256`** :   SHA256 hash.
     : 462 - 13: type: keyword
     : 463 - 38: **`dll.hash.sha512`** :   SHA512 hash.
     : 464 - 13: type: keyword
     : 465 - 38: **`dll.hash.ssdeep`** :   SSDEEP hash.
     : 466 - 13: type: keyword
     : 467 - 92: **`dll.name`** :   Name of the library. This gener
     : 468 - 13: type: keyword
     : 469 - 21: example: kernel32.dll
     : 470 - 49: **`dll.path`** :   Full file path of the library.
     : 471 - 13: type: keyword
     : 472 - 41: example: C:\Windows\System32\kernel32.dll
     : 473 - 67: **`dll.pe.architecture`** :   CPU architecture tar
     : 474 - 13: type: keyword
     : 475 - 12: example: x64
     : 476 - 85: **`dll.pe.company`** :   Internal company name of 
     : 477 - 13: type: keyword
     : 478 - 30: example: Microsoft Corporation
     : 479 - 88: **`dll.pe.description`** :   Internal description 
     : 480 - 13: type: keyword
     : 481 - 14: example: Paint
     : 482 - 85: **`dll.pe.file_version`** :   Internal version of 
     : 483 - 13: type: keyword
     : 484 - 23: example: 6.3.9600.17415
     : 485 - 357: **`dll.pe.imphash`** :   A hash of the imports in 
     : 486 - 13: type: keyword
     : 487 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 488 - 88: **`dll.pe.original_file_name`** :   Internal name 
     : 489 - 13: type: keyword
     : 490 - 20: example: MSPAINT.EXE
     : 491 - 85: **`dll.pe.product`** :   Internal product name of 
     : 492 - 13: type: keyword
     : 493 - 45: example: Microsoft® Windows® Operating System
   : 494 - 4934: ## dns [_dns]  Fields describing DNS queries and a
     : 495 - 13: ## dns [_dns]
     : 496 - 300: Fields describing DNS queries and answers. DNS eve
     : 497 - 512: **`dns.answers`** :   An array containing an objec
     : 498 - 12: type: object
     : 499 - 84: **`dns.answers.class`** :   The class of DNS data 
     : 500 - 13: type: keyword
     : 501 - 11: example: IN
     : 502 - 139: **`dns.answers.data`** :   The data describing the
     : 503 - 13: type: keyword
     : 504 - 20: example: 10.10.10.10
     : 505 - 267: **`dns.answers.name`** :   The domain name to whic
     : 506 - 13: type: keyword
     : 507 - 24: example: www.example.com
     : 508 - 178: **`dns.answers.ttl`** :   The time interval in sec
     : 509 - 10: type: long
     : 510 - 12: example: 180
     : 511 - 78: **`dns.answers.type`** :   The type of data contai
     : 512 - 13: type: keyword
     : 513 - 14: example: CNAME
     : 514 - 111: **`dns.header_flags`** :   Array of 2 letter DNS h
     : 515 - 13: type: keyword
     : 516 - 21: example: ["RD", "RA"]
     : 517 - 134: **`dns.id`** :   The DNS packet identifier assigne
     : 518 - 13: type: keyword
     : 519 - 14: example: 62111
     : 520 - 170: **`dns.op_code`** :   The DNS operation code that 
     : 521 - 13: type: keyword
     : 522 - 14: example: QUERY
     : 523 - 64: **`dns.question.class`** :   The class of records 
     : 524 - 13: type: keyword
     : 525 - 11: example: IN
     : 526 - 337: **`dns.question.name`** :   The name being queried
     : 527 - 13: type: keyword
     : 528 - 24: example: www.example.com
     : 529 - 390: **`dns.question.registered_domain`** :   The highe
     : 530 - 13: type: keyword
     : 531 - 20: example: example.com
     : 532 - 250: **`dns.question.subdomain`** :   The subdomain is 
     : 533 - 13: type: keyword
     : 534 - 12: example: www
     : 535 - 430: **`dns.question.top_level_domain`** :   The effect
     : 536 - 13: type: keyword
     : 537 - 14: example: co.uk
     : 538 - 61: **`dns.question.type`** :   The type of record bei
     : 539 - 13: type: keyword
     : 540 - 13: example: AAAA
     : 541 - 337: **`dns.resolved_ip`** :   Array containing all IPs
     : 542 - 8: type: ip
     : 543 - 39: example: ["10.10.10.10", "10.10.10.11"]
     : 544 - 50: **`dns.response_code`** :   The DNS response code.
     : 545 - 13: type: keyword
     : 546 - 16: example: NOERROR
     : 547 - 402: **`dns.type`** :   The type of DNS event captured,
     : 548 - 13: type: keyword
     : 549 - 15: example: answer
   : 550 - 386: ## ecs [_ecs]  Meta-information specific to ECS.  
     : 551 - 13: ## ecs [_ecs]
     : 552 - 33: Meta-information specific to ECS.
     : 553 - 289: **`ecs.version`** :   ECS version this event confo
     : 554 - 13: type: keyword
     : 555 - 14: example: 1.0.0
     : 556 - 14: required: True
   : 557 - 2883: ## elf [_elf]  These fields contain Linux Executab
     : 558 - 13: ## elf [_elf]
     : 559 - 69: These fields contain Linux Executable Linkable For
     : 560 - 64: **`elf.architecture`** :   Machine architecture of
     : 561 - 13: type: keyword
     : 562 - 15: example: x86-64
     : 563 - 51: **`elf.byte_order`** :   Byte sequence of ELF file
     : 564 - 13: type: keyword
     : 565 - 22: example: Little Endian
     : 566 - 48: **`elf.cpu_type`** :   CPU type of the ELF file.
     : 567 - 13: type: keyword
     : 568 - 14: example: Intel
     : 569 - 160: **`elf.creation_date`** :   Extracted when possibl
     : 570 - 10: type: date
     : 571 - 63: **`elf.exports`** :   List of exported element nam
     : 572 - 15: type: flattened
     : 573 - 87: **`elf.header.abi_version`** :   Version of the EL
     : 574 - 13: type: keyword
     : 575 - 56: **`elf.header.class`** :   Header class of the ELF
     : 576 - 13: type: keyword
     : 577 - 55: **`elf.header.data`** :   Data table of the ELF he
     : 578 - 13: type: keyword
     : 579 - 66: **`elf.header.entrypoint`** :   Header entrypoint 
     : 580 - 10: type: long
     : 581 - 14: format: string
     : 582 - 65: **`elf.header.object_version`** :   "0x1" for orig
     : 583 - 13: type: keyword
     : 584 - 79: **`elf.header.os_abi`** :   Application Binary Int
     : 585 - 13: type: keyword
     : 586 - 54: **`elf.header.type`** :   Header type of the ELF f
     : 587 - 13: type: keyword
     : 588 - 55: **`elf.header.version`** :   Version of the ELF he
     : 589 - 13: type: keyword
     : 590 - 63: **`elf.imports`** :   List of imported element nam
     : 591 - 15: type: flattened
     : 592 - 191: **`elf.sections`** :   An array containing an obje
     : 593 - 12: type: nested
     : 594 - 79: **`elf.sections.chi2`** :   Chi-square probability
     : 595 - 10: type: long
     : 596 - 14: format: number
     : 597 - 76: **`elf.sections.entropy`** :   Shannon entropy cal
     : 598 - 10: type: long
     : 599 - 14: format: number
     : 600 - 52: **`elf.sections.flags`** :   ELF Section List flag
     : 601 - 13: type: keyword
     : 602 - 50: **`elf.sections.name`** :   ELF Section List name.
     : 603 - 13: type: keyword
     : 604 - 63: **`elf.sections.physical_offset`** :   ELF Section
     : 605 - 13: type: keyword
     : 606 - 68: **`elf.sections.physical_size`** :   ELF Section L
     : 607 - 10: type: long
     : 608 - 13: format: bytes
     : 609 - 50: **`elf.sections.type`** :   ELF Section List type.
     : 610 - 13: type: keyword
     : 611 - 72: **`elf.sections.virtual_address`** :   ELF Section
     : 612 - 10: type: long
     : 613 - 14: format: string
     : 614 - 66: **`elf.sections.virtual_size`** :   ELF Section Li
     : 615 - 10: type: long
     : 616 - 14: format: string
     : 617 - 191: **`elf.segments`** :   An array containing an obje
     : 618 - 12: type: nested
     : 619 - 60: **`elf.segments.sections`** :   ELF object segment
     : 620 - 13: type: keyword
     : 621 - 52: **`elf.segments.type`** :   ELF object segment typ
     : 622 - 13: type: keyword
     : 623 - 80: **`elf.shared_libraries`** :   List of shared libr
     : 624 - 13: type: keyword
     : 625 - 57: **`elf.telfhash`** :   telfhash symbol hash for EL
     : 626 - 13: type: keyword
   : 627 - 666: ## error [_error]  These fields can represent erro
     : 628 - 17: ## error [_error]
     : 629 - 154: These fields can represent errors of any kind. Use
     : 630 - 53: **`error.code`** :   Error code describing the err
     : 631 - 13: type: keyword
     : 632 - 51: **`error.id`** :   Unique identifier for the error
     : 633 - 13: type: keyword
     : 634 - 38: **`error.message`** :   Error message.
     : 635 - 21: type: match_only_text
     : 636 - 72: **`error.stack_trace`** :   The stack trace of thi
     : 637 - 14: type: wildcard
     : 638 - 54: **`error.stack_trace.text`** :   type: match_only_
     : 639 - 88: **`error.type`** :   The type of the error, for ex
     : 640 - 13: type: keyword
     : 641 - 39: example: java.lang.NullPointerException
   : 642 - 11163: ## event [_event]  The event fields are used for c
     : 643 - 17: ## event [_event]
     : 644 - 749: The event fields are used for context information 
     : 645 - 259: **`event.action`** :   The action captured by the 
     : 646 - 13: type: keyword
     : 647 - 29: example: user-password-change
     : 648 - 1107: **`event.agent_id_status`** :   Agents are normall
     : 649 - 13: type: keyword
     : 650 - 17: example: verified
     : 651 - 488: **`event.category`** :   This is one of four ECS C
     : 652 - 13: type: keyword
     : 653 - 23: example: authentication
     : 654 - 251: **`event.code`** :   Identification code for this 
     : 655 - 13: type: keyword
     : 656 - 13: example: 4648
     : 657 - 620: **`event.created`** :   event.created contains the
     : 658 - 10: type: date
     : 659 - 33: example: 2016-05-23T08:05:34.857Z
     : 660 - 326: **`event.dataset`** :   Name of the dataset. If an
     : 661 - 13: type: keyword
     : 662 - 22: example: apache.access
     : 663 - 169: **`event.duration`** :   Duration of the event in 
     : 664 - 10: type: long
     : 665 - 16: format: duration
     : 666 - 108: **`event.end`** :   event.end contains the date wh
     : 667 - 10: type: date
     : 668 - 110: **`event.hash`** :   Hash (perhaps logstash finger
     : 669 - 13: type: keyword
     : 670 - 43: example: 123456789012345678901234567890ABCD
     : 671 - 51: **`event.id`** :   Unique ID to describe the event
     : 672 - 13: type: keyword
     : 673 - 17: example: 8a4f500d
     : 674 - 426: **`event.ingested`** :   Timestamp when an event a
     : 675 - 10: type: date
     : 676 - 33: example: 2016-05-23T08:05:35.101Z
     : 677 - 595: **`event.kind`** :   This is one of four ECS Categ
     : 678 - 13: type: keyword
     : 679 - 14: example: alert
     : 680 - 246: **`event.module`** :   Name of the module this dat
     : 681 - 13: type: keyword
     : 682 - 15: example: apache
     : 683 - 437: **`event.original`** :   Raw text message of entir
     : 684 - 13: type: keyword
     : 685 - 21: Field is not indexed.
     : 686 - 913: **`event.outcome`** :   This is one of four ECS Ca
     : 687 - 13: type: keyword
     : 688 - 16: example: success
     : 689 - 315: **`event.provider`** :   Source of the event. Even
     : 690 - 13: type: keyword
     : 691 - 15: example: kernel
     : 692 - 418: **`event.reason`** :   Reason why this event happe
     : 693 - 13: type: keyword
     : 694 - 41: example: Terminated an unexpected process
     : 695 - 230: **`event.reference`** :   Reference URL linking to
     : 696 - 13: type: keyword
     : 697 - 50: example: https://system.example.com/event/#0001234
     : 698 - 128: **`event.risk_score`** :   Risk score or priority 
     : 699 - 11: type: float
     : 700 - 242: **`event.risk_score_norm`** :   Normalized risk sc
     : 701 - 11: type: float
     : 702 - 207: **`event.sequence`** :   Sequence number of the ev
     : 703 - 10: type: long
     : 704 - 14: format: string
     : 705 - 576: **`event.severity`** :   The numeric severity of t
     : 706 - 10: type: long
     : 707 - 10: example: 7
     : 708 - 14: format: string
     : 709 - 115: **`event.start`** :   event.start contains the dat
     : 710 - 10: type: date
     : 711 - 329: **`event.timezone`** :   This field should be popu
     : 712 - 13: type: keyword
     : 713 - 435: **`event.type`** :   This is one of four ECS Categ
     : 714 - 13: type: keyword
     : 715 - 299: **`event.url`** :   URL linking to an external sys
     : 716 - 13: type: keyword
     : 717 - 80: example: https://mysystem.example.com/alert/5271de
   : 718 - 712: ## faas [_faas]  The user fields describe informat
     : 719 - 15: ## faas [_faas]
     : 720 - 99: The user fields describe information about the fun
     : 721 - 77: **`faas.coldstart`** :   Boolean value indicating 
     : 722 - 13: type: boolean
     : 723 - 76: **`faas.execution`** :   The execution ID of the c
     : 724 - 13: type: keyword
     : 725 - 45: example: af9d5aa4-a685-4c5f-a22b-444f80b3cc28
     : 726 - 58: **`faas.trigger`** :   Details about the function 
     : 727 - 12: type: nested
     : 728 - 86: **`faas.trigger.request_id`** :   The ID of the tr
     : 729 - 13: type: keyword
     : 730 - 18: example: 123456789
     : 731 - 133: **`faas.trigger.type`** :   The trigger for the fu
     : 732 - 13: type: keyword
     : 733 - 13: example: http
   : 734 - 14039: ## file [_file_2]  A file is defined as a set of i
     : 735 - 17: ## file [_file_2]
     : 736 - 352: A file is defined as a set of information that has
     : 737 - 113: **`file.accessed`** :   Last time the file was acc
     : 738 - 10: type: date
     : 739 - 254: **`file.attributes`** :   Array of file attributes
     : 740 - 13: type: keyword
     : 741 - 31: example: ["readonly", "system"]
     : 742 - 227: **`file.code_signature.digest_algorithm`** :   The
     : 743 - 13: type: keyword
     : 744 - 15: example: sha256
     : 745 - 82: **`file.code_signature.exists`** :   Boolean to ca
     : 746 - 13: type: boolean
     : 747 - 13: example: true
     : 748 - 198: **`file.code_signature.signing_id`** :   The ident
     : 749 - 13: type: keyword
     : 750 - 28: example: com.apple.xpc.proxy
     : 751 - 261: **`file.code_signature.status`** :   Additional in
     : 752 - 13: type: keyword
     : 753 - 29: example: ERROR_UNTRUSTED_ROOT
     : 754 - 74: **`file.code_signature.subject_name`** :   Subject
     : 755 - 13: type: keyword
     : 756 - 30: example: Microsoft Corporation
     : 757 - 191: **`file.code_signature.team_id`** :   The team ide
     : 758 - 13: type: keyword
     : 759 - 19: example: EQHXZ8M8AV
     : 760 - 103: **`file.code_signature.timestamp`** :   Date and t
     : 761 - 10: type: date
     : 762 - 29: example: 2021-01-01T12:10:30Z
     : 763 - 234: **`file.code_signature.trusted`** :   Stores the t
     : 764 - 13: type: boolean
     : 765 - 13: example: true
     : 766 - 169: **`file.code_signature.valid`** :   Boolean to cap
     : 767 - 13: type: boolean
     : 768 - 13: example: true
     : 769 - 97: **`file.created`** :   File creation time. Note th
     : 770 - 10: type: date
     : 771 - 230: **`file.ctime`** :   Last time the file attributes
     : 772 - 10: type: date
     : 773 - 60: **`file.device`** :   Device that is the source of
     : 774 - 13: type: keyword
     : 775 - 12: example: sda
     : 776 - 115: **`file.directory`** :   Directory where the file 
     : 777 - 13: type: keyword
     : 778 - 20: example: /home/alice
     : 779 - 165: **`file.drive_letter`** :   Drive letter where the
     : 780 - 13: type: keyword
     : 781 - 10: example: C
     : 782 - 69: **`file.elf.architecture`** :   Machine architectu
     : 783 - 13: type: keyword
     : 784 - 15: example: x86-64
     : 785 - 56: **`file.elf.byte_order`** :   Byte sequence of ELF
     : 786 - 13: type: keyword
     : 787 - 22: example: Little Endian
     : 788 - 53: **`file.elf.cpu_type`** :   CPU type of the ELF fi
     : 789 - 13: type: keyword
     : 790 - 14: example: Intel
     : 791 - 165: **`file.elf.creation_date`** :   Extracted when po
     : 792 - 10: type: date
     : 793 - 68: **`file.elf.exports`** :   List of exported elemen
     : 794 - 15: type: flattened
     : 795 - 92: **`file.elf.header.abi_version`** :   Version of t
     : 796 - 13: type: keyword
     : 797 - 61: **`file.elf.header.class`** :   Header class of th
     : 798 - 13: type: keyword
     : 799 - 60: **`file.elf.header.data`** :   Data table of the E
     : 800 - 13: type: keyword
     : 801 - 71: **`file.elf.header.entrypoint`** :   Header entryp
     : 802 - 10: type: long
     : 803 - 14: format: string
     : 804 - 70: **`file.elf.header.object_version`** :   "0x1" for
     : 805 - 13: type: keyword
     : 806 - 84: **`file.elf.header.os_abi`** :   Application Binar
     : 807 - 13: type: keyword
     : 808 - 59: **`file.elf.header.type`** :   Header type of the 
     : 809 - 13: type: keyword
     : 810 - 60: **`file.elf.header.version`** :   Version of the E
     : 811 - 13: type: keyword
     : 812 - 68: **`file.elf.imports`** :   List of imported elemen
     : 813 - 15: type: flattened
     : 814 - 196: **`file.elf.sections`** :   An array containing an
     : 815 - 12: type: nested
     : 816 - 84: **`file.elf.sections.chi2`** :   Chi-square probab
     : 817 - 10: type: long
     : 818 - 14: format: number
     : 819 - 81: **`file.elf.sections.entropy`** :   Shannon entrop
     : 820 - 10: type: long
     : 821 - 14: format: number
     : 822 - 57: **`file.elf.sections.flags`** :   ELF Section List
     : 823 - 13: type: keyword
     : 824 - 55: **`file.elf.sections.name`** :   ELF Section List 
     : 825 - 13: type: keyword
     : 826 - 68: **`file.elf.sections.physical_offset`** :   ELF Se
     : 827 - 13: type: keyword
     : 828 - 73: **`file.elf.sections.physical_size`** :   ELF Sect
     : 829 - 10: type: long
     : 830 - 13: format: bytes
     : 831 - 55: **`file.elf.sections.type`** :   ELF Section List 
     : 832 - 13: type: keyword
     : 833 - 77: **`file.elf.sections.virtual_address`** :   ELF Se
     : 834 - 10: type: long
     : 835 - 14: format: string
     : 836 - 71: **`file.elf.sections.virtual_size`** :   ELF Secti
     : 837 - 10: type: long
     : 838 - 14: format: string
     : 839 - 196: **`file.elf.segments`** :   An array containing an
     : 840 - 12: type: nested
     : 841 - 65: **`file.elf.segments.sections`** :   ELF object se
     : 842 - 13: type: keyword
     : 843 - 57: **`file.elf.segments.type`** :   ELF object segmen
     : 844 - 13: type: keyword
     : 845 - 85: **`file.elf.shared_libraries`** :   List of shared
     : 846 - 13: type: keyword
     : 847 - 62: **`file.elf.telfhash`** :   telfhash symbol hash f
     : 848 - 13: type: keyword
     : 849 - 197: **`file.extension`** :   File extension, excluding
     : 850 - 13: type: keyword
     : 851 - 12: example: png
     : 852 - 787: **`file.fork_name`** :   A fork is additional data
     : 853 - 13: type: keyword
     : 854 - 23: example: Zone.Identifer
     : 855 - 54: **`file.gid`** :   Primary group ID (GID) of the f
     : 856 - 13: type: keyword
     : 857 - 13: example: 1001
     : 858 - 52: **`file.group`** :   Primary group name of the fil
     : 859 - 13: type: keyword
     : 860 - 14: example: alice
     : 861 - 33: **`file.hash.md5`** :   MD5 hash.
     : 862 - 13: type: keyword
     : 863 - 35: **`file.hash.sha1`** :   SHA1 hash.
     : 864 - 13: type: keyword
     : 865 - 39: **`file.hash.sha256`** :   SHA256 hash.
     : 866 - 13: type: keyword
     : 867 - 39: **`file.hash.sha512`** :   SHA512 hash.
     : 868 - 13: type: keyword
     : 869 - 39: **`file.hash.ssdeep`** :   SSDEEP hash.
     : 870 - 13: type: keyword
     : 871 - 67: **`file.inode`** :   Inode representing the file i
     : 872 - 13: type: keyword
     : 873 - 15: example: 256383
     : 874 - 214: **`file.mime_type`** :   MIME type should identify
     : 875 - 13: type: keyword
     : 876 - 61: **`file.mode`** :   Mode of the file in octal repr
     : 877 - 13: type: keyword
     : 878 - 13: example: 0640
     : 879 - 61: **`file.mtime`** :   Last time the file content wa
     : 880 - 10: type: date
     : 881 - 84: **`file.name`** :   Name of the file including the
     : 882 - 13: type: keyword
     : 883 - 20: example: example.png
     : 884 - 43: **`file.owner`** :   File owner’s username.
     : 885 - 13: type: keyword
     : 886 - 14: example: alice
     : 887 - 121: **`file.path`** :   Full path to the file, includi
     : 888 - 13: type: keyword
     : 889 - 32: example: /home/alice/example.png
     : 890 - 46: **`file.path.text`** :   type: match_only_text
     : 891 - 68: **`file.pe.architecture`** :   CPU architecture ta
     : 892 - 13: type: keyword
     : 893 - 12: example: x64
     : 894 - 86: **`file.pe.company`** :   Internal company name of
     : 895 - 13: type: keyword
     : 896 - 30: example: Microsoft Corporation
     : 897 - 89: **`file.pe.description`** :   Internal description
     : 898 - 13: type: keyword
     : 899 - 14: example: Paint
     : 900 - 86: **`file.pe.file_version`** :   Internal version of
     : 901 - 13: type: keyword
     : 902 - 23: example: 6.3.9600.17415
     : 903 - 358: **`file.pe.imphash`** :   A hash of the imports in
     : 904 - 13: type: keyword
     : 905 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 906 - 89: **`file.pe.original_file_name`** :   Internal name
     : 907 - 13: type: keyword
     : 908 - 20: example: MSPAINT.EXE
     : 909 - 86: **`file.pe.product`** :   Internal product name of
     : 910 - 13: type: keyword
     : 911 - 45: example: Microsoft® Windows® Operating System
     : 912 - 81: **`file.size`** :   File size in bytes. Only relev
     : 913 - 10: type: long
     : 914 - 14: example: 16384
     : 915 - 52: **`file.target_path`** :   Target path for symlink
     : 916 - 13: type: keyword
     : 917 - 53: **`file.target_path.text`** :   type: match_only_t
     : 918 - 54: **`file.type`** :   File type (file, dir, or symli
     : 919 - 13: type: keyword
     : 920 - 13: example: file
     : 921 - 84: **`file.uid`** :   The user ID (UID) or security i
     : 922 - 13: type: keyword
     : 923 - 13: example: 1001
     : 924 - 223: **`file.x509.alternative_names`** :   List of subj
     : 925 - 13: type: keyword
     : 926 - 21: example: *.elastic.co
     : 927 - 97: **`file.x509.issuer.common_name`** :   List of com
     : 928 - 13: type: keyword
     : 929 - 46: example: Example SHA2 High Assurance Server CA
     : 930 - 58: **`file.x509.issuer.country`** :   List of country
     : 931 - 13: type: keyword
     : 932 - 11: example: US
     : 933 - 103: **`file.x509.issuer.distinguished_name`** :   Dist
     : 934 - 13: type: keyword
     : 935 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 936 - 62: **`file.x509.issuer.locality`** :   List of locali
     : 937 - 13: type: keyword
     : 938 - 22: example: Mountain View
     : 939 - 99: **`file.x509.issuer.organization`** :   List of or
     : 940 - 13: type: keyword
     : 941 - 20: example: Example Inc
     : 942 - 114: **`file.x509.issuer.organizational_unit`** :   Lis
     : 943 - 13: type: keyword
     : 944 - 24: example: www.example.com
     : 945 - 90: **`file.x509.issuer.state_or_province`** :   List 
     : 946 - 13: type: keyword
     : 947 - 19: example: California
     : 948 - 90: **`file.x509.not_after`** :   Time at which the ce
     : 949 - 10: type: date
     : 950 - 34: example: 2020-07-16 03:15:39+00:00
     : 951 - 87: **`file.x509.not_before`** :   Time at which the c
     : 952 - 10: type: date
     : 953 - 34: example: 2019-08-16 01:40:25+00:00
     : 954 - 83: **`file.x509.public_key_algorithm`** :   Algorithm
     : 955 - 13: type: keyword
     : 956 - 12: example: RSA
     : 957 - 123: **`file.x509.public_key_curve`** :   The curve use
     : 958 - 13: type: keyword
     : 959 - 17: example: nistp521
     : 960 - 107: **`file.x509.public_key_exponent`** :   Exponent u
     : 961 - 10: type: long
     : 962 - 14: example: 65537
     : 963 - 21: Field is not indexed.
     : 964 - 77: **`file.x509.public_key_size`** :   The size of th
     : 965 - 10: type: long
     : 966 - 13: example: 2048
     : 967 - 203: **`file.x509.serial_number`** :   Unique serial nu
     : 968 - 13: type: keyword
     : 969 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 970 - 226: **`file.x509.signature_algorithm`** :   Identifier
     : 971 - 13: type: keyword
     : 972 - 19: example: SHA256-RSA
     : 973 - 77: **`file.x509.subject.common_name`** :   List of co
     : 974 - 13: type: keyword
     : 975 - 34: example: shared.global.example.net
     : 976 - 58: **`file.x509.subject.country`** :   List of countr
     : 977 - 13: type: keyword
     : 978 - 11: example: US
     : 979 - 105: **`file.x509.subject.distinguished_name`** :   Dis
     : 980 - 13: type: keyword
     : 981 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 982 - 63: **`file.x509.subject.locality`** :   List of local
     : 983 - 13: type: keyword
     : 984 - 22: example: San Francisco
     : 985 - 78: **`file.x509.subject.organization`** :   List of o
     : 986 - 13: type: keyword
     : 987 - 22: example: Example, Inc.
     : 988 - 93: **`file.x509.subject.organizational_unit`** :   Li
     : 989 - 13: type: keyword
     : 990 - 91: **`file.x509.subject.state_or_province`** :   List
     : 991 - 13: type: keyword
     : 992 - 19: example: California
     : 993 - 58: **`file.x509.version_number`** :   Version of x509
     : 994 - 13: type: keyword
     : 995 - 10: example: 3
   : 996 - 1532: ## geo [_geo]  Geo fields can carry data about a s
     : 997 - 13: ## geo [_geo]
     : 998 - 169: Geo fields can carry data about a specific locatio
     : 999 - 34: **`geo.city_name`** :   City name.
     : 1000 - 13: type: keyword
     : 1001 - 17: example: Montreal
     : 1002 - 75: **`geo.continent_code`** :   Two-letter code repre
     : 1003 - 13: type: keyword
     : 1004 - 11: example: NA
     : 1005 - 51: **`geo.continent_name`** :   Name of the continent
     : 1006 - 13: type: keyword
     : 1007 - 22: example: North America
     : 1008 - 48: **`geo.country_iso_code`** :   Country ISO code.
     : 1009 - 13: type: keyword
     : 1010 - 11: example: CA
     : 1011 - 40: **`geo.country_name`** :   Country name.
     : 1012 - 13: type: keyword
     : 1013 - 15: example: Canada
     : 1014 - 46: **`geo.location`** :   Longitude and latitude.
     : 1015 - 15: type: geo_point
     : 1016 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 1017 - 262: **`geo.name`** :   User-defined description of a l
     : 1018 - 13: type: keyword
     : 1019 - 18: example: boston-dc
     : 1020 - 191: **`geo.postal_code`** :   Postal code associated w
     : 1021 - 13: type: keyword
     : 1022 - 14: example: 94040
     : 1023 - 46: **`geo.region_iso_code`** :   Region ISO code.
     : 1024 - 13: type: keyword
     : 1025 - 14: example: CA-QC
     : 1026 - 38: **`geo.region_name`** :   Region name.
     : 1027 - 13: type: keyword
     : 1028 - 15: example: Quebec
     : 1029 - 82: **`geo.timezone`** :   The time zone of the locati
     : 1030 - 13: type: keyword
     : 1031 - 39: example: America/Argentina/Buenos_Aires
   : 1032 - 387: ## group [_group_3]  The group fields are meant to
     : 1033 - 19: ## group [_group_3]
     : 1034 - 78: The group fields are meant to represent groups tha
     : 1035 - 124: **`group.domain`** :   Name of the directory the g
     : 1036 - 13: type: keyword
     : 1037 - 74: **`group.id`** :   Unique identifier for the group
     : 1038 - 13: type: keyword
     : 1039 - 39: **`group.name`** :   Name of the group.
     : 1040 - 13: type: keyword
   : 1041 - 770: ## hash [_hash]  The hash fields represent differe
     : 1042 - 15: ## hash [_hash]
     : 1043 - 508: The hash fields represent different bitwise hash a
     : 1044 - 28: **`hash.md5`** :   MD5 hash.
     : 1045 - 13: type: keyword
     : 1046 - 30: **`hash.sha1`** :   SHA1 hash.
     : 1047 - 13: type: keyword
     : 1048 - 34: **`hash.sha256`** :   SHA256 hash.
     : 1049 - 13: type: keyword
     : 1050 - 34: **`hash.sha512`** :   SHA512 hash.
     : 1051 - 13: type: keyword
     : 1052 - 34: **`hash.ssdeep`** :   SSDEEP hash.
     : 1053 - 13: type: keyword
   : 1054 - 5679: ## host [_host]  A host is defined as a general co
     : 1055 - 15: ## host [_host]
     : 1056 - 274: A host is defined as a general computing instance.
     : 1057 - 58: **`host.architecture`** :   Operating system archi
     : 1058 - 13: type: keyword
     : 1059 - 15: example: x86_64
     : 1060 - 239: **`host.cpu.usage`** :   Percent CPU used which is
     : 1061 - 18: type: scaled_float
     : 1062 - 144: **`host.disk.read.bytes`** :   The total number of
     : 1063 - 10: type: long
     : 1064 - 148: **`host.disk.write.bytes`** :   The total number o
     : 1065 - 10: type: long
     : 1066 - 232: **`host.domain`** :   Name of the domain of which 
     : 1067 - 13: type: keyword
     : 1068 - 16: example: CONTOSO
     : 1069 - 39: **`host.geo.city_name`** :   City name.
     : 1070 - 13: type: keyword
     : 1071 - 17: example: Montreal
     : 1072 - 80: **`host.geo.continent_code`** :   Two-letter code 
     : 1073 - 13: type: keyword
     : 1074 - 11: example: NA
     : 1075 - 56: **`host.geo.continent_name`** :   Name of the cont
     : 1076 - 13: type: keyword
     : 1077 - 22: example: North America
     : 1078 - 53: **`host.geo.country_iso_code`** :   Country ISO co
     : 1079 - 13: type: keyword
     : 1080 - 11: example: CA
     : 1081 - 45: **`host.geo.country_name`** :   Country name.
     : 1082 - 13: type: keyword
     : 1083 - 15: example: Canada
     : 1084 - 51: **`host.geo.location`** :   Longitude and latitude
     : 1085 - 15: type: geo_point
     : 1086 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 1087 - 267: **`host.geo.name`** :   User-defined description o
     : 1088 - 13: type: keyword
     : 1089 - 18: example: boston-dc
     : 1090 - 196: **`host.geo.postal_code`** :   Postal code associa
     : 1091 - 13: type: keyword
     : 1092 - 14: example: 94040
     : 1093 - 51: **`host.geo.region_iso_code`** :   Region ISO code
     : 1094 - 13: type: keyword
     : 1095 - 14: example: CA-QC
     : 1096 - 43: **`host.geo.region_name`** :   Region name.
     : 1097 - 13: type: keyword
     : 1098 - 15: example: Quebec
     : 1099 - 87: **`host.geo.timezone`** :   The time zone of the l
     : 1100 - 13: type: keyword
     : 1101 - 39: example: America/Argentina/Buenos_Aires
     : 1102 - 123: **`host.hostname`** :   Hostname of the host. It n
     : 1103 - 13: type: keyword
     : 1104 - 163: **`host.id`** :   Unique host id. As hostname is n
     : 1105 - 13: type: keyword
     : 1106 - 36: **`host.ip`** :   Host ip addresses.
     : 1107 - 8: type: ip
     : 1108 - 271: **`host.mac`** :   Host MAC addresses. The notatio
     : 1109 - 13: type: keyword
     : 1110 - 51: example: ["00-00-5E-00-53-23", "00-00-5E-00-53-24"
     : 1111 - 198: **`host.name`** :   Name of the host. It can conta
     : 1112 - 13: type: keyword
     : 1113 - 144: **`host.network.egress.bytes`** :   The number of 
     : 1114 - 10: type: long
     : 1115 - 148: **`host.network.egress.packets`** :   The number o
     : 1116 - 10: type: long
     : 1117 - 145: **`host.network.ingress.bytes`** :   The number of
     : 1118 - 10: type: long
     : 1119 - 149: **`host.network.ingress.packets`** :   The number 
     : 1120 - 10: type: long
     : 1121 - 78: **`host.os.family`** :   OS family (such as redhat
     : 1122 - 13: type: keyword
     : 1123 - 15: example: debian
     : 1124 - 81: **`host.os.full`** :   Operating system name, incl
     : 1125 - 13: type: keyword
     : 1126 - 22: example: Mac OS Mojave
     : 1127 - 49: **`host.os.full.text`** :   type: match_only_text
     : 1128 - 73: **`host.os.kernel`** :   Operating system kernel v
     : 1129 - 13: type: keyword
     : 1130 - 26: example: 4.4.0-112-generic
     : 1131 - 66: **`host.os.name`** :   Operating system name, with
     : 1132 - 13: type: keyword
     : 1133 - 17: example: Mac OS X
     : 1134 - 49: **`host.os.name.text`** :   type: match_only_text
     : 1135 - 84: **`host.os.platform`** :   Operating system platfo
     : 1136 - 13: type: keyword
     : 1137 - 15: example: darwin
     : 1138 - 370: **`host.os.type`** :   Use the `os.type` field to 
     : 1139 - 13: type: keyword
     : 1140 - 14: example: macos
     : 1141 - 67: **`host.os.version`** :   Operating system version
     : 1142 - 13: type: keyword
     : 1143 - 16: example: 10.14.1
     : 1144 - 203: **`host.type`** :   Type of host. For Cloud provid
     : 1145 - 13: type: keyword
     : 1146 - 51: **`host.uptime`** :   Seconds the host has been up
     : 1147 - 10: type: long
     : 1148 - 13: example: 1325
   : 1149 - 2441: ## http [_http]  Fields related to HTTP activity. 
     : 1150 - 15: ## http [_http]
     : 1151 - 89: Fields related to HTTP activity. Use the `url` fie
     : 1152 - 68: **`http.request.body.bytes`** :   Size in bytes of
     : 1153 - 10: type: long
     : 1154 - 12: example: 887
     : 1155 - 13: format: bytes
     : 1156 - 63: **`http.request.body.content`** :   The full HTTP 
     : 1157 - 14: type: wildcard
     : 1158 - 20: example: Hello world
     : 1159 - 62: **`http.request.body.content.text`** :   type: mat
     : 1160 - 83: **`http.request.bytes`** :   Total size in bytes o
     : 1161 - 10: type: long
     : 1162 - 13: example: 1437
     : 1163 - 13: format: bytes
     : 1164 - 232: **`http.request.id`** :   A unique identifier for 
     : 1165 - 13: type: keyword
     : 1166 - 45: example: 123e4567-e89b-12d3-a456-426614174000
     : 1167 - 197: **`http.request.method`** :   HTTP request method.
     : 1168 - 13: type: keyword
     : 1169 - 13: example: POST
     : 1170 - 318: **`http.request.mime_type`** :   Mime type of the 
     : 1171 - 13: type: keyword
     : 1172 - 18: example: image/gif
     : 1173 - 63: **`http.request.referrer`** :   Referrer for this 
     : 1174 - 13: type: keyword
     : 1175 - 34: example: https://blog.example.com/
     : 1176 - 70: **`http.response.body.bytes`** :   Size in bytes o
     : 1177 - 10: type: long
     : 1178 - 12: example: 887
     : 1179 - 13: format: bytes
     : 1180 - 65: **`http.response.body.content`** :   The full HTTP
     : 1181 - 14: type: wildcard
     : 1182 - 20: example: Hello world
     : 1183 - 63: **`http.response.body.content.text`** :   type: ma
     : 1184 - 85: **`http.response.bytes`** :   Total size in bytes 
     : 1185 - 10: type: long
     : 1186 - 13: example: 1437
     : 1187 - 13: format: bytes
     : 1188 - 312: **`http.response.mime_type`** :   Mime type of the
     : 1189 - 13: type: keyword
     : 1190 - 18: example: image/gif
     : 1191 - 62: **`http.response.status_code`** :   HTTP response 
     : 1192 - 10: type: long
     : 1193 - 12: example: 404
     : 1194 - 14: format: string
     : 1195 - 36: **`http.version`** :   HTTP version.
     : 1196 - 13: type: keyword
     : 1197 - 12: example: 1.1
   : 1198 - 803: ## interface [_interface]  The interface fields ar
     : 1199 - 25: ## interface [_interface]
     : 1200 - 350: The interface fields are used to record ingress an
     : 1201 - 170: **`interface.alias`** :   Interface alias as repor
     : 1202 - 13: type: keyword
     : 1203 - 16: example: outside
     : 1204 - 93: **`interface.id`** :   Interface ID as reported by
     : 1205 - 13: type: keyword
     : 1206 - 11: example: 10
     : 1207 - 66: **`interface.name`** :   Interface name as reporte
     : 1208 - 13: type: keyword
     : 1209 - 13: example: eth0
   : 1210 - 3382: ## log [_log]  Details about the event’s logging m
     : 1211 - 13: ## log [_log]
     : 1212 - 379: Details about the event’s logging mechanism or log
     : 1213 - 220: **`log.file.path`** :   Full path to the log file 
     : 1214 - 13: type: keyword
     : 1215 - 31: example: /var/log/fun-times.log
     : 1216 - 336: **`log.level`** :   Original log level of the log 
     : 1217 - 13: type: keyword
     : 1218 - 14: example: error
     : 1219 - 159: **`log.logger`** :   The name of the logger inside
     : 1220 - 13: type: keyword
     : 1221 - 46: example: org.elasticsearch.bootstrap.Bootstrap
     : 1222 - 117: **`log.origin.file.line`** :   The line number of 
     : 1223 - 10: type: long
     : 1224 - 11: example: 42
     : 1225 - 232: **`log.origin.file.name`** :   The name of the fil
     : 1226 - 13: type: keyword
     : 1227 - 23: example: Bootstrap.java
     : 1228 - 96: **`log.origin.function`** :   The name of the func
     : 1229 - 13: type: keyword
     : 1230 - 13: example: init
     : 1231 - 125: **`log.syslog`** :   The Syslog metadata of the ev
     : 1232 - 12: type: object
     : 1233 - 177: **`log.syslog.facility.code`** :   The Syslog nume
     : 1234 - 10: type: long
     : 1235 - 11: example: 23
     : 1236 - 14: format: string
     : 1237 - 97: **`log.syslog.facility.name`** :   The Syslog text
     : 1238 - 13: type: keyword
     : 1239 - 15: example: local7
     : 1240 - 227: **`log.syslog.priority`** :   Syslog numeric prior
     : 1241 - 10: type: long
     : 1242 - 12: example: 135
     : 1243 - 14: format: string
     : 1244 - 389: **`log.syslog.severity.code`** :   The Syslog nume
     : 1245 - 10: type: long
     : 1246 - 10: example: 3
     : 1247 - 368: **`log.syslog.severity.name`** :   The Syslog nume
     : 1248 - 13: type: keyword
     : 1249 - 14: example: Error
   : 1250 - 4189: ## network [_network]  The network is defined as t
     : 1251 - 21: ## network [_network]
     : 1252 - 199: The network is defined as the communication path o
     : 1253 - 453: **`network.application`** :   When a specific appl
     : 1254 - 13: type: keyword
     : 1255 - 12: example: aim
     : 1256 - 150: **`network.bytes`** :   Total bytes transferred in
     : 1257 - 10: type: long
     : 1258 - 12: example: 368
     : 1259 - 13: format: bytes
     : 1260 - 242: **`network.community_id`** :   A hash of source an
     : 1261 - 13: type: keyword
     : 1262 - 39: example: 1:hO+sN4H+MG5MY/8hIrXPqc4ZQz0=
     : 1263 - 157: **`network.direction`** :   Direction of the netwo
     : 1264 - 672: When mapping events from a host-based monitoring c
     : 1265 - 13: type: keyword
     : 1266 - 16: example: inbound
     : 1267 - 87: **`network.forwarded_ip`** :   Host IP address whe
     : 1268 - 8: type: ip
     : 1269 - 18: example: 192.1.1.2
     : 1270 - 249: **`network.iana_number`** :   IANA Protocol Number
     : 1271 - 13: type: keyword
     : 1272 - 10: example: 6
     : 1273 - 341: **`network.inner`** :   Network.inner fields are a
     : 1274 - 12: type: object
     : 1275 - 68: **`network.inner.vlan.id`** :   VLAN ID as reporte
     : 1276 - 13: type: keyword
     : 1277 - 11: example: 10
     : 1278 - 81: **`network.inner.vlan.name`** :   Optional VLAN na
     : 1279 - 13: type: keyword
     : 1280 - 16: example: outside
     : 1281 - 76: **`network.name`** :   Name given by operators to 
     : 1282 - 13: type: keyword
     : 1283 - 19: example: Guest Wifi
     : 1284 - 160: **`network.packets`** :   Total packets transferre
     : 1285 - 10: type: long
     : 1286 - 11: example: 24
     : 1287 - 192: **`network.protocol`** :   In the OSI Model this w
     : 1288 - 13: type: keyword
     : 1289 - 13: example: http
     : 1290 - 204: **`network.transport`** :   Same as network.iana_n
     : 1291 - 13: type: keyword
     : 1292 - 12: example: tcp
     : 1293 - 162: **`network.type`** :   In the OSI Model this would
     : 1294 - 13: type: keyword
     : 1295 - 13: example: ipv4
     : 1296 - 62: **`network.vlan.id`** :   VLAN ID as reported by t
     : 1297 - 13: type: keyword
     : 1298 - 11: example: 10
     : 1299 - 75: **`network.vlan.name`** :   Optional VLAN name as 
     : 1300 - 13: type: keyword
     : 1301 - 16: example: outside
   : 1302 - 7234: ## observer [_observer]  An observer is defined as
     : 1303 - 23: ## observer [_observer]
     : 1304 - 770: An observer is defined as a special network, secur
     : 1305 - 267: **`observer.egress`** :   Observer.egress holds in
     : 1306 - 12: type: object
     : 1307 - 186: **`observer.egress.interface.alias`** :   Interfac
     : 1308 - 13: type: keyword
     : 1309 - 16: example: outside
     : 1310 - 109: **`observer.egress.interface.id`** :   Interface I
     : 1311 - 13: type: keyword
     : 1312 - 11: example: 10
     : 1313 - 82: **`observer.egress.interface.name`** :   Interface
     : 1314 - 13: type: keyword
     : 1315 - 13: example: eth0
     : 1316 - 70: **`observer.egress.vlan.id`** :   VLAN ID as repor
     : 1317 - 13: type: keyword
     : 1318 - 11: example: 10
     : 1319 - 83: **`observer.egress.vlan.name`** :   Optional VLAN 
     : 1320 - 13: type: keyword
     : 1321 - 16: example: outside
     : 1322 - 191: **`observer.egress.zone`** :   Network zone of out
     : 1323 - 13: type: keyword
     : 1324 - 24: example: Public_Internet
     : 1325 - 43: **`observer.geo.city_name`** :   City name.
     : 1326 - 13: type: keyword
     : 1327 - 17: example: Montreal
     : 1328 - 84: **`observer.geo.continent_code`** :   Two-letter c
     : 1329 - 13: type: keyword
     : 1330 - 11: example: NA
     : 1331 - 60: **`observer.geo.continent_name`** :   Name of the 
     : 1332 - 13: type: keyword
     : 1333 - 22: example: North America
     : 1334 - 57: **`observer.geo.country_iso_code`** :   Country IS
     : 1335 - 13: type: keyword
     : 1336 - 11: example: CA
     : 1337 - 49: **`observer.geo.country_name`** :   Country name.
     : 1338 - 13: type: keyword
     : 1339 - 15: example: Canada
     : 1340 - 55: **`observer.geo.location`** :   Longitude and lati
     : 1341 - 15: type: geo_point
     : 1342 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 1343 - 271: **`observer.geo.name`** :   User-defined descripti
     : 1344 - 13: type: keyword
     : 1345 - 18: example: boston-dc
     : 1346 - 200: **`observer.geo.postal_code`** :   Postal code ass
     : 1347 - 13: type: keyword
     : 1348 - 14: example: 94040
     : 1349 - 55: **`observer.geo.region_iso_code`** :   Region ISO 
     : 1350 - 13: type: keyword
     : 1351 - 14: example: CA-QC
     : 1352 - 47: **`observer.geo.region_name`** :   Region name.
     : 1353 - 13: type: keyword
     : 1354 - 15: example: Quebec
     : 1355 - 91: **`observer.geo.timezone`** :   The time zone of t
     : 1356 - 13: type: keyword
     : 1357 - 39: example: America/Argentina/Buenos_Aires
     : 1358 - 53: **`observer.hostname`** :   Hostname of the observ
     : 1359 - 13: type: keyword
     : 1360 - 270: **`observer.ingress`** :   Observer.ingress holds 
     : 1361 - 12: type: object
     : 1362 - 187: **`observer.ingress.interface.alias`** :   Interfa
     : 1363 - 13: type: keyword
     : 1364 - 16: example: outside
     : 1365 - 110: **`observer.ingress.interface.id`** :   Interface 
     : 1366 - 13: type: keyword
     : 1367 - 11: example: 10
     : 1368 - 83: **`observer.ingress.interface.name`** :   Interfac
     : 1369 - 13: type: keyword
     : 1370 - 13: example: eth0
     : 1371 - 71: **`observer.ingress.vlan.id`** :   VLAN ID as repo
     : 1372 - 13: type: keyword
     : 1373 - 11: example: 10
     : 1374 - 84: **`observer.ingress.vlan.name`** :   Optional VLAN
     : 1375 - 13: type: keyword
     : 1376 - 16: example: outside
     : 1377 - 188: **`observer.ingress.zone`** :   Network zone of in
     : 1378 - 13: type: keyword
     : 1379 - 12: example: DMZ
     : 1380 - 51: **`observer.ip`** :   IP addresses of the observer
     : 1381 - 8: type: ip
     : 1382 - 286: **`observer.mac`** :   MAC addresses of the observ
     : 1383 - 13: type: keyword
     : 1384 - 51: example: ["00-00-5E-00-53-23", "00-00-5E-00-53-24"
     : 1385 - 260: **`observer.name`** :   Custom name of the observe
     : 1386 - 13: type: keyword
     : 1387 - 18: example: 1_proxySG
     : 1388 - 82: **`observer.os.family`** :   OS family (such as re
     : 1389 - 13: type: keyword
     : 1390 - 15: example: debian
     : 1391 - 85: **`observer.os.full`** :   Operating system name, 
     : 1392 - 13: type: keyword
     : 1393 - 22: example: Mac OS Mojave
     : 1394 - 53: **`observer.os.full.text`** :   type: match_only_t
     : 1395 - 77: **`observer.os.kernel`** :   Operating system kern
     : 1396 - 13: type: keyword
     : 1397 - 26: example: 4.4.0-112-generic
     : 1398 - 70: **`observer.os.name`** :   Operating system name, 
     : 1399 - 13: type: keyword
     : 1400 - 17: example: Mac OS X
     : 1401 - 53: **`observer.os.name.text`** :   type: match_only_t
     : 1402 - 88: **`observer.os.platform`** :   Operating system pl
     : 1403 - 13: type: keyword
     : 1404 - 15: example: darwin
     : 1405 - 374: **`observer.os.type`** :   Use the `os.type` field
     : 1406 - 13: type: keyword
     : 1407 - 14: example: macos
     : 1408 - 71: **`observer.os.version`** :   Operating system ver
     : 1409 - 13: type: keyword
     : 1410 - 16: example: 10.14.1
     : 1411 - 60: **`observer.product`** :   The product name of the
     : 1412 - 13: type: keyword
     : 1413 - 13: example: s200
     : 1414 - 56: **`observer.serial_number`** :   Observer serial n
     : 1415 - 13: type: keyword
     : 1416 - 228: **`observer.type`** :   The type of the observer t
     : 1417 - 13: type: keyword
     : 1418 - 17: example: firewall
     : 1419 - 54: **`observer.vendor`** :   Vendor name of the obser
     : 1420 - 13: type: keyword
     : 1421 - 17: example: Symantec
     : 1422 - 44: **`observer.version`** :   Observer version.
     : 1423 - 13: type: keyword
   : 1424 - 1102: ## orchestrator [_orchestrator]  Fields that descr
     : 1425 - 31: ## orchestrator [_orchestrator]
     : 1426 - 84: Fields that describe the resources which container
     : 1427 - 81: **`orchestrator.api_version`** :   API version bei
     : 1428 - 13: type: keyword
     : 1429 - 16: example: v1beta1
     : 1430 - 56: **`orchestrator.cluster.name`** :   Name of the cl
     : 1431 - 13: type: keyword
     : 1432 - 77: **`orchestrator.cluster.url`** :   URL of the API 
     : 1433 - 13: type: keyword
     : 1434 - 66: **`orchestrator.cluster.version`** :   The version
     : 1435 - 13: type: keyword
     : 1436 - 79: **`orchestrator.namespace`** :   Namespace in whic
     : 1437 - 13: type: keyword
     : 1438 - 20: example: kube-system
     : 1439 - 110: **`orchestrator.organization`** :   Organization a
     : 1440 - 13: type: keyword
     : 1441 - 16: example: elastic
     : 1442 - 75: **`orchestrator.resource.name`** :   Name of the r
     : 1443 - 13: type: keyword
     : 1444 - 23: example: test-pod-cdcws
     : 1445 - 71: **`orchestrator.resource.type`** :   Type of resou
     : 1446 - 13: type: keyword
     : 1447 - 16: example: service
     : 1448 - 95: **`orchestrator.type`** :   Orchestrator cluster t
     : 1449 - 13: type: keyword
     : 1450 - 19: example: kubernetes
   : 1451 - 441: ## organization [_organization]  The organization 
     : 1452 - 31: ## organization [_organization]
     : 1453 - 207: The organization fields enrich data with informati
     : 1454 - 65: **`organization.id`** :   Unique identifier for th
     : 1455 - 13: type: keyword
     : 1456 - 46: **`organization.name`** :   Organization name.
     : 1457 - 13: type: keyword
     : 1458 - 54: **`organization.name.text`** :   type: match_only_
   : 1459 - 1208: ## os [_os]  The OS fields contain information abo
     : 1460 - 11: ## os [_os]
     : 1461 - 61: The OS fields contain information about the operat
     : 1462 - 73: **`os.family`** :   OS family (such as redhat, deb
     : 1463 - 13: type: keyword
     : 1464 - 15: example: debian
     : 1465 - 76: **`os.full`** :   Operating system name, including
     : 1466 - 13: type: keyword
     : 1467 - 22: example: Mac OS Mojave
     : 1468 - 44: **`os.full.text`** :   type: match_only_text
     : 1469 - 68: **`os.kernel`** :   Operating system kernel versio
     : 1470 - 13: type: keyword
     : 1471 - 26: example: 4.4.0-112-generic
     : 1472 - 61: **`os.name`** :   Operating system name, without t
     : 1473 - 13: type: keyword
     : 1474 - 17: example: Mac OS X
     : 1475 - 44: **`os.name.text`** :   type: match_only_text
     : 1476 - 79: **`os.platform`** :   Operating system platform (s
     : 1477 - 13: type: keyword
     : 1478 - 15: example: darwin
     : 1479 - 365: **`os.type`** :   Use the `os.type` field to categ
     : 1480 - 13: type: keyword
     : 1481 - 14: example: macos
     : 1482 - 62: **`os.version`** :   Operating system version as a
     : 1483 - 13: type: keyword
     : 1484 - 16: example: 10.14.1
   : 1485 - 1985: ## package [_package]  These fields contain inform
     : 1486 - 21: ## package [_package]
     : 1487 - 214: These fields contain information about an installe
     : 1488 - 52: **`package.architecture`** :   Package architectur
     : 1489 - 13: type: keyword
     : 1490 - 15: example: x86_64
     : 1491 - 162: **`package.build_version`** :   Additional informa
     : 1492 - 13: type: keyword
     : 1493 - 49: example: 36f4f7e89dd61b0988b12ee000b98966867710cd
     : 1494 - 78: **`package.checksum`** :   Checksum of the install
     : 1495 - 13: type: keyword
     : 1496 - 41: example: 68b329da9893e34099c7d8ad5cb9c940
     : 1497 - 57: **`package.description`** :   Description of the p
     : 1498 - 13: type: keyword
     : 1499 - 86: example: Open source programming language to build
     : 1500 - 98: **`package.install_scope`** :   Indicating how the
     : 1501 - 13: type: keyword
     : 1502 - 15: example: global
     : 1503 - 60: **`package.installed`** :   Time when package was 
     : 1504 - 10: type: date
     : 1505 - 187: **`package.license`** :   License under which the 
     : 1506 - 13: type: keyword
     : 1507 - 27: example: Apache License 2.0
     : 1508 - 35: **`package.name`** :   Package name
     : 1509 - 13: type: keyword
     : 1510 - 11: example: go
     : 1511 - 59: **`package.path`** :   Path where the package is i
     : 1512 - 13: type: keyword
     : 1513 - 37: example: /usr/local/Cellar/go/1.12.9/
     : 1514 - 101: **`package.reference`** :   Home page or reference
     : 1515 - 13: type: keyword
     : 1516 - 27: example: https://golang.org
     : 1517 - 45: **`package.size`** :   Package size in bytes.
     : 1518 - 10: type: long
     : 1519 - 14: example: 62231
     : 1520 - 14: format: string
     : 1521 - 169: **`package.type`** :   Type of package. This shoul
     : 1522 - 13: type: keyword
     : 1523 - 12: example: rpm
     : 1524 - 41: **`package.version`** :   Package version
     : 1525 - 13: type: keyword
     : 1526 - 15: example: 1.12.9
   : 1527 - 1221: ## pe [_pe]  These fields contain Windows Portable
     : 1528 - 11: ## pe [_pe]
     : 1529 - 63: These fields contain Windows Portable Executable (
     : 1530 - 63: **`pe.architecture`** :   CPU architecture target 
     : 1531 - 13: type: keyword
     : 1532 - 12: example: x64
     : 1533 - 81: **`pe.company`** :   Internal company name of the 
     : 1534 - 13: type: keyword
     : 1535 - 30: example: Microsoft Corporation
     : 1536 - 84: **`pe.description`** :   Internal description of t
     : 1537 - 13: type: keyword
     : 1538 - 14: example: Paint
     : 1539 - 81: **`pe.file_version`** :   Internal version of the 
     : 1540 - 13: type: keyword
     : 1541 - 23: example: 6.3.9600.17415
     : 1542 - 353: **`pe.imphash`** :   A hash of the imports in a PE
     : 1543 - 13: type: keyword
     : 1544 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 1545 - 84: **`pe.original_file_name`** :   Internal name of t
     : 1546 - 13: type: keyword
     : 1547 - 20: example: MSPAINT.EXE
     : 1548 - 81: **`pe.product`** :   Internal product name of the 
     : 1549 - 13: type: keyword
     : 1550 - 45: example: Microsoft® Windows® Operating System
   : 1551 - 19483: ## process [_process_2]  These fields contain info
     : 1552 - 23: ## process [_process_2]
     : 1553 - 251: These fields contain information about a process. 
     : 1554 - 151: **`process.args`** :   Array of process arguments,
     : 1555 - 13: type: keyword
     : 1556 - 52: example: ["/usr/bin/ssh", "-l", "user", "10.0.0.16
     : 1557 - 246: **`process.args_count`** :   Length of the process
     : 1558 - 10: type: long
     : 1559 - 10: example: 4
     : 1560 - 230: **`process.code_signature.digest_algorithm`** :   
     : 1561 - 13: type: keyword
     : 1562 - 15: example: sha256
     : 1563 - 85: **`process.code_signature.exists`** :   Boolean to
     : 1564 - 13: type: boolean
     : 1565 - 13: example: true
     : 1566 - 201: **`process.code_signature.signing_id`** :   The id
     : 1567 - 13: type: keyword
     : 1568 - 28: example: com.apple.xpc.proxy
     : 1569 - 264: **`process.code_signature.status`** :   Additional
     : 1570 - 13: type: keyword
     : 1571 - 29: example: ERROR_UNTRUSTED_ROOT
     : 1572 - 77: **`process.code_signature.subject_name`** :   Subj
     : 1573 - 13: type: keyword
     : 1574 - 30: example: Microsoft Corporation
     : 1575 - 194: **`process.code_signature.team_id`** :   The team 
     : 1576 - 13: type: keyword
     : 1577 - 19: example: EQHXZ8M8AV
     : 1578 - 106: **`process.code_signature.timestamp`** :   Date an
     : 1579 - 10: type: date
     : 1580 - 29: example: 2021-01-01T12:10:30Z
     : 1581 - 237: **`process.code_signature.trusted`** :   Stores th
     : 1582 - 13: type: boolean
     : 1583 - 13: example: true
     : 1584 - 172: **`process.code_signature.valid`** :   Boolean to 
     : 1585 - 13: type: boolean
     : 1586 - 13: example: true
     : 1587 - 205: **`process.command_line`** :   Full command line t
     : 1588 - 14: type: wildcard
     : 1589 - 39: example: /usr/bin/ssh -l user 10.0.0.16
     : 1590 - 57: **`process.command_line.text`** :   type: match_on
     : 1591 - 72: **`process.elf.architecture`** :   Machine archite
     : 1592 - 13: type: keyword
     : 1593 - 15: example: x86-64
     : 1594 - 59: **`process.elf.byte_order`** :   Byte sequence of 
     : 1595 - 13: type: keyword
     : 1596 - 22: example: Little Endian
     : 1597 - 56: **`process.elf.cpu_type`** :   CPU type of the ELF
     : 1598 - 13: type: keyword
     : 1599 - 14: example: Intel
     : 1600 - 168: **`process.elf.creation_date`** :   Extracted when
     : 1601 - 10: type: date
     : 1602 - 71: **`process.elf.exports`** :   List of exported ele
     : 1603 - 15: type: flattened
     : 1604 - 95: **`process.elf.header.abi_version`** :   Version o
     : 1605 - 13: type: keyword
     : 1606 - 64: **`process.elf.header.class`** :   Header class of
     : 1607 - 13: type: keyword
     : 1608 - 63: **`process.elf.header.data`** :   Data table of th
     : 1609 - 13: type: keyword
     : 1610 - 74: **`process.elf.header.entrypoint`** :   Header ent
     : 1611 - 10: type: long
     : 1612 - 14: format: string
     : 1613 - 73: **`process.elf.header.object_version`** :   "0x1" 
     : 1614 - 13: type: keyword
     : 1615 - 87: **`process.elf.header.os_abi`** :   Application Bi
     : 1616 - 13: type: keyword
     : 1617 - 62: **`process.elf.header.type`** :   Header type of t
     : 1618 - 13: type: keyword
     : 1619 - 63: **`process.elf.header.version`** :   Version of th
     : 1620 - 13: type: keyword
     : 1621 - 71: **`process.elf.imports`** :   List of imported ele
     : 1622 - 15: type: flattened
     : 1623 - 199: **`process.elf.sections`** :   An array containing
     : 1624 - 12: type: nested
     : 1625 - 87: **`process.elf.sections.chi2`** :   Chi-square pro
     : 1626 - 10: type: long
     : 1627 - 14: format: number
     : 1628 - 84: **`process.elf.sections.entropy`** :   Shannon ent
     : 1629 - 10: type: long
     : 1630 - 14: format: number
     : 1631 - 60: **`process.elf.sections.flags`** :   ELF Section L
     : 1632 - 13: type: keyword
     : 1633 - 58: **`process.elf.sections.name`** :   ELF Section Li
     : 1634 - 13: type: keyword
     : 1635 - 71: **`process.elf.sections.physical_offset`** :   ELF
     : 1636 - 13: type: keyword
     : 1637 - 76: **`process.elf.sections.physical_size`** :   ELF S
     : 1638 - 10: type: long
     : 1639 - 13: format: bytes
     : 1640 - 58: **`process.elf.sections.type`** :   ELF Section Li
     : 1641 - 13: type: keyword
     : 1642 - 80: **`process.elf.sections.virtual_address`** :   ELF
     : 1643 - 10: type: long
     : 1644 - 14: format: string
     : 1645 - 74: **`process.elf.sections.virtual_size`** :   ELF Se
     : 1646 - 10: type: long
     : 1647 - 14: format: string
     : 1648 - 199: **`process.elf.segments`** :   An array containing
     : 1649 - 12: type: nested
     : 1650 - 68: **`process.elf.segments.sections`** :   ELF object
     : 1651 - 13: type: keyword
     : 1652 - 60: **`process.elf.segments.type`** :   ELF object seg
     : 1653 - 13: type: keyword
     : 1654 - 88: **`process.elf.shared_libraries`** :   List of sha
     : 1655 - 13: type: keyword
     : 1656 - 65: **`process.elf.telfhash`** :   telfhash symbol has
     : 1657 - 13: type: keyword
     : 1658 - 49: **`process.end`** :   The time the process ended.
     : 1659 - 10: type: date
     : 1660 - 33: example: 2016-05-23T08:05:34.853Z
     : 1661 - 454: **`process.entity_id`** :   Unique identifier for 
     : 1662 - 13: type: keyword
     : 1663 - 24: example: c2c455d9f99375d
     : 1664 - 69: **`process.executable`** :   Absolute path to the 
     : 1665 - 13: type: keyword
     : 1666 - 21: example: /usr/bin/ssh
     : 1667 - 55: **`process.executable.text`** :   type: match_only
     : 1668 - 177: **`process.exit_code`** :   The exit code of the p
     : 1669 - 10: type: long
     : 1670 - 12: example: 137
     : 1671 - 36: **`process.hash.md5`** :   MD5 hash.
     : 1672 - 13: type: keyword
     : 1673 - 38: **`process.hash.sha1`** :   SHA1 hash.
     : 1674 - 13: type: keyword
     : 1675 - 42: **`process.hash.sha256`** :   SHA256 hash.
     : 1676 - 13: type: keyword
     : 1677 - 42: **`process.hash.sha512`** :   SHA512 hash.
     : 1678 - 13: type: keyword
     : 1679 - 42: **`process.hash.ssdeep`** :   SSDEEP hash.
     : 1680 - 13: type: keyword
     : 1681 - 78: **`process.name`** :   Process name. Sometimes cal
     : 1682 - 13: type: keyword
     : 1683 - 12: example: ssh
     : 1684 - 49: **`process.name.text`** :   type: match_only_text
     : 1685 - 158: **`process.parent.args`** :   Array of process arg
     : 1686 - 13: type: keyword
     : 1687 - 52: example: ["/usr/bin/ssh", "-l", "user", "10.0.0.16
     : 1688 - 253: **`process.parent.args_count`** :   Length of the 
     : 1689 - 10: type: long
     : 1690 - 10: example: 4
     : 1691 - 237: **`process.parent.code_signature.digest_algorithm`
     : 1692 - 13: type: keyword
     : 1693 - 15: example: sha256
     : 1694 - 92: **`process.parent.code_signature.exists`** :   Boo
     : 1695 - 13: type: boolean
     : 1696 - 13: example: true
     : 1697 - 208: **`process.parent.code_signature.signing_id`** :  
     : 1698 - 13: type: keyword
     : 1699 - 28: example: com.apple.xpc.proxy
     : 1700 - 271: **`process.parent.code_signature.status`** :   Add
     : 1701 - 13: type: keyword
     : 1702 - 29: example: ERROR_UNTRUSTED_ROOT
     : 1703 - 84: **`process.parent.code_signature.subject_name`** :
     : 1704 - 13: type: keyword
     : 1705 - 30: example: Microsoft Corporation
     : 1706 - 201: **`process.parent.code_signature.team_id`** :   Th
     : 1707 - 13: type: keyword
     : 1708 - 19: example: EQHXZ8M8AV
     : 1709 - 113: **`process.parent.code_signature.timestamp`** :   
     : 1710 - 10: type: date
     : 1711 - 29: example: 2021-01-01T12:10:30Z
     : 1712 - 244: **`process.parent.code_signature.trusted`** :   St
     : 1713 - 13: type: boolean
     : 1714 - 13: example: true
     : 1715 - 179: **`process.parent.code_signature.valid`** :   Bool
     : 1716 - 13: type: boolean
     : 1717 - 13: example: true
     : 1718 - 212: **`process.parent.command_line`** :   Full command
     : 1719 - 14: type: wildcard
     : 1720 - 39: example: /usr/bin/ssh -l user 10.0.0.16
     : 1721 - 64: **`process.parent.command_line.text`** :   type: m
     : 1722 - 79: **`process.parent.elf.architecture`** :   Machine 
     : 1723 - 13: type: keyword
     : 1724 - 15: example: x86-64
     : 1725 - 66: **`process.parent.elf.byte_order`** :   Byte seque
     : 1726 - 13: type: keyword
     : 1727 - 22: example: Little Endian
     : 1728 - 63: **`process.parent.elf.cpu_type`** :   CPU type of 
     : 1729 - 13: type: keyword
     : 1730 - 14: example: Intel
     : 1731 - 175: **`process.parent.elf.creation_date`** :   Extract
     : 1732 - 10: type: date
     : 1733 - 78: **`process.parent.elf.exports`** :   List of expor
     : 1734 - 15: type: flattened
     : 1735 - 102: **`process.parent.elf.header.abi_version`** :   Ve
     : 1736 - 13: type: keyword
     : 1737 - 71: **`process.parent.elf.header.class`** :   Header c
     : 1738 - 13: type: keyword
     : 1739 - 70: **`process.parent.elf.header.data`** :   Data tabl
     : 1740 - 13: type: keyword
     : 1741 - 81: **`process.parent.elf.header.entrypoint`** :   Hea
     : 1742 - 10: type: long
     : 1743 - 14: format: string
     : 1744 - 80: **`process.parent.elf.header.object_version`** :  
     : 1745 - 13: type: keyword
     : 1746 - 94: **`process.parent.elf.header.os_abi`** :   Applica
     : 1747 - 13: type: keyword
     : 1748 - 69: **`process.parent.elf.header.type`** :   Header ty
     : 1749 - 13: type: keyword
     : 1750 - 70: **`process.parent.elf.header.version`** :   Versio
     : 1751 - 13: type: keyword
     : 1752 - 78: **`process.parent.elf.imports`** :   List of impor
     : 1753 - 15: type: flattened
     : 1754 - 206: **`process.parent.elf.sections`** :   An array con
     : 1755 - 12: type: nested
     : 1756 - 94: **`process.parent.elf.sections.chi2`** :   Chi-squ
     : 1757 - 10: type: long
     : 1758 - 14: format: number
     : 1759 - 91: **`process.parent.elf.sections.entropy`** :   Shan
     : 1760 - 10: type: long
     : 1761 - 14: format: number
     : 1762 - 67: **`process.parent.elf.sections.flags`** :   ELF Se
     : 1763 - 13: type: keyword
     : 1764 - 65: **`process.parent.elf.sections.name`** :   ELF Sec
     : 1765 - 13: type: keyword
     : 1766 - 78: **`process.parent.elf.sections.physical_offset`** 
     : 1767 - 13: type: keyword
     : 1768 - 83: **`process.parent.elf.sections.physical_size`** : 
     : 1769 - 10: type: long
     : 1770 - 13: format: bytes
     : 1771 - 65: **`process.parent.elf.sections.type`** :   ELF Sec
     : 1772 - 13: type: keyword
     : 1773 - 87: **`process.parent.elf.sections.virtual_address`** 
     : 1774 - 10: type: long
     : 1775 - 14: format: string
     : 1776 - 81: **`process.parent.elf.sections.virtual_size`** :  
     : 1777 - 10: type: long
     : 1778 - 14: format: string
     : 1779 - 206: **`process.parent.elf.segments`** :   An array con
     : 1780 - 12: type: nested
     : 1781 - 75: **`process.parent.elf.segments.sections`** :   ELF
     : 1782 - 13: type: keyword
     : 1783 - 67: **`process.parent.elf.segments.type`** :   ELF obj
     : 1784 - 13: type: keyword
     : 1785 - 95: **`process.parent.elf.shared_libraries`** :   List
     : 1786 - 13: type: keyword
     : 1787 - 72: **`process.parent.elf.telfhash`** :   telfhash sym
     : 1788 - 13: type: keyword
     : 1789 - 56: **`process.parent.end`** :   The time the process 
     : 1790 - 10: type: date
     : 1791 - 33: example: 2016-05-23T08:05:34.853Z
     : 1792 - 461: **`process.parent.entity_id`** :   Unique identifi
     : 1793 - 13: type: keyword
     : 1794 - 24: example: c2c455d9f99375d
     : 1795 - 76: **`process.parent.executable`** :   Absolute path 
     : 1796 - 13: type: keyword
     : 1797 - 21: example: /usr/bin/ssh
     : 1798 - 62: **`process.parent.executable.text`** :   type: mat
     : 1799 - 184: **`process.parent.exit_code`** :   The exit code o
     : 1800 - 10: type: long
     : 1801 - 12: example: 137
     : 1802 - 43: **`process.parent.hash.md5`** :   MD5 hash.
     : 1803 - 13: type: keyword
     : 1804 - 45: **`process.parent.hash.sha1`** :   SHA1 hash.
     : 1805 - 13: type: keyword
     : 1806 - 49: **`process.parent.hash.sha256`** :   SHA256 hash.
     : 1807 - 13: type: keyword
     : 1808 - 49: **`process.parent.hash.sha512`** :   SHA512 hash.
     : 1809 - 13: type: keyword
     : 1810 - 49: **`process.parent.hash.ssdeep`** :   SSDEEP hash.
     : 1811 - 13: type: keyword
     : 1812 - 85: **`process.parent.name`** :   Process name. Someti
     : 1813 - 13: type: keyword
     : 1814 - 12: example: ssh
     : 1815 - 56: **`process.parent.name.text`** :   type: match_onl
     : 1816 - 78: **`process.parent.pe.architecture`** :   CPU archi
     : 1817 - 13: type: keyword
     : 1818 - 12: example: x64
     : 1819 - 96: **`process.parent.pe.company`** :   Internal compa
     : 1820 - 13: type: keyword
     : 1821 - 30: example: Microsoft Corporation
     : 1822 - 99: **`process.parent.pe.description`** :   Internal d
     : 1823 - 13: type: keyword
     : 1824 - 14: example: Paint
     : 1825 - 96: **`process.parent.pe.file_version`** :   Internal 
     : 1826 - 13: type: keyword
     : 1827 - 23: example: 6.3.9600.17415
     : 1828 - 368: **`process.parent.pe.imphash`** :   A hash of the 
     : 1829 - 13: type: keyword
     : 1830 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 1831 - 99: **`process.parent.pe.original_file_name`** :   Int
     : 1832 - 13: type: keyword
     : 1833 - 20: example: MSPAINT.EXE
     : 1834 - 96: **`process.parent.pe.product`** :   Internal produ
     : 1835 - 13: type: keyword
     : 1836 - 45: example: Microsoft® Windows® Operating System
     : 1837 - 90: **`process.parent.pgid`** :   Identifier of the gr
     : 1838 - 10: type: long
     : 1839 - 14: format: string
     : 1840 - 40: **`process.parent.pid`** :   Process id.
     : 1841 - 10: type: long
     : 1842 - 13: example: 4242
     : 1843 - 14: format: string
     : 1844 - 60: **`process.parent.start`** :   The time the proces
     : 1845 - 10: type: date
     : 1846 - 33: example: 2016-05-23T08:05:34.853Z
     : 1847 - 45: **`process.parent.thread.id`** :   Thread ID.
     : 1848 - 10: type: long
     : 1849 - 13: example: 4242
     : 1850 - 14: format: string
     : 1851 - 49: **`process.parent.thread.name`** :   Thread name.
     : 1852 - 13: type: keyword
     : 1853 - 17: example: thread-0
     : 1854 - 194: **`process.parent.title`** :   Process title. The 
     : 1855 - 13: type: keyword
     : 1856 - 57: **`process.parent.title.text`** :   type: match_on
     : 1857 - 64: **`process.parent.uptime`** :   Seconds the proces
     : 1858 - 10: type: long
     : 1859 - 13: example: 1325
     : 1860 - 80: **`process.parent.working_directory`** :   The wor
     : 1861 - 13: type: keyword
     : 1862 - 20: example: /home/alice
     : 1863 - 69: **`process.parent.working_directory.text`** :   ty
     : 1864 - 71: **`process.pe.architecture`** :   CPU architecture
     : 1865 - 13: type: keyword
     : 1866 - 12: example: x64
     : 1867 - 89: **`process.pe.company`** :   Internal company name
     : 1868 - 13: type: keyword
     : 1869 - 30: example: Microsoft Corporation
     : 1870 - 92: **`process.pe.description`** :   Internal descript
     : 1871 - 13: type: keyword
     : 1872 - 14: example: Paint
     : 1873 - 89: **`process.pe.file_version`** :   Internal version
     : 1874 - 13: type: keyword
     : 1875 - 23: example: 6.3.9600.17415
     : 1876 - 361: **`process.pe.imphash`** :   A hash of the imports
     : 1877 - 13: type: keyword
     : 1878 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 1879 - 92: **`process.pe.original_file_name`** :   Internal n
     : 1880 - 13: type: keyword
     : 1881 - 20: example: MSPAINT.EXE
     : 1882 - 89: **`process.pe.product`** :   Internal product name
     : 1883 - 13: type: keyword
     : 1884 - 45: example: Microsoft® Windows® Operating System
     : 1885 - 83: **`process.pgid`** :   Identifier of the group of 
     : 1886 - 10: type: long
     : 1887 - 14: format: string
     : 1888 - 33: **`process.pid`** :   Process id.
     : 1889 - 10: type: long
     : 1890 - 13: example: 4242
     : 1891 - 14: format: string
     : 1892 - 53: **`process.start`** :   The time the process start
     : 1893 - 10: type: date
     : 1894 - 33: example: 2016-05-23T08:05:34.853Z
     : 1895 - 38: **`process.thread.id`** :   Thread ID.
     : 1896 - 10: type: long
     : 1897 - 13: example: 4242
     : 1898 - 14: format: string
     : 1899 - 42: **`process.thread.name`** :   Thread name.
     : 1900 - 13: type: keyword
     : 1901 - 17: example: thread-0
     : 1902 - 187: **`process.title`** :   Process title. The proctit
     : 1903 - 13: type: keyword
     : 1904 - 50: **`process.title.text`** :   type: match_only_text
     : 1905 - 57: **`process.uptime`** :   Seconds the process has b
     : 1906 - 10: type: long
     : 1907 - 13: example: 1325
     : 1908 - 73: **`process.working_directory`** :   The working di
     : 1909 - 13: type: keyword
     : 1910 - 20: example: /home/alice
     : 1911 - 62: **`process.working_directory.text`** :   type: mat
   : 1912 - 1558: ## registry [_registry]  Fields related to Windows
     : 1913 - 23: ## registry [_registry]
     : 1914 - 46: Fields related to Windows Registry operations.
     : 1915 - 306: **`registry.data.bytes`** :   Original bytes writt
     : 1916 - 13: type: keyword
     : 1917 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
     : 1918 - 430: **`registry.data.strings`** :   Content when writi
     : 1919 - 14: type: wildcard
     : 1920 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
     : 1921 - 73: **`registry.data.type`** :   Standard registry typ
     : 1922 - 13: type: keyword
     : 1923 - 15: example: REG_SZ
     : 1924 - 54: **`registry.hive`** :   Abbreviated name for the h
     : 1925 - 13: type: keyword
     : 1926 - 13: example: HKLM
     : 1927 - 50: **`registry.key`** :   Hive-relative path of keys.
     : 1928 - 13: type: keyword
     : 1929 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
     : 1930 - 64: **`registry.path`** :   Full path, including hive,
     : 1931 - 13: type: keyword
     : 1932 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
     : 1933 - 51: **`registry.value`** :   Name of the value written
     : 1934 - 13: type: keyword
     : 1935 - 17: example: Debugger
   : 1936 - 1158: ## related [_related]  This field set is meant to 
     : 1937 - 21: ## related [_related]
     : 1938 - 541: This field set is meant to facilitate pivoting aro
     : 1939 - 227: **`related.hash`** :   All the hashes seen on your
     : 1940 - 13: type: keyword
     : 1941 - 163: **`related.hosts`** :   All hostnames or other hos
     : 1942 - 13: type: keyword
     : 1943 - 55: **`related.ip`** :   All of the IPs seen on your e
     : 1944 - 8: type: ip
     : 1945 - 86: **`related.user`** :   All the user names or other
     : 1946 - 13: type: keyword
   : 1947 - 2170: ## rule [_rule]  Rule fields are used to capture t
     : 1948 - 15: ## rule [_rule]
     : 1949 - 365: Rule fields are used to capture the specifics of a
     : 1950 - 129: **`rule.author`** :   Name, organization, or pseud
     : 1951 - 13: type: keyword
     : 1952 - 22: example: ["Star-Lord"]
     : 1953 - 117: **`rule.category`** :   A categorization value key
     : 1954 - 13: type: keyword
     : 1955 - 35: example: Attempted Information Leak
     : 1956 - 76: **`rule.description`** :   The description of the 
     : 1957 - 13: type: keyword
     : 1958 - 64: example: Block requests to public DNS over HTTPS /
     : 1959 - 142: **`rule.id`** :   A rule ID that is unique within 
     : 1960 - 13: type: keyword
     : 1961 - 12: example: 101
     : 1962 - 110: **`rule.license`** :   Name of the license under w
     : 1963 - 13: type: keyword
     : 1964 - 19: example: Apache 2.0
     : 1965 - 75: **`rule.name`** :   The name of the rule or signat
     : 1966 - 13: type: keyword
     : 1967 - 27: example: BLOCK_DNS_over_TLS
     : 1968 - 273: **`rule.reference`** :   Reference URL to addition
     : 1969 - 13: type: keyword
     : 1970 - 51: example: https://en.wikipedia.org/wiki/DNS_over_TL
     : 1971 - 136: **`rule.ruleset`** :   Name of the ruleset, policy
     : 1972 - 13: type: keyword
     : 1973 - 34: example: Standard_Protocol_Filters
     : 1974 - 163: **`rule.uuid`** :   A rule ID that is unique withi
     : 1975 - 13: type: keyword
     : 1976 - 19: example: 1100110011
     : 1977 - 82: **`rule.version`** :   The version / revision of t
     : 1978 - 13: type: keyword
     : 1979 - 12: example: 1.1
   : 1980 - 7101: ## server [_server]  A Server is defined as the re
     : 1981 - 19: ## server [_server]
     : 1982 - 890: A Server is defined as the responder in a network 
     : 1983 - 290: **`server.address`** :   Some event server address
     : 1984 - 13: type: keyword
     : 1985 - 161: **`server.as.number`** :   Unique number allocated
     : 1986 - 10: type: long
     : 1987 - 14: example: 15169
     : 1988 - 56: **`server.as.organization.name`** :   Organization
     : 1989 - 13: type: keyword
     : 1990 - 19: example: Google LLC
     : 1991 - 64: **`server.as.organization.name.text`** :   type: m
     : 1992 - 64: **`server.bytes`** :   Bytes sent from the server 
     : 1993 - 10: type: long
     : 1994 - 12: example: 184
     : 1995 - 13: format: bytes
     : 1996 - 228: **`server.domain`** :   The domain name of the ser
     : 1997 - 13: type: keyword
     : 1998 - 24: example: foo.example.com
     : 1999 - 41: **`server.geo.city_name`** :   City name.
     : 2000 - 13: type: keyword
     : 2001 - 17: example: Montreal
     : 2002 - 82: **`server.geo.continent_code`** :   Two-letter cod
     : 2003 - 13: type: keyword
     : 2004 - 11: example: NA
     : 2005 - 58: **`server.geo.continent_name`** :   Name of the co
     : 2006 - 13: type: keyword
     : 2007 - 22: example: North America
     : 2008 - 55: **`server.geo.country_iso_code`** :   Country ISO 
     : 2009 - 13: type: keyword
     : 2010 - 11: example: CA
     : 2011 - 47: **`server.geo.country_name`** :   Country name.
     : 2012 - 13: type: keyword
     : 2013 - 15: example: Canada
     : 2014 - 53: **`server.geo.location`** :   Longitude and latitu
     : 2015 - 15: type: geo_point
     : 2016 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 2017 - 269: **`server.geo.name`** :   User-defined description
     : 2018 - 13: type: keyword
     : 2019 - 18: example: boston-dc
     : 2020 - 198: **`server.geo.postal_code`** :   Postal code assoc
     : 2021 - 13: type: keyword
     : 2022 - 14: example: 94040
     : 2023 - 53: **`server.geo.region_iso_code`** :   Region ISO co
     : 2024 - 13: type: keyword
     : 2025 - 14: example: CA-QC
     : 2026 - 45: **`server.geo.region_name`** :   Region name.
     : 2027 - 13: type: keyword
     : 2028 - 15: example: Quebec
     : 2029 - 89: **`server.geo.timezone`** :   The time zone of the
     : 2030 - 13: type: keyword
     : 2031 - 39: example: America/Argentina/Buenos_Aires
     : 2032 - 60: **`server.ip`** :   IP address of the server (IPv4
     : 2033 - 8: type: ip
     : 2034 - 280: **`server.mac`** :   MAC address of the server. Th
     : 2035 - 13: type: keyword
     : 2036 - 26: example: 00-00-5E-00-53-23
     : 2037 - 161: **`server.nat.ip`** :   Translated ip of destinati
     : 2038 - 8: type: ip
     : 2039 - 165: **`server.nat.port`** :   Translated port of desti
     : 2040 - 10: type: long
     : 2041 - 14: format: string
     : 2042 - 68: **`server.packets`** :   Packets sent from the ser
     : 2043 - 10: type: long
     : 2044 - 11: example: 12
     : 2045 - 41: **`server.port`** :   Port of the server.
     : 2046 - 10: type: long
     : 2047 - 14: format: string
     : 2048 - 391: **`server.registered_domain`** :   The highest reg
     : 2049 - 13: type: keyword
     : 2050 - 20: example: example.com
     : 2051 - 557: **`server.subdomain`** :   The subdomain portion o
     : 2052 - 13: type: keyword
     : 2053 - 13: example: east
     : 2054 - 424: **`server.top_level_domain`** :   The effective to
     : 2055 - 13: type: keyword
     : 2056 - 14: example: co.uk
     : 2057 - 129: **`server.user.domain`** :   Name of the directory
     : 2058 - 13: type: keyword
     : 2059 - 47: **`server.user.email`** :   User email address.
     : 2060 - 13: type: keyword
     : 2061 - 63: **`server.user.full_name`** :   User’s full name, 
     : 2062 - 13: type: keyword
     : 2063 - 24: example: Albert Einstein
     : 2064 - 58: **`server.user.full_name.text`** :   type: match_o
     : 2065 - 136: **`server.user.group.domain`** :   Name of the dir
     : 2066 - 13: type: keyword
     : 2067 - 86: **`server.user.group.id`** :   Unique identifier f
     : 2068 - 13: type: keyword
     : 2069 - 51: **`server.user.group.name`** :   Name of the group
     : 2070 - 13: type: keyword
     : 2071 - 187: **`server.user.hash`** :   Unique user hash to cor
     : 2072 - 13: type: keyword
     : 2073 - 55: **`server.user.id`** :   Unique identifier of the 
     : 2074 - 13: type: keyword
     : 2075 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 2076 - 59: **`server.user.name`** :   Short name or login of 
     : 2077 - 13: type: keyword
     : 2078 - 19: example: a.einstein
     : 2079 - 53: **`server.user.name.text`** :   type: match_only_t
     : 2080 - 73: **`server.user.roles`** :   Array of user roles at
     : 2081 - 13: type: keyword
     : 2082 - 43: example: ["kibana_admin", "reporting_user"]
   : 2083 - 9426: ## service [_service]  The service fields describe
     : 2084 - 21: ## service [_service]
     : 2085 - 163: The service fields describe the service for or fro
     : 2086 - 178: **`service.address`** :   Address where data about
     : 2087 - 13: type: keyword
     : 2088 - 24: example: 172.26.0.2:5432
     : 2089 - 317: **`service.environment`** :   Identifies the envir
     : 2090 - 13: type: keyword
     : 2091 - 19: example: production
     : 2092 - 153: **`service.ephemeral_id`** :   Ephemeral identifie
     : 2093 - 13: type: keyword
     : 2094 - 17: example: 8a4f500f
     : 2095 - 471: **`service.id`** :   Unique identifier of the runn
     : 2096 - 13: type: keyword
     : 2097 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
     : 2098 - 415: **`service.name`** :   Name of the service data is
     : 2099 - 13: type: keyword
     : 2100 - 30: example: elasticsearch-metrics
     : 2101 - 668: **`service.node.name`** :   Name of a service node
     : 2102 - 13: type: keyword
     : 2103 - 28: example: instance-0000000016
     : 2104 - 185: **`service.origin.address`** :   Address where dat
     : 2105 - 13: type: keyword
     : 2106 - 24: example: 172.26.0.2:5432
     : 2107 - 324: **`service.origin.environment`** :   Identifies th
     : 2108 - 13: type: keyword
     : 2109 - 19: example: production
     : 2110 - 160: **`service.origin.ephemeral_id`** :   Ephemeral id
     : 2111 - 13: type: keyword
     : 2112 - 17: example: 8a4f500f
     : 2113 - 478: **`service.origin.id`** :   Unique identifier of t
     : 2114 - 13: type: keyword
     : 2115 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
     : 2116 - 422: **`service.origin.name`** :   Name of the service 
     : 2117 - 13: type: keyword
     : 2118 - 30: example: elasticsearch-metrics
     : 2119 - 675: **`service.origin.node.name`** :   Name of a servi
     : 2120 - 13: type: keyword
     : 2121 - 28: example: instance-0000000016
     : 2122 - 60: **`service.origin.state`** :   Current state of th
     : 2123 - 13: type: keyword
     : 2124 - 265: **`service.origin.type`** :   The type of the serv
     : 2125 - 13: type: keyword
     : 2126 - 22: example: elasticsearch
     : 2127 - 160: **`service.origin.version`** :   Version of the se
     : 2128 - 13: type: keyword
     : 2129 - 14: example: 3.2.4
     : 2130 - 53: **`service.state`** :   Current state of the servi
     : 2131 - 13: type: keyword
     : 2132 - 185: **`service.target.address`** :   Address where dat
     : 2133 - 13: type: keyword
     : 2134 - 24: example: 172.26.0.2:5432
     : 2135 - 324: **`service.target.environment`** :   Identifies th
     : 2136 - 13: type: keyword
     : 2137 - 19: example: production
     : 2138 - 160: **`service.target.ephemeral_id`** :   Ephemeral id
     : 2139 - 13: type: keyword
     : 2140 - 17: example: 8a4f500f
     : 2141 - 478: **`service.target.id`** :   Unique identifier of t
     : 2142 - 13: type: keyword
     : 2143 - 49: example: d37e5ebfe0ae6c4972dbe9f0174a1637bb8247f6
     : 2144 - 422: **`service.target.name`** :   Name of the service 
     : 2145 - 13: type: keyword
     : 2146 - 30: example: elasticsearch-metrics
     : 2147 - 675: **`service.target.node.name`** :   Name of a servi
     : 2148 - 13: type: keyword
     : 2149 - 28: example: instance-0000000016
     : 2150 - 60: **`service.target.state`** :   Current state of th
     : 2151 - 13: type: keyword
     : 2152 - 265: **`service.target.type`** :   The type of the serv
     : 2153 - 13: type: keyword
     : 2154 - 22: example: elasticsearch
     : 2155 - 160: **`service.target.version`** :   Version of the se
     : 2156 - 13: type: keyword
     : 2157 - 14: example: 3.2.4
     : 2158 - 258: **`service.type`** :   The type of the service dat
     : 2159 - 13: type: keyword
     : 2160 - 22: example: elasticsearch
     : 2161 - 153: **`service.version`** :   Version of the service t
     : 2162 - 13: type: keyword
     : 2163 - 14: example: 3.2.4
   : 2164 - 6808: ## source [_source_2]  Source fields capture detai
     : 2165 - 21: ## source [_source_2]
     : 2166 - 573: Source fields capture details about the sender of 
     : 2167 - 290: **`source.address`** :   Some event source address
     : 2168 - 13: type: keyword
     : 2169 - 161: **`source.as.number`** :   Unique number allocated
     : 2170 - 10: type: long
     : 2171 - 14: example: 15169
     : 2172 - 56: **`source.as.organization.name`** :   Organization
     : 2173 - 13: type: keyword
     : 2174 - 19: example: Google LLC
     : 2175 - 64: **`source.as.organization.name.text`** :   type: m
     : 2176 - 69: **`source.bytes`** :   Bytes sent from the source 
     : 2177 - 10: type: long
     : 2178 - 12: example: 184
     : 2179 - 13: format: bytes
     : 2180 - 228: **`source.domain`** :   The domain name of the sou
     : 2181 - 13: type: keyword
     : 2182 - 24: example: foo.example.com
     : 2183 - 41: **`source.geo.city_name`** :   City name.
     : 2184 - 13: type: keyword
     : 2185 - 17: example: Montreal
     : 2186 - 82: **`source.geo.continent_code`** :   Two-letter cod
     : 2187 - 13: type: keyword
     : 2188 - 11: example: NA
     : 2189 - 58: **`source.geo.continent_name`** :   Name of the co
     : 2190 - 13: type: keyword
     : 2191 - 22: example: North America
     : 2192 - 55: **`source.geo.country_iso_code`** :   Country ISO 
     : 2193 - 13: type: keyword
     : 2194 - 11: example: CA
     : 2195 - 47: **`source.geo.country_name`** :   Country name.
     : 2196 - 13: type: keyword
     : 2197 - 15: example: Canada
     : 2198 - 53: **`source.geo.location`** :   Longitude and latitu
     : 2199 - 15: type: geo_point
     : 2200 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 2201 - 269: **`source.geo.name`** :   User-defined description
     : 2202 - 13: type: keyword
     : 2203 - 18: example: boston-dc
     : 2204 - 198: **`source.geo.postal_code`** :   Postal code assoc
     : 2205 - 13: type: keyword
     : 2206 - 14: example: 94040
     : 2207 - 53: **`source.geo.region_iso_code`** :   Region ISO co
     : 2208 - 13: type: keyword
     : 2209 - 14: example: CA-QC
     : 2210 - 45: **`source.geo.region_name`** :   Region name.
     : 2211 - 13: type: keyword
     : 2212 - 15: example: Quebec
     : 2213 - 89: **`source.geo.timezone`** :   The time zone of the
     : 2214 - 13: type: keyword
     : 2215 - 39: example: America/Argentina/Buenos_Aires
     : 2216 - 60: **`source.ip`** :   IP address of the source (IPv4
     : 2217 - 8: type: ip
     : 2218 - 280: **`source.mac`** :   MAC address of the source. Th
     : 2219 - 13: type: keyword
     : 2220 - 26: example: 00-00-5E-00-53-23
     : 2221 - 173: **`source.nat.ip`** :   Translated ip of source ba
     : 2222 - 8: type: ip
     : 2223 - 165: **`source.nat.port`** :   Translated port of sourc
     : 2224 - 10: type: long
     : 2225 - 14: format: string
     : 2226 - 73: **`source.packets`** :   Packets sent from the sou
     : 2227 - 10: type: long
     : 2228 - 11: example: 12
     : 2229 - 41: **`source.port`** :   Port of the source.
     : 2230 - 10: type: long
     : 2231 - 14: format: string
     : 2232 - 391: **`source.registered_domain`** :   The highest reg
     : 2233 - 13: type: keyword
     : 2234 - 20: example: example.com
     : 2235 - 557: **`source.subdomain`** :   The subdomain portion o
     : 2236 - 13: type: keyword
     : 2237 - 13: example: east
     : 2238 - 424: **`source.top_level_domain`** :   The effective to
     : 2239 - 13: type: keyword
     : 2240 - 14: example: co.uk
     : 2241 - 129: **`source.user.domain`** :   Name of the directory
     : 2242 - 13: type: keyword
     : 2243 - 47: **`source.user.email`** :   User email address.
     : 2244 - 13: type: keyword
     : 2245 - 63: **`source.user.full_name`** :   User’s full name, 
     : 2246 - 13: type: keyword
     : 2247 - 24: example: Albert Einstein
     : 2248 - 58: **`source.user.full_name.text`** :   type: match_o
     : 2249 - 136: **`source.user.group.domain`** :   Name of the dir
     : 2250 - 13: type: keyword
     : 2251 - 86: **`source.user.group.id`** :   Unique identifier f
     : 2252 - 13: type: keyword
     : 2253 - 51: **`source.user.group.name`** :   Name of the group
     : 2254 - 13: type: keyword
     : 2255 - 187: **`source.user.hash`** :   Unique user hash to cor
     : 2256 - 13: type: keyword
     : 2257 - 55: **`source.user.id`** :   Unique identifier of the 
     : 2258 - 13: type: keyword
     : 2259 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 2260 - 59: **`source.user.name`** :   Short name or login of 
     : 2261 - 13: type: keyword
     : 2262 - 19: example: a.einstein
     : 2263 - 53: **`source.user.name.text`** :   type: match_only_t
     : 2264 - 73: **`source.user.roles`** :   Array of user roles at
     : 2265 - 13: type: keyword
     : 2266 - 43: example: ["kibana_admin", "reporting_user"]
   : 2267 - 68088: ## threat [_threat]  Fields to classify events and
     : 2268 - 19: ## threat [_threat]
     : 2269 - 495: Fields to classify events and alerts according to 
     : 2270 - 137: **`threat.enrichments`** :   A list of associated 
     : 2271 - 12: type: nested
     : 2272 - 99: **`threat.enrichments.indicator`** :   Object cont
     : 2273 - 12: type: object
     : 2274 - 183: **`threat.enrichments.indicator.as.number`** :   U
     : 2275 - 10: type: long
     : 2276 - 14: example: 15169
     : 2277 - 78: **`threat.enrichments.indicator.as.organization.na
     : 2278 - 13: type: keyword
     : 2279 - 19: example: Google LLC
     : 2280 - 86: **`threat.enrichments.indicator.as.organization.na
     : 2281 - 314: **`threat.enrichments.indicator.confidence`** :   
     : 2282 - 13: type: keyword
     : 2283 - 15: example: Medium
     : 2284 - 104: **`threat.enrichments.indicator.description`** :  
     : 2285 - 13: type: keyword
     : 2286 - 58: example: IP x.x.x.x was observed delivering the An
     : 2287 - 131: **`threat.enrichments.indicator.email.address`** :
     : 2288 - 13: type: keyword
     : 2289 - 28: example: `phish@example.com`
     : 2290 - 142: **`threat.enrichments.indicator.file.accessed`** :
     : 2291 - 10: type: date
     : 2292 - 283: **`threat.enrichments.indicator.file.attributes`**
     : 2293 - 13: type: keyword
     : 2294 - 31: example: ["readonly", "system"]
     : 2295 - 256: **`threat.enrichments.indicator.file.code_signatur
     : 2296 - 13: type: keyword
     : 2297 - 15: example: sha256
     : 2298 - 111: **`threat.enrichments.indicator.file.code_signatur
     : 2299 - 13: type: boolean
     : 2300 - 13: example: true
     : 2301 - 227: **`threat.enrichments.indicator.file.code_signatur
     : 2302 - 13: type: keyword
     : 2303 - 28: example: com.apple.xpc.proxy
     : 2304 - 290: **`threat.enrichments.indicator.file.code_signatur
     : 2305 - 13: type: keyword
     : 2306 - 29: example: ERROR_UNTRUSTED_ROOT
     : 2307 - 103: **`threat.enrichments.indicator.file.code_signatur
     : 2308 - 13: type: keyword
     : 2309 - 30: example: Microsoft Corporation
     : 2310 - 220: **`threat.enrichments.indicator.file.code_signatur
     : 2311 - 13: type: keyword
     : 2312 - 19: example: EQHXZ8M8AV
     : 2313 - 132: **`threat.enrichments.indicator.file.code_signatur
     : 2314 - 10: type: date
     : 2315 - 29: example: 2021-01-01T12:10:30Z
     : 2316 - 263: **`threat.enrichments.indicator.file.code_signatur
     : 2317 - 13: type: boolean
     : 2318 - 13: example: true
     : 2319 - 198: **`threat.enrichments.indicator.file.code_signatur
     : 2320 - 13: type: boolean
     : 2321 - 13: example: true
     : 2322 - 126: **`threat.enrichments.indicator.file.created`** : 
     : 2323 - 10: type: date
     : 2324 - 259: **`threat.enrichments.indicator.file.ctime`** :   
     : 2325 - 10: type: date
     : 2326 - 89: **`threat.enrichments.indicator.file.device`** :  
     : 2327 - 13: type: keyword
     : 2328 - 12: example: sda
     : 2329 - 144: **`threat.enrichments.indicator.file.directory`** 
     : 2330 - 13: type: keyword
     : 2331 - 20: example: /home/alice
     : 2332 - 194: **`threat.enrichments.indicator.file.drive_letter`
     : 2333 - 13: type: keyword
     : 2334 - 10: example: C
     : 2335 - 98: **`threat.enrichments.indicator.file.elf.architect
     : 2336 - 13: type: keyword
     : 2337 - 15: example: x86-64
     : 2338 - 85: **`threat.enrichments.indicator.file.elf.byte_orde
     : 2339 - 13: type: keyword
     : 2340 - 22: example: Little Endian
     : 2341 - 82: **`threat.enrichments.indicator.file.elf.cpu_type`
     : 2342 - 13: type: keyword
     : 2343 - 14: example: Intel
     : 2344 - 194: **`threat.enrichments.indicator.file.elf.creation_
     : 2345 - 10: type: date
     : 2346 - 97: **`threat.enrichments.indicator.file.elf.exports`*
     : 2347 - 15: type: flattened
     : 2348 - 121: **`threat.enrichments.indicator.file.elf.header.ab
     : 2349 - 13: type: keyword
     : 2350 - 90: **`threat.enrichments.indicator.file.elf.header.cl
     : 2351 - 13: type: keyword
     : 2352 - 89: **`threat.enrichments.indicator.file.elf.header.da
     : 2353 - 13: type: keyword
     : 2354 - 100: **`threat.enrichments.indicator.file.elf.header.en
     : 2355 - 10: type: long
     : 2356 - 14: format: string
     : 2357 - 99: **`threat.enrichments.indicator.file.elf.header.ob
     : 2358 - 13: type: keyword
     : 2359 - 113: **`threat.enrichments.indicator.file.elf.header.os
     : 2360 - 13: type: keyword
     : 2361 - 88: **`threat.enrichments.indicator.file.elf.header.ty
     : 2362 - 13: type: keyword
     : 2363 - 89: **`threat.enrichments.indicator.file.elf.header.ve
     : 2364 - 13: type: keyword
     : 2365 - 97: **`threat.enrichments.indicator.file.elf.imports`*
     : 2366 - 15: type: flattened
     : 2367 - 225: **`threat.enrichments.indicator.file.elf.sections`
     : 2368 - 12: type: nested
     : 2369 - 113: **`threat.enrichments.indicator.file.elf.sections.
     : 2370 - 10: type: long
     : 2371 - 14: format: number
     : 2372 - 110: **`threat.enrichments.indicator.file.elf.sections.
     : 2373 - 10: type: long
     : 2374 - 14: format: number
     : 2375 - 86: **`threat.enrichments.indicator.file.elf.sections.
     : 2376 - 13: type: keyword
     : 2377 - 84: **`threat.enrichments.indicator.file.elf.sections.
     : 2378 - 13: type: keyword
     : 2379 - 97: **`threat.enrichments.indicator.file.elf.sections.
     : 2380 - 13: type: keyword
     : 2381 - 102: **`threat.enrichments.indicator.file.elf.sections.
     : 2382 - 10: type: long
     : 2383 - 13: format: bytes
     : 2384 - 84: **`threat.enrichments.indicator.file.elf.sections.
     : 2385 - 13: type: keyword
     : 2386 - 106: **`threat.enrichments.indicator.file.elf.sections.
     : 2387 - 10: type: long
     : 2388 - 14: format: string
     : 2389 - 100: **`threat.enrichments.indicator.file.elf.sections.
     : 2390 - 10: type: long
     : 2391 - 14: format: string
     : 2392 - 225: **`threat.enrichments.indicator.file.elf.segments`
     : 2393 - 12: type: nested
     : 2394 - 94: **`threat.enrichments.indicator.file.elf.segments.
     : 2395 - 13: type: keyword
     : 2396 - 86: **`threat.enrichments.indicator.file.elf.segments.
     : 2397 - 13: type: keyword
     : 2398 - 114: **`threat.enrichments.indicator.file.elf.shared_li
     : 2399 - 13: type: keyword
     : 2400 - 91: **`threat.enrichments.indicator.file.elf.telfhash`
     : 2401 - 13: type: keyword
     : 2402 - 226: **`threat.enrichments.indicator.file.extension`** 
     : 2403 - 13: type: keyword
     : 2404 - 12: example: png
     : 2405 - 816: **`threat.enrichments.indicator.file.fork_name`** 
     : 2406 - 13: type: keyword
     : 2407 - 23: example: Zone.Identifer
     : 2408 - 83: **`threat.enrichments.indicator.file.gid`** :   Pr
     : 2409 - 13: type: keyword
     : 2410 - 13: example: 1001
     : 2411 - 81: **`threat.enrichments.indicator.file.group`** :   
     : 2412 - 13: type: keyword
     : 2413 - 14: example: alice
     : 2414 - 62: **`threat.enrichments.indicator.file.hash.md5`** :
     : 2415 - 13: type: keyword
     : 2416 - 64: **`threat.enrichments.indicator.file.hash.sha1`** 
     : 2417 - 13: type: keyword
     : 2418 - 68: **`threat.enrichments.indicator.file.hash.sha256`*
     : 2419 - 13: type: keyword
     : 2420 - 68: **`threat.enrichments.indicator.file.hash.sha512`*
     : 2421 - 13: type: keyword
     : 2422 - 68: **`threat.enrichments.indicator.file.hash.ssdeep`*
     : 2423 - 13: type: keyword
     : 2424 - 96: **`threat.enrichments.indicator.file.inode`** :   
     : 2425 - 13: type: keyword
     : 2426 - 15: example: 256383
     : 2427 - 243: **`threat.enrichments.indicator.file.mime_type`** 
     : 2428 - 13: type: keyword
     : 2429 - 90: **`threat.enrichments.indicator.file.mode`** :   M
     : 2430 - 13: type: keyword
     : 2431 - 13: example: 0640
     : 2432 - 90: **`threat.enrichments.indicator.file.mtime`** :   
     : 2433 - 10: type: date
     : 2434 - 113: **`threat.enrichments.indicator.file.name`** :   N
     : 2435 - 13: type: keyword
     : 2436 - 20: example: example.png
     : 2437 - 72: **`threat.enrichments.indicator.file.owner`** :   
     : 2438 - 13: type: keyword
     : 2439 - 14: example: alice
     : 2440 - 150: **`threat.enrichments.indicator.file.path`** :   F
     : 2441 - 13: type: keyword
     : 2442 - 32: example: /home/alice/example.png
     : 2443 - 75: **`threat.enrichments.indicator.file.path.text`** 
     : 2444 - 97: **`threat.enrichments.indicator.file.pe.architectu
     : 2445 - 13: type: keyword
     : 2446 - 12: example: x64
     : 2447 - 115: **`threat.enrichments.indicator.file.pe.company`**
     : 2448 - 13: type: keyword
     : 2449 - 30: example: Microsoft Corporation
     : 2450 - 118: **`threat.enrichments.indicator.file.pe.descriptio
     : 2451 - 13: type: keyword
     : 2452 - 14: example: Paint
     : 2453 - 115: **`threat.enrichments.indicator.file.pe.file_versi
     : 2454 - 13: type: keyword
     : 2455 - 23: example: 6.3.9600.17415
     : 2456 - 387: **`threat.enrichments.indicator.file.pe.imphash`**
     : 2457 - 13: type: keyword
     : 2458 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 2459 - 118: **`threat.enrichments.indicator.file.pe.original_f
     : 2460 - 13: type: keyword
     : 2461 - 20: example: MSPAINT.EXE
     : 2462 - 115: **`threat.enrichments.indicator.file.pe.product`**
     : 2463 - 13: type: keyword
     : 2464 - 45: example: Microsoft® Windows® Operating System
     : 2465 - 110: **`threat.enrichments.indicator.file.size`** :   F
     : 2466 - 10: type: long
     : 2467 - 14: example: 16384
     : 2468 - 81: **`threat.enrichments.indicator.file.target_path`*
     : 2469 - 13: type: keyword
     : 2470 - 82: **`threat.enrichments.indicator.file.target_path.t
     : 2471 - 83: **`threat.enrichments.indicator.file.type`** :   F
     : 2472 - 13: type: keyword
     : 2473 - 13: example: file
     : 2474 - 113: **`threat.enrichments.indicator.file.uid`** :   Th
     : 2475 - 13: type: keyword
     : 2476 - 13: example: 1001
     : 2477 - 252: **`threat.enrichments.indicator.file.x509.alternat
     : 2478 - 13: type: keyword
     : 2479 - 21: example: *.elastic.co
     : 2480 - 126: **`threat.enrichments.indicator.file.x509.issuer.c
     : 2481 - 13: type: keyword
     : 2482 - 46: example: Example SHA2 High Assurance Server CA
     : 2483 - 87: **`threat.enrichments.indicator.file.x509.issuer.c
     : 2484 - 13: type: keyword
     : 2485 - 11: example: US
     : 2486 - 132: **`threat.enrichments.indicator.file.x509.issuer.d
     : 2487 - 13: type: keyword
     : 2488 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 2489 - 91: **`threat.enrichments.indicator.file.x509.issuer.l
     : 2490 - 13: type: keyword
     : 2491 - 22: example: Mountain View
     : 2492 - 128: **`threat.enrichments.indicator.file.x509.issuer.o
     : 2493 - 13: type: keyword
     : 2494 - 20: example: Example Inc
     : 2495 - 143: **`threat.enrichments.indicator.file.x509.issuer.o
     : 2496 - 13: type: keyword
     : 2497 - 24: example: www.example.com
     : 2498 - 119: **`threat.enrichments.indicator.file.x509.issuer.s
     : 2499 - 13: type: keyword
     : 2500 - 19: example: California
     : 2501 - 119: **`threat.enrichments.indicator.file.x509.not_afte
     : 2502 - 10: type: date
     : 2503 - 34: example: 2020-07-16 03:15:39+00:00
     : 2504 - 116: **`threat.enrichments.indicator.file.x509.not_befo
     : 2505 - 10: type: date
     : 2506 - 34: example: 2019-08-16 01:40:25+00:00
     : 2507 - 112: **`threat.enrichments.indicator.file.x509.public_k
     : 2508 - 13: type: keyword
     : 2509 - 12: example: RSA
     : 2510 - 152: **`threat.enrichments.indicator.file.x509.public_k
     : 2511 - 13: type: keyword
     : 2512 - 17: example: nistp521
     : 2513 - 136: **`threat.enrichments.indicator.file.x509.public_k
     : 2514 - 10: type: long
     : 2515 - 14: example: 65537
     : 2516 - 21: Field is not indexed.
     : 2517 - 106: **`threat.enrichments.indicator.file.x509.public_k
     : 2518 - 10: type: long
     : 2519 - 13: example: 2048
     : 2520 - 232: **`threat.enrichments.indicator.file.x509.serial_n
     : 2521 - 13: type: keyword
     : 2522 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 2523 - 255: **`threat.enrichments.indicator.file.x509.signatur
     : 2524 - 13: type: keyword
     : 2525 - 19: example: SHA256-RSA
     : 2526 - 106: **`threat.enrichments.indicator.file.x509.subject.
     : 2527 - 13: type: keyword
     : 2528 - 34: example: shared.global.example.net
     : 2529 - 87: **`threat.enrichments.indicator.file.x509.subject.
     : 2530 - 13: type: keyword
     : 2531 - 11: example: US
     : 2532 - 134: **`threat.enrichments.indicator.file.x509.subject.
     : 2533 - 13: type: keyword
     : 2534 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 2535 - 92: **`threat.enrichments.indicator.file.x509.subject.
     : 2536 - 13: type: keyword
     : 2537 - 22: example: San Francisco
     : 2538 - 107: **`threat.enrichments.indicator.file.x509.subject.
     : 2539 - 13: type: keyword
     : 2540 - 22: example: Example, Inc.
     : 2541 - 122: **`threat.enrichments.indicator.file.x509.subject.
     : 2542 - 13: type: keyword
     : 2543 - 120: **`threat.enrichments.indicator.file.x509.subject.
     : 2544 - 13: type: keyword
     : 2545 - 19: example: California
     : 2546 - 87: **`threat.enrichments.indicator.file.x509.version_
     : 2547 - 13: type: keyword
     : 2548 - 10: example: 3
     : 2549 - 132: **`threat.enrichments.indicator.first_seen`** :   
     : 2550 - 10: type: date
     : 2551 - 33: example: 2020-11-05T17:25:47.000Z
     : 2552 - 63: **`threat.enrichments.indicator.geo.city_name`** :
     : 2553 - 13: type: keyword
     : 2554 - 17: example: Montreal
     : 2555 - 104: **`threat.enrichments.indicator.geo.continent_code
     : 2556 - 13: type: keyword
     : 2557 - 11: example: NA
     : 2558 - 80: **`threat.enrichments.indicator.geo.continent_name
     : 2559 - 13: type: keyword
     : 2560 - 22: example: North America
     : 2561 - 77: **`threat.enrichments.indicator.geo.country_iso_co
     : 2562 - 13: type: keyword
     : 2563 - 11: example: CA
     : 2564 - 69: **`threat.enrichments.indicator.geo.country_name`*
     : 2565 - 13: type: keyword
     : 2566 - 15: example: Canada
     : 2567 - 75: **`threat.enrichments.indicator.geo.location`** : 
     : 2568 - 15: type: geo_point
     : 2569 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 2570 - 291: **`threat.enrichments.indicator.geo.name`** :   Us
     : 2571 - 13: type: keyword
     : 2572 - 18: example: boston-dc
     : 2573 - 220: **`threat.enrichments.indicator.geo.postal_code`**
     : 2574 - 13: type: keyword
     : 2575 - 14: example: 94040
     : 2576 - 75: **`threat.enrichments.indicator.geo.region_iso_cod
     : 2577 - 13: type: keyword
     : 2578 - 14: example: CA-QC
     : 2579 - 67: **`threat.enrichments.indicator.geo.region_name`**
     : 2580 - 13: type: keyword
     : 2581 - 15: example: Quebec
     : 2582 - 111: **`threat.enrichments.indicator.geo.timezone`** : 
     : 2583 - 13: type: keyword
     : 2584 - 39: example: America/Argentina/Buenos_Aires
     : 2585 - 117: **`threat.enrichments.indicator.ip`** :   Identifi
     : 2586 - 8: type: ip
     : 2587 - 16: example: 1.2.3.4
     : 2588 - 130: **`threat.enrichments.indicator.last_seen`** :   T
     : 2589 - 10: type: date
     : 2590 - 33: example: 2020-11-05T17:25:47.000Z
     : 2591 - 145: **`threat.enrichments.indicator.marking.tlp`** :  
     : 2592 - 13: type: keyword
     : 2593 - 14: example: White
     : 2594 - 139: **`threat.enrichments.indicator.modified_at`** :  
     : 2595 - 10: type: date
     : 2596 - 33: example: 2020-11-05T17:25:47.000Z
     : 2597 - 119: **`threat.enrichments.indicator.port`** :   Identi
     : 2598 - 10: type: long
     : 2599 - 12: example: 443
     : 2600 - 85: **`threat.enrichments.indicator.provider`** :   Th
     : 2601 - 13: type: keyword
     : 2602 - 20: example: lrz_urlhaus
     : 2603 - 118: **`threat.enrichments.indicator.reference`** :   R
     : 2604 - 13: type: keyword
     : 2605 - 53: example: https://system.example.com/indicator/0001
     : 2606 - 335: **`threat.enrichments.indicator.registry.data.byte
     : 2607 - 13: type: keyword
     : 2608 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
     : 2609 - 459: **`threat.enrichments.indicator.registry.data.stri
     : 2610 - 14: type: wildcard
     : 2611 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
     : 2612 - 102: **`threat.enrichments.indicator.registry.data.type
     : 2613 - 13: type: keyword
     : 2614 - 15: example: REG_SZ
     : 2615 - 83: **`threat.enrichments.indicator.registry.hive`** :
     : 2616 - 13: type: keyword
     : 2617 - 13: example: HKLM
     : 2618 - 79: **`threat.enrichments.indicator.registry.key`** : 
     : 2619 - 13: type: keyword
     : 2620 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
     : 2621 - 93: **`threat.enrichments.indicator.registry.path`** :
     : 2622 - 13: type: keyword
     : 2623 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
     : 2624 - 80: **`threat.enrichments.indicator.registry.value`** 
     : 2625 - 13: type: keyword
     : 2626 - 17: example: Debugger
     : 2627 - 126: **`threat.enrichments.indicator.scanner_stats`** :
     : 2628 - 10: type: long
     : 2629 - 10: example: 4
     : 2630 - 120: **`threat.enrichments.indicator.sightings`** :   N
     : 2631 - 10: type: long
     : 2632 - 11: example: 20
     : 2633 - 340: **`threat.enrichments.indicator.type`** :   Type o
     : 2634 - 13: type: keyword
     : 2635 - 18: example: ipv4-addr
     : 2636 - 397: **`threat.enrichments.indicator.url.domain`** :   
     : 2637 - 13: type: keyword
     : 2638 - 23: example: www.elastic.co
     : 2639 - 453: **`threat.enrichments.indicator.url.extension`** :
     : 2640 - 13: type: keyword
     : 2641 - 12: example: png
     : 2642 - 138: **`threat.enrichments.indicator.url.fragment`** : 
     : 2643 - 13: type: keyword
     : 2644 - 198: **`threat.enrichments.indicator.url.full`** :   If
     : 2645 - 14: type: wildcard
     : 2646 - 62: example: https://www.elastic.co:443/search?q=elast
     : 2647 - 74: **`threat.enrichments.indicator.url.full.text`** :
     : 2648 - 320: **`threat.enrichments.indicator.url.original`** : 
     : 2649 - 14: type: wildcard
     : 2650 - 89: example: https://www.elastic.co:443/search?q=elast
     : 2651 - 78: **`threat.enrichments.indicator.url.original.text`
     : 2652 - 76: **`threat.enrichments.indicator.url.password`** : 
     : 2653 - 13: type: keyword
     : 2654 - 87: **`threat.enrichments.indicator.url.path`** :   Pa
     : 2655 - 14: type: wildcard
     : 2656 - 81: **`threat.enrichments.indicator.url.port`** :   Po
     : 2657 - 10: type: long
     : 2658 - 12: example: 443
     : 2659 - 14: format: string
     : 2660 - 377: **`threat.enrichments.indicator.url.query`** :   T
     : 2661 - 13: type: keyword
     : 2662 - 414: **`threat.enrichments.indicator.url.registered_dom
     : 2663 - 13: type: keyword
     : 2664 - 20: example: example.com
     : 2665 - 130: **`threat.enrichments.indicator.url.scheme`** :   
     : 2666 - 13: type: keyword
     : 2667 - 14: example: https
     : 2668 - 583: **`threat.enrichments.indicator.url.subdomain`** :
     : 2669 - 13: type: keyword
     : 2670 - 13: example: east
     : 2671 - 450: **`threat.enrichments.indicator.url.top_level_doma
     : 2672 - 13: type: keyword
     : 2673 - 14: example: co.uk
     : 2674 - 76: **`threat.enrichments.indicator.url.username`** : 
     : 2675 - 13: type: keyword
     : 2676 - 247: **`threat.enrichments.indicator.x509.alternative_n
     : 2677 - 13: type: keyword
     : 2678 - 21: example: *.elastic.co
     : 2679 - 121: **`threat.enrichments.indicator.x509.issuer.common
     : 2680 - 13: type: keyword
     : 2681 - 46: example: Example SHA2 High Assurance Server CA
     : 2682 - 82: **`threat.enrichments.indicator.x509.issuer.countr
     : 2683 - 13: type: keyword
     : 2684 - 11: example: US
     : 2685 - 127: **`threat.enrichments.indicator.x509.issuer.distin
     : 2686 - 13: type: keyword
     : 2687 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 2688 - 86: **`threat.enrichments.indicator.x509.issuer.locali
     : 2689 - 13: type: keyword
     : 2690 - 22: example: Mountain View
     : 2691 - 123: **`threat.enrichments.indicator.x509.issuer.organi
     : 2692 - 13: type: keyword
     : 2693 - 20: example: Example Inc
     : 2694 - 138: **`threat.enrichments.indicator.x509.issuer.organi
     : 2695 - 13: type: keyword
     : 2696 - 24: example: www.example.com
     : 2697 - 114: **`threat.enrichments.indicator.x509.issuer.state_
     : 2698 - 13: type: keyword
     : 2699 - 19: example: California
     : 2700 - 114: **`threat.enrichments.indicator.x509.not_after`** 
     : 2701 - 10: type: date
     : 2702 - 34: example: 2020-07-16 03:15:39+00:00
     : 2703 - 111: **`threat.enrichments.indicator.x509.not_before`**
     : 2704 - 10: type: date
     : 2705 - 34: example: 2019-08-16 01:40:25+00:00
     : 2706 - 107: **`threat.enrichments.indicator.x509.public_key_al
     : 2707 - 13: type: keyword
     : 2708 - 12: example: RSA
     : 2709 - 147: **`threat.enrichments.indicator.x509.public_key_cu
     : 2710 - 13: type: keyword
     : 2711 - 17: example: nistp521
     : 2712 - 131: **`threat.enrichments.indicator.x509.public_key_ex
     : 2713 - 10: type: long
     : 2714 - 14: example: 65537
     : 2715 - 21: Field is not indexed.
     : 2716 - 101: **`threat.enrichments.indicator.x509.public_key_si
     : 2717 - 10: type: long
     : 2718 - 13: example: 2048
     : 2719 - 227: **`threat.enrichments.indicator.x509.serial_number
     : 2720 - 13: type: keyword
     : 2721 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 2722 - 250: **`threat.enrichments.indicator.x509.signature_alg
     : 2723 - 13: type: keyword
     : 2724 - 19: example: SHA256-RSA
     : 2725 - 101: **`threat.enrichments.indicator.x509.subject.commo
     : 2726 - 13: type: keyword
     : 2727 - 34: example: shared.global.example.net
     : 2728 - 82: **`threat.enrichments.indicator.x509.subject.count
     : 2729 - 13: type: keyword
     : 2730 - 11: example: US
     : 2731 - 129: **`threat.enrichments.indicator.x509.subject.disti
     : 2732 - 13: type: keyword
     : 2733 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 2734 - 87: **`threat.enrichments.indicator.x509.subject.local
     : 2735 - 13: type: keyword
     : 2736 - 22: example: San Francisco
     : 2737 - 102: **`threat.enrichments.indicator.x509.subject.organ
     : 2738 - 13: type: keyword
     : 2739 - 22: example: Example, Inc.
     : 2740 - 117: **`threat.enrichments.indicator.x509.subject.organ
     : 2741 - 13: type: keyword
     : 2742 - 115: **`threat.enrichments.indicator.x509.subject.state
     : 2743 - 13: type: keyword
     : 2744 - 19: example: California
     : 2745 - 82: **`threat.enrichments.indicator.x509.version_numbe
     : 2746 - 13: type: keyword
     : 2747 - 10: example: 3
     : 2748 - 141: **`threat.enrichments.matched.atomic`** :   Identi
     : 2749 - 13: type: keyword
     : 2750 - 23: example: bad-domain.com
     : 2751 - 147: **`threat.enrichments.matched.field`** :   Identif
     : 2752 - 13: type: keyword
     : 2753 - 25: example: file.hash.sha256
     : 2754 - 105: **`threat.enrichments.matched.id`** :   Identifies
     : 2755 - 13: type: keyword
     : 2756 - 45: example: ff93aee5-86a1-4a61-b0e6-0cdc313d01b5
     : 2757 - 111: **`threat.enrichments.matched.index`** :   Identif
     : 2758 - 13: type: keyword
     : 2759 - 41: example: filebeat-8.0.0-2021.05.23-000011
     : 2760 - 132: **`threat.enrichments.matched.type`** :   Identifi
     : 2761 - 13: type: keyword
     : 2762 - 29: example: indicator_match_rule
     : 2763 - 270: **`threat.framework`** :   Name of the threat fram
     : 2764 - 13: type: keyword
     : 2765 - 21: example: MITRE ATT&CK
     : 2766 - 221: **`threat.group.alias`** :   The alias(es) of the 
     : 2767 - 13: type: keyword
     : 2768 - 31: example: [ "Magecart Group 6" ]
     : 2769 - 204: **`threat.group.id`** :   The id of the group for 
     : 2770 - 13: type: keyword
     : 2771 - 14: example: G0037
     : 2772 - 210: **`threat.group.name`** :   The name of the group 
     : 2773 - 13: type: keyword
     : 2774 - 13: example: FIN6
     : 2775 - 233: **`threat.group.reference`** :   The reference URL
     : 2776 - 13: type: keyword
     : 2777 - 47: example: https://attack.mitre.org/groups/G0037/
     : 2778 - 171: **`threat.indicator.as.number`** :   Unique number
     : 2779 - 10: type: long
     : 2780 - 14: example: 15169
     : 2781 - 66: **`threat.indicator.as.organization.name`** :   Or
     : 2782 - 13: type: keyword
     : 2783 - 19: example: Google LLC
     : 2784 - 74: **`threat.indicator.as.organization.name.text`** :
     : 2785 - 302: **`threat.indicator.confidence`** :   Identifies t
     : 2786 - 13: type: keyword
     : 2787 - 15: example: Medium
     : 2788 - 92: **`threat.indicator.description`** :   Describes t
     : 2789 - 13: type: keyword
     : 2790 - 58: example: IP x.x.x.x was observed delivering the An
     : 2791 - 119: **`threat.indicator.email.address`** :   Identifie
     : 2792 - 13: type: keyword
     : 2793 - 28: example: `phish@example.com`
     : 2794 - 130: **`threat.indicator.file.accessed`** :   Last time
     : 2795 - 10: type: date
     : 2796 - 271: **`threat.indicator.file.attributes`** :   Array o
     : 2797 - 13: type: keyword
     : 2798 - 31: example: ["readonly", "system"]
     : 2799 - 244: **`threat.indicator.file.code_signature.digest_alg
     : 2800 - 13: type: keyword
     : 2801 - 15: example: sha256
     : 2802 - 99: **`threat.indicator.file.code_signature.exists`** 
     : 2803 - 13: type: boolean
     : 2804 - 13: example: true
     : 2805 - 215: **`threat.indicator.file.code_signature.signing_id
     : 2806 - 13: type: keyword
     : 2807 - 28: example: com.apple.xpc.proxy
     : 2808 - 278: **`threat.indicator.file.code_signature.status`** 
     : 2809 - 13: type: keyword
     : 2810 - 29: example: ERROR_UNTRUSTED_ROOT
     : 2811 - 91: **`threat.indicator.file.code_signature.subject_na
     : 2812 - 13: type: keyword
     : 2813 - 30: example: Microsoft Corporation
     : 2814 - 208: **`threat.indicator.file.code_signature.team_id`**
     : 2815 - 13: type: keyword
     : 2816 - 19: example: EQHXZ8M8AV
     : 2817 - 120: **`threat.indicator.file.code_signature.timestamp`
     : 2818 - 10: type: date
     : 2819 - 29: example: 2021-01-01T12:10:30Z
     : 2820 - 251: **`threat.indicator.file.code_signature.trusted`**
     : 2821 - 13: type: boolean
     : 2822 - 13: example: true
     : 2823 - 186: **`threat.indicator.file.code_signature.valid`** :
     : 2824 - 13: type: boolean
     : 2825 - 13: example: true
     : 2826 - 114: **`threat.indicator.file.created`** :   File creat
     : 2827 - 10: type: date
     : 2828 - 247: **`threat.indicator.file.ctime`** :   Last time th
     : 2829 - 10: type: date
     : 2830 - 77: **`threat.indicator.file.device`** :   Device that
     : 2831 - 13: type: keyword
     : 2832 - 12: example: sda
     : 2833 - 132: **`threat.indicator.file.directory`** :   Director
     : 2834 - 13: type: keyword
     : 2835 - 20: example: /home/alice
     : 2836 - 182: **`threat.indicator.file.drive_letter`** :   Drive
     : 2837 - 13: type: keyword
     : 2838 - 10: example: C
     : 2839 - 86: **`threat.indicator.file.elf.architecture`** :   M
     : 2840 - 13: type: keyword
     : 2841 - 15: example: x86-64
     : 2842 - 73: **`threat.indicator.file.elf.byte_order`** :   Byt
     : 2843 - 13: type: keyword
     : 2844 - 22: example: Little Endian
     : 2845 - 70: **`threat.indicator.file.elf.cpu_type`** :   CPU t
     : 2846 - 13: type: keyword
     : 2847 - 14: example: Intel
     : 2848 - 182: **`threat.indicator.file.elf.creation_date`** :   
     : 2849 - 10: type: date
     : 2850 - 85: **`threat.indicator.file.elf.exports`** :   List o
     : 2851 - 15: type: flattened
     : 2852 - 109: **`threat.indicator.file.elf.header.abi_version`**
     : 2853 - 13: type: keyword
     : 2854 - 78: **`threat.indicator.file.elf.header.class`** :   H
     : 2855 - 13: type: keyword
     : 2856 - 77: **`threat.indicator.file.elf.header.data`** :   Da
     : 2857 - 13: type: keyword
     : 2858 - 88: **`threat.indicator.file.elf.header.entrypoint`** 
     : 2859 - 10: type: long
     : 2860 - 14: format: string
     : 2861 - 87: **`threat.indicator.file.elf.header.object_version
     : 2862 - 13: type: keyword
     : 2863 - 101: **`threat.indicator.file.elf.header.os_abi`** :   
     : 2864 - 13: type: keyword
     : 2865 - 76: **`threat.indicator.file.elf.header.type`** :   He
     : 2866 - 13: type: keyword
     : 2867 - 77: **`threat.indicator.file.elf.header.version`** :  
     : 2868 - 13: type: keyword
     : 2869 - 85: **`threat.indicator.file.elf.imports`** :   List o
     : 2870 - 15: type: flattened
     : 2871 - 213: **`threat.indicator.file.elf.sections`** :   An ar
     : 2872 - 12: type: nested
     : 2873 - 101: **`threat.indicator.file.elf.sections.chi2`** :   
     : 2874 - 10: type: long
     : 2875 - 14: format: number
     : 2876 - 98: **`threat.indicator.file.elf.sections.entropy`** :
     : 2877 - 10: type: long
     : 2878 - 14: format: number
     : 2879 - 74: **`threat.indicator.file.elf.sections.flags`** :  
     : 2880 - 13: type: keyword
     : 2881 - 72: **`threat.indicator.file.elf.sections.name`** :   
     : 2882 - 13: type: keyword
     : 2883 - 85: **`threat.indicator.file.elf.sections.physical_off
     : 2884 - 13: type: keyword
     : 2885 - 90: **`threat.indicator.file.elf.sections.physical_siz
     : 2886 - 10: type: long
     : 2887 - 13: format: bytes
     : 2888 - 72: **`threat.indicator.file.elf.sections.type`** :   
     : 2889 - 13: type: keyword
     : 2890 - 94: **`threat.indicator.file.elf.sections.virtual_addr
     : 2891 - 10: type: long
     : 2892 - 14: format: string
     : 2893 - 88: **`threat.indicator.file.elf.sections.virtual_size
     : 2894 - 10: type: long
     : 2895 - 14: format: string
     : 2896 - 213: **`threat.indicator.file.elf.segments`** :   An ar
     : 2897 - 12: type: nested
     : 2898 - 82: **`threat.indicator.file.elf.segments.sections`** 
     : 2899 - 13: type: keyword
     : 2900 - 74: **`threat.indicator.file.elf.segments.type`** :   
     : 2901 - 13: type: keyword
     : 2902 - 102: **`threat.indicator.file.elf.shared_libraries`** :
     : 2903 - 13: type: keyword
     : 2904 - 79: **`threat.indicator.file.elf.telfhash`** :   telfh
     : 2905 - 13: type: keyword
     : 2906 - 214: **`threat.indicator.file.extension`** :   File ext
     : 2907 - 13: type: keyword
     : 2908 - 12: example: png
     : 2909 - 804: **`threat.indicator.file.fork_name`** :   A fork i
     : 2910 - 13: type: keyword
     : 2911 - 23: example: Zone.Identifer
     : 2912 - 71: **`threat.indicator.file.gid`** :   Primary group 
     : 2913 - 13: type: keyword
     : 2914 - 13: example: 1001
     : 2915 - 69: **`threat.indicator.file.group`** :   Primary grou
     : 2916 - 13: type: keyword
     : 2917 - 14: example: alice
     : 2918 - 50: **`threat.indicator.file.hash.md5`** :   MD5 hash.
     : 2919 - 13: type: keyword
     : 2920 - 52: **`threat.indicator.file.hash.sha1`** :   SHA1 has
     : 2921 - 13: type: keyword
     : 2922 - 56: **`threat.indicator.file.hash.sha256`** :   SHA256
     : 2923 - 13: type: keyword
     : 2924 - 56: **`threat.indicator.file.hash.sha512`** :   SHA512
     : 2925 - 13: type: keyword
     : 2926 - 56: **`threat.indicator.file.hash.ssdeep`** :   SSDEEP
     : 2927 - 13: type: keyword
     : 2928 - 84: **`threat.indicator.file.inode`** :   Inode repres
     : 2929 - 13: type: keyword
     : 2930 - 15: example: 256383
     : 2931 - 231: **`threat.indicator.file.mime_type`** :   MIME typ
     : 2932 - 13: type: keyword
     : 2933 - 78: **`threat.indicator.file.mode`** :   Mode of the f
     : 2934 - 13: type: keyword
     : 2935 - 13: example: 0640
     : 2936 - 78: **`threat.indicator.file.mtime`** :   Last time th
     : 2937 - 10: type: date
     : 2938 - 101: **`threat.indicator.file.name`** :   Name of the f
     : 2939 - 13: type: keyword
     : 2940 - 20: example: example.png
     : 2941 - 60: **`threat.indicator.file.owner`** :   File owner’s
     : 2942 - 13: type: keyword
     : 2943 - 14: example: alice
     : 2944 - 138: **`threat.indicator.file.path`** :   Full path to 
     : 2945 - 13: type: keyword
     : 2946 - 32: example: /home/alice/example.png
     : 2947 - 63: **`threat.indicator.file.path.text`** :   type: ma
     : 2948 - 85: **`threat.indicator.file.pe.architecture`** :   CP
     : 2949 - 13: type: keyword
     : 2950 - 12: example: x64
     : 2951 - 103: **`threat.indicator.file.pe.company`** :   Interna
     : 2952 - 13: type: keyword
     : 2953 - 30: example: Microsoft Corporation
     : 2954 - 106: **`threat.indicator.file.pe.description`** :   Int
     : 2955 - 13: type: keyword
     : 2956 - 14: example: Paint
     : 2957 - 103: **`threat.indicator.file.pe.file_version`** :   In
     : 2958 - 13: type: keyword
     : 2959 - 23: example: 6.3.9600.17415
     : 2960 - 375: **`threat.indicator.file.pe.imphash`** :   A hash 
     : 2961 - 13: type: keyword
     : 2962 - 41: example: 0c6803c4e922103c4dca5963aad36ddf
     : 2963 - 106: **`threat.indicator.file.pe.original_file_name`** 
     : 2964 - 13: type: keyword
     : 2965 - 20: example: MSPAINT.EXE
     : 2966 - 103: **`threat.indicator.file.pe.product`** :   Interna
     : 2967 - 13: type: keyword
     : 2968 - 45: example: Microsoft® Windows® Operating System
     : 2969 - 98: **`threat.indicator.file.size`** :   File size in 
     : 2970 - 10: type: long
     : 2971 - 14: example: 16384
     : 2972 - 69: **`threat.indicator.file.target_path`** :   Target
     : 2973 - 13: type: keyword
     : 2974 - 70: **`threat.indicator.file.target_path.text`** :   t
     : 2975 - 71: **`threat.indicator.file.type`** :   File type (fi
     : 2976 - 13: type: keyword
     : 2977 - 13: example: file
     : 2978 - 101: **`threat.indicator.file.uid`** :   The user ID (U
     : 2979 - 13: type: keyword
     : 2980 - 13: example: 1001
     : 2981 - 240: **`threat.indicator.file.x509.alternative_names`**
     : 2982 - 13: type: keyword
     : 2983 - 21: example: *.elastic.co
     : 2984 - 114: **`threat.indicator.file.x509.issuer.common_name`*
     : 2985 - 13: type: keyword
     : 2986 - 46: example: Example SHA2 High Assurance Server CA
     : 2987 - 75: **`threat.indicator.file.x509.issuer.country`** : 
     : 2988 - 13: type: keyword
     : 2989 - 11: example: US
     : 2990 - 120: **`threat.indicator.file.x509.issuer.distinguished
     : 2991 - 13: type: keyword
     : 2992 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 2993 - 79: **`threat.indicator.file.x509.issuer.locality`** :
     : 2994 - 13: type: keyword
     : 2995 - 22: example: Mountain View
     : 2996 - 116: **`threat.indicator.file.x509.issuer.organization`
     : 2997 - 13: type: keyword
     : 2998 - 20: example: Example Inc
     : 2999 - 131: **`threat.indicator.file.x509.issuer.organizationa
     : 3000 - 13: type: keyword
     : 3001 - 24: example: www.example.com
     : 3002 - 107: **`threat.indicator.file.x509.issuer.state_or_prov
     : 3003 - 13: type: keyword
     : 3004 - 19: example: California
     : 3005 - 107: **`threat.indicator.file.x509.not_after`** :   Tim
     : 3006 - 10: type: date
     : 3007 - 34: example: 2020-07-16 03:15:39+00:00
     : 3008 - 104: **`threat.indicator.file.x509.not_before`** :   Ti
     : 3009 - 10: type: date
     : 3010 - 34: example: 2019-08-16 01:40:25+00:00
     : 3011 - 100: **`threat.indicator.file.x509.public_key_algorithm
     : 3012 - 13: type: keyword
     : 3013 - 12: example: RSA
     : 3014 - 140: **`threat.indicator.file.x509.public_key_curve`** 
     : 3015 - 13: type: keyword
     : 3016 - 17: example: nistp521
     : 3017 - 124: **`threat.indicator.file.x509.public_key_exponent`
     : 3018 - 10: type: long
     : 3019 - 14: example: 65537
     : 3020 - 21: Field is not indexed.
     : 3021 - 94: **`threat.indicator.file.x509.public_key_size`** :
     : 3022 - 10: type: long
     : 3023 - 13: example: 2048
     : 3024 - 220: **`threat.indicator.file.x509.serial_number`** :  
     : 3025 - 13: type: keyword
     : 3026 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 3027 - 243: **`threat.indicator.file.x509.signature_algorithm`
     : 3028 - 13: type: keyword
     : 3029 - 19: example: SHA256-RSA
     : 3030 - 94: **`threat.indicator.file.x509.subject.common_name`
     : 3031 - 13: type: keyword
     : 3032 - 34: example: shared.global.example.net
     : 3033 - 75: **`threat.indicator.file.x509.subject.country`** :
     : 3034 - 13: type: keyword
     : 3035 - 11: example: US
     : 3036 - 122: **`threat.indicator.file.x509.subject.distinguishe
     : 3037 - 13: type: keyword
     : 3038 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 3039 - 80: **`threat.indicator.file.x509.subject.locality`** 
     : 3040 - 13: type: keyword
     : 3041 - 22: example: San Francisco
     : 3042 - 95: **`threat.indicator.file.x509.subject.organization
     : 3043 - 13: type: keyword
     : 3044 - 22: example: Example, Inc.
     : 3045 - 110: **`threat.indicator.file.x509.subject.organization
     : 3046 - 13: type: keyword
     : 3047 - 108: **`threat.indicator.file.x509.subject.state_or_pro
     : 3048 - 13: type: keyword
     : 3049 - 19: example: California
     : 3050 - 75: **`threat.indicator.file.x509.version_number`** : 
     : 3051 - 13: type: keyword
     : 3052 - 10: example: 3
     : 3053 - 120: **`threat.indicator.first_seen`** :   The date and
     : 3054 - 10: type: date
     : 3055 - 33: example: 2020-11-05T17:25:47.000Z
     : 3056 - 51: **`threat.indicator.geo.city_name`** :   City name
     : 3057 - 13: type: keyword
     : 3058 - 17: example: Montreal
     : 3059 - 92: **`threat.indicator.geo.continent_code`** :   Two-
     : 3060 - 13: type: keyword
     : 3061 - 11: example: NA
     : 3062 - 68: **`threat.indicator.geo.continent_name`** :   Name
     : 3063 - 13: type: keyword
     : 3064 - 22: example: North America
     : 3065 - 65: **`threat.indicator.geo.country_iso_code`** :   Co
     : 3066 - 13: type: keyword
     : 3067 - 11: example: CA
     : 3068 - 57: **`threat.indicator.geo.country_name`** :   Countr
     : 3069 - 13: type: keyword
     : 3070 - 15: example: Canada
     : 3071 - 63: **`threat.indicator.geo.location`** :   Longitude 
     : 3072 - 15: type: geo_point
     : 3073 - 48: example: { "lon": -73.614830, "lat": 45.505918 }
     : 3074 - 279: **`threat.indicator.geo.name`** :   User-defined d
     : 3075 - 13: type: keyword
     : 3076 - 18: example: boston-dc
     : 3077 - 208: **`threat.indicator.geo.postal_code`** :   Postal 
     : 3078 - 13: type: keyword
     : 3079 - 14: example: 94040
     : 3080 - 63: **`threat.indicator.geo.region_iso_code`** :   Reg
     : 3081 - 13: type: keyword
     : 3082 - 14: example: CA-QC
     : 3083 - 55: **`threat.indicator.geo.region_name`** :   Region 
     : 3084 - 13: type: keyword
     : 3085 - 15: example: Quebec
     : 3086 - 99: **`threat.indicator.geo.timezone`** :   The time z
     : 3087 - 13: type: keyword
     : 3088 - 39: example: America/Argentina/Buenos_Aires
     : 3089 - 105: **`threat.indicator.ip`** :   Identifies a threat 
     : 3090 - 8: type: ip
     : 3091 - 16: example: 1.2.3.4
     : 3092 - 118: **`threat.indicator.last_seen`** :   The date and 
     : 3093 - 10: type: date
     : 3094 - 33: example: 2020-11-05T17:25:47.000Z
     : 3095 - 133: **`threat.indicator.marking.tlp`** :   Traffic Lig
     : 3096 - 13: type: keyword
     : 3097 - 14: example: WHITE
     : 3098 - 127: **`threat.indicator.modified_at`** :   The date an
     : 3099 - 10: type: date
     : 3100 - 33: example: 2020-11-05T17:25:47.000Z
     : 3101 - 107: **`threat.indicator.port`** :   Identifies a threa
     : 3102 - 10: type: long
     : 3103 - 12: example: 443
     : 3104 - 73: **`threat.indicator.provider`** :   The name of th
     : 3105 - 13: type: keyword
     : 3106 - 20: example: lrz_urlhaus
     : 3107 - 106: **`threat.indicator.reference`** :   Reference URL
     : 3108 - 13: type: keyword
     : 3109 - 53: example: https://system.example.com/indicator/0001
     : 3110 - 323: **`threat.indicator.registry.data.bytes`** :   Ori
     : 3111 - 13: type: keyword
     : 3112 - 37: example: ZQBuAC0AVQBTAAAAZQBuAAAAAAA=
     : 3113 - 447: **`threat.indicator.registry.data.strings`** :   C
     : 3114 - 14: type: wildcard
     : 3115 - 41: example: ["C:\rta\red_ttp\bin\myapp.exe"]
     : 3116 - 90: **`threat.indicator.registry.data.type`** :   Stan
     : 3117 - 13: type: keyword
     : 3118 - 15: example: REG_SZ
     : 3119 - 71: **`threat.indicator.registry.hive`** :   Abbreviat
     : 3120 - 13: type: keyword
     : 3121 - 13: example: HKLM
     : 3122 - 67: **`threat.indicator.registry.key`** :   Hive-relat
     : 3123 - 13: type: keyword
     : 3124 - 94: example: SOFTWARE\Microsoft\Windows NT\CurrentVers
     : 3125 - 81: **`threat.indicator.registry.path`** :   Full path
     : 3126 - 13: type: keyword
     : 3127 - 108: example: HKLM\SOFTWARE\Microsoft\Windows NT\Curren
     : 3128 - 68: **`threat.indicator.registry.value`** :   Name of 
     : 3129 - 13: type: keyword
     : 3130 - 17: example: Debugger
     : 3131 - 114: **`threat.indicator.scanner_stats`** :   Count of 
     : 3132 - 10: type: long
     : 3133 - 10: example: 4
     : 3134 - 108: **`threat.indicator.sightings`** :   Number of tim
     : 3135 - 10: type: long
     : 3136 - 11: example: 20
     : 3137 - 328: **`threat.indicator.type`** :   Type of indicator 
     : 3138 - 13: type: keyword
     : 3139 - 18: example: ipv4-addr
     : 3140 - 385: **`threat.indicator.url.domain`** :   Domain of th
     : 3141 - 13: type: keyword
     : 3142 - 23: example: www.elastic.co
     : 3143 - 441: **`threat.indicator.url.extension`** :   The field
     : 3144 - 13: type: keyword
     : 3145 - 12: example: png
     : 3146 - 126: **`threat.indicator.url.fragment`** :   Portion of
     : 3147 - 13: type: keyword
     : 3148 - 186: **`threat.indicator.url.full`** :   If full URLs a
     : 3149 - 14: type: wildcard
     : 3150 - 62: example: https://www.elastic.co:443/search?q=elast
     : 3151 - 62: **`threat.indicator.url.full.text`** :   type: mat
     : 3152 - 308: **`threat.indicator.url.original`** :   Unmodified
     : 3153 - 14: type: wildcard
     : 3154 - 89: example: https://www.elastic.co:443/search?q=elast
     : 3155 - 66: **`threat.indicator.url.original.text`** :   type:
     : 3156 - 64: **`threat.indicator.url.password`** :   Password o
     : 3157 - 13: type: keyword
     : 3158 - 75: **`threat.indicator.url.path`** :   Path of the re
     : 3159 - 14: type: wildcard
     : 3160 - 69: **`threat.indicator.url.port`** :   Port of the re
     : 3161 - 10: type: long
     : 3162 - 12: example: 443
     : 3163 - 14: format: string
     : 3164 - 365: **`threat.indicator.url.query`** :   The query fie
     : 3165 - 13: type: keyword
     : 3166 - 402: **`threat.indicator.url.registered_domain`** :   T
     : 3167 - 13: type: keyword
     : 3168 - 20: example: example.com
     : 3169 - 118: **`threat.indicator.url.scheme`** :   Scheme of th
     : 3170 - 13: type: keyword
     : 3171 - 14: example: https
     : 3172 - 571: **`threat.indicator.url.subdomain`** :   The subdo
     : 3173 - 13: type: keyword
     : 3174 - 13: example: east
     : 3175 - 438: **`threat.indicator.url.top_level_domain`** :   Th
     : 3176 - 13: type: keyword
     : 3177 - 14: example: co.uk
     : 3178 - 64: **`threat.indicator.url.username`** :   Username o
     : 3179 - 13: type: keyword
     : 3180 - 235: **`threat.indicator.x509.alternative_names`** :   
     : 3181 - 13: type: keyword
     : 3182 - 21: example: *.elastic.co
     : 3183 - 109: **`threat.indicator.x509.issuer.common_name`** :  
     : 3184 - 13: type: keyword
     : 3185 - 46: example: Example SHA2 High Assurance Server CA
     : 3186 - 70: **`threat.indicator.x509.issuer.country`** :   Lis
     : 3187 - 13: type: keyword
     : 3188 - 11: example: US
     : 3189 - 115: **`threat.indicator.x509.issuer.distinguished_name
     : 3190 - 13: type: keyword
     : 3191 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 3192 - 74: **`threat.indicator.x509.issuer.locality`** :   Li
     : 3193 - 13: type: keyword
     : 3194 - 22: example: Mountain View
     : 3195 - 111: **`threat.indicator.x509.issuer.organization`** : 
     : 3196 - 13: type: keyword
     : 3197 - 20: example: Example Inc
     : 3198 - 126: **`threat.indicator.x509.issuer.organizational_uni
     : 3199 - 13: type: keyword
     : 3200 - 24: example: www.example.com
     : 3201 - 102: **`threat.indicator.x509.issuer.state_or_province`
     : 3202 - 13: type: keyword
     : 3203 - 19: example: California
     : 3204 - 102: **`threat.indicator.x509.not_after`** :   Time at 
     : 3205 - 10: type: date
     : 3206 - 34: example: 2020-07-16 03:15:39+00:00
     : 3207 - 99: **`threat.indicator.x509.not_before`** :   Time at
     : 3208 - 10: type: date
     : 3209 - 34: example: 2019-08-16 01:40:25+00:00
     : 3210 - 95: **`threat.indicator.x509.public_key_algorithm`** :
     : 3211 - 13: type: keyword
     : 3212 - 12: example: RSA
     : 3213 - 135: **`threat.indicator.x509.public_key_curve`** :   T
     : 3214 - 13: type: keyword
     : 3215 - 17: example: nistp521
     : 3216 - 119: **`threat.indicator.x509.public_key_exponent`** : 
     : 3217 - 10: type: long
     : 3218 - 14: example: 65537
     : 3219 - 21: Field is not indexed.
     : 3220 - 89: **`threat.indicator.x509.public_key_size`** :   Th
     : 3221 - 10: type: long
     : 3222 - 13: example: 2048
     : 3223 - 215: **`threat.indicator.x509.serial_number`** :   Uniq
     : 3224 - 13: type: keyword
     : 3225 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 3226 - 238: **`threat.indicator.x509.signature_algorithm`** : 
     : 3227 - 13: type: keyword
     : 3228 - 19: example: SHA256-RSA
     : 3229 - 89: **`threat.indicator.x509.subject.common_name`** : 
     : 3230 - 13: type: keyword
     : 3231 - 34: example: shared.global.example.net
     : 3232 - 70: **`threat.indicator.x509.subject.country`** :   Li
     : 3233 - 13: type: keyword
     : 3234 - 11: example: US
     : 3235 - 117: **`threat.indicator.x509.subject.distinguished_nam
     : 3236 - 13: type: keyword
     : 3237 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 3238 - 75: **`threat.indicator.x509.subject.locality`** :   L
     : 3239 - 13: type: keyword
     : 3240 - 22: example: San Francisco
     : 3241 - 90: **`threat.indicator.x509.subject.organization`** :
     : 3242 - 13: type: keyword
     : 3243 - 22: example: Example, Inc.
     : 3244 - 105: **`threat.indicator.x509.subject.organizational_un
     : 3245 - 13: type: keyword
     : 3246 - 103: **`threat.indicator.x509.subject.state_or_province
     : 3247 - 13: type: keyword
     : 3248 - 19: example: California
     : 3249 - 70: **`threat.indicator.x509.version_number`** :   Ver
     : 3250 - 13: type: keyword
     : 3251 - 10: example: 3
     : 3252 - 243: **`threat.software.alias`** :   The alias(es) of t
     : 3253 - 13: type: keyword
     : 3254 - 22: example: [ "X-Agent" ]
     : 3255 - 190: **`threat.software.id`** :   The id of the softwar
     : 3256 - 13: type: keyword
     : 3257 - 14: example: S0552
     : 3258 - 196: **`threat.software.name`** :   The name of the sof
     : 3259 - 13: type: keyword
     : 3260 - 15: example: AdFind
     : 3261 - 250: **`threat.software.platforms`** :   The platforms 
     : 3262 - 67: While not required, you can use a MITRE ATT&CK® so
     : 3263 - 13: type: keyword
     : 3264 - 22: example: [ "Windows" ]
     : 3265 - 219: **`threat.software.reference`** :   The reference 
     : 3266 - 13: type: keyword
     : 3267 - 49: example: https://attack.mitre.org/software/S0552/
     : 3268 - 165: **`threat.software.type`** :   The type of softwar
     : 3269 - 70: ``` While not required, you can use a MITRE ATT&CK
     : 3270 - 13: type: keyword
     : 3271 - 13: example: Tool
     : 3272 - 161: **`threat.tactic.id`** :   The id of tactic used b
     : 3273 - 13: type: keyword
     : 3274 - 15: example: TA0002
     : 3275 - 173: **`threat.tactic.name`** :   Name of the type of t
     : 3276 - 13: type: keyword
     : 3277 - 18: example: Execution
     : 3278 - 179: **`threat.tactic.reference`** :   The reference ur
     : 3279 - 13: type: keyword
     : 3280 - 49: example: https://attack.mitre.org/tactics/TA0002/
     : 3281 - 172: **`threat.technique.id`** :   The id of technique 
     : 3282 - 13: type: keyword
     : 3283 - 14: example: T1059
     : 3284 - 176: **`threat.technique.name`** :   The name of techni
     : 3285 - 13: type: keyword
     : 3286 - 42: example: Command and Scripting Interpreter
     : 3287 - 58: **`threat.technique.name.text`** :   type: match_o
     : 3288 - 190: **`threat.technique.reference`** :   The reference
     : 3289 - 13: type: keyword
     : 3290 - 51: example: https://attack.mitre.org/techniques/T1059
     : 3291 - 200: **`threat.technique.subtechnique.id`** :   The ful
     : 3292 - 13: type: keyword
     : 3293 - 18: example: T1059.001
     : 3294 - 199: **`threat.technique.subtechnique.name`** :   The n
     : 3295 - 13: type: keyword
     : 3296 - 19: example: PowerShell
     : 3297 - 71: **`threat.technique.subtechnique.name.text`** :   
     : 3298 - 213: **`threat.technique.subtechnique.reference`** :   
     : 3299 - 13: type: keyword
     : 3300 - 55: example: https://attack.mitre.org/techniques/T1059
   : 3301 - 14483: ## tls [_tls]  Fields related to a TLS connection.
     : 3302 - 13: ## tls [_tls]
     : 3303 - 164: Fields related to a TLS connection. These fields f
     : 3304 - 85: **`tls.cipher`** :   String indicating the cipher 
     : 3305 - 13: type: keyword
     : 3306 - 46: example: TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
     : 3307 - 199: **`tls.client.certificate`** :   PEM-encoded stand
     : 3308 - 13: type: keyword
     : 3309 - 14: example: MII…​
     : 3310 - 252: **`tls.client.certificate_chain`** :   Array of PE
     : 3311 - 13: type: keyword
     : 3312 - 27: example: ["MII…​", "MII…​"]
     : 3313 - 228: **`tls.client.hash.md5`** :   Certificate fingerpr
     : 3314 - 13: type: keyword
     : 3315 - 41: example: 0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC
     : 3316 - 230: **`tls.client.hash.sha1`** :   Certificate fingerp
     : 3317 - 13: type: keyword
     : 3318 - 49: example: 9E393D93138888D288266C2D915214D1D1CCEB2A
     : 3319 - 234: **`tls.client.hash.sha256`** :   Certificate finge
     : 3320 - 13: type: keyword
     : 3321 - 73: example: 0687F666A054EF17A08E2F2162EAB4CBC0D265E1D
     : 3322 - 121: **`tls.client.issuer`** :   Distinguished name of 
     : 3323 - 13: type: keyword
     : 3324 - 71: example: CN=Example Root CA, OU=Infrastructure Tea
     : 3325 - 103: **`tls.client.ja3`** :   A hash that identifies cl
     : 3326 - 13: type: keyword
     : 3327 - 41: example: d4e5b18d6b55c71272893221c96ba240
     : 3328 - 106: **`tls.client.not_after`** :   Date/Time indicatin
     : 3329 - 10: type: date
     : 3330 - 33: example: 2021-01-01T00:00:00.000Z
     : 3331 - 103: **`tls.client.not_before`** :   Date/Time indicati
     : 3332 - 10: type: date
     : 3333 - 33: example: 1970-01-01T00:00:00.000Z
     : 3334 - 215: **`tls.client.server_name`** :   Also called an SN
     : 3335 - 13: type: keyword
     : 3336 - 23: example: www.elastic.co
     : 3337 - 108: **`tls.client.subject`** :   Distinguished name of
     : 3338 - 13: type: keyword
     : 3339 - 63: example: CN=myclient, OU=Documentation Team, DC=ex
     : 3340 - 102: **`tls.client.supported_ciphers`** :   Array of ci
     : 3341 - 13: type: keyword
     : 3342 - 99: example: ["TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
     : 3343 - 229: **`tls.client.x509.alternative_names`** :   List o
     : 3344 - 13: type: keyword
     : 3345 - 21: example: *.elastic.co
     : 3346 - 103: **`tls.client.x509.issuer.common_name`** :   List 
     : 3347 - 13: type: keyword
     : 3348 - 46: example: Example SHA2 High Assurance Server CA
     : 3349 - 64: **`tls.client.x509.issuer.country`** :   List of c
     : 3350 - 13: type: keyword
     : 3351 - 11: example: US
     : 3352 - 109: **`tls.client.x509.issuer.distinguished_name`** : 
     : 3353 - 13: type: keyword
     : 3354 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 3355 - 68: **`tls.client.x509.issuer.locality`** :   List of 
     : 3356 - 13: type: keyword
     : 3357 - 22: example: Mountain View
     : 3358 - 105: **`tls.client.x509.issuer.organization`** :   List
     : 3359 - 13: type: keyword
     : 3360 - 20: example: Example Inc
     : 3361 - 120: **`tls.client.x509.issuer.organizational_unit`** :
     : 3362 - 13: type: keyword
     : 3363 - 24: example: www.example.com
     : 3364 - 96: **`tls.client.x509.issuer.state_or_province`** :  
     : 3365 - 13: type: keyword
     : 3366 - 19: example: California
     : 3367 - 96: **`tls.client.x509.not_after`** :   Time at which 
     : 3368 - 10: type: date
     : 3369 - 34: example: 2020-07-16 03:15:39+00:00
     : 3370 - 93: **`tls.client.x509.not_before`** :   Time at which
     : 3371 - 10: type: date
     : 3372 - 34: example: 2019-08-16 01:40:25+00:00
     : 3373 - 89: **`tls.client.x509.public_key_algorithm`** :   Alg
     : 3374 - 13: type: keyword
     : 3375 - 12: example: RSA
     : 3376 - 129: **`tls.client.x509.public_key_curve`** :   The cur
     : 3377 - 13: type: keyword
     : 3378 - 17: example: nistp521
     : 3379 - 113: **`tls.client.x509.public_key_exponent`** :   Expo
     : 3380 - 10: type: long
     : 3381 - 14: example: 65537
     : 3382 - 21: Field is not indexed.
     : 3383 - 83: **`tls.client.x509.public_key_size`** :   The size
     : 3384 - 10: type: long
     : 3385 - 13: example: 2048
     : 3386 - 209: **`tls.client.x509.serial_number`** :   Unique ser
     : 3387 - 13: type: keyword
     : 3388 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 3389 - 232: **`tls.client.x509.signature_algorithm`** :   Iden
     : 3390 - 13: type: keyword
     : 3391 - 19: example: SHA256-RSA
     : 3392 - 83: **`tls.client.x509.subject.common_name`** :   List
     : 3393 - 13: type: keyword
     : 3394 - 34: example: shared.global.example.net
     : 3395 - 64: **`tls.client.x509.subject.country`** :   List of 
     : 3396 - 13: type: keyword
     : 3397 - 11: example: US
     : 3398 - 111: **`tls.client.x509.subject.distinguished_name`** :
     : 3399 - 13: type: keyword
     : 3400 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 3401 - 69: **`tls.client.x509.subject.locality`** :   List of
     : 3402 - 13: type: keyword
     : 3403 - 22: example: San Francisco
     : 3404 - 84: **`tls.client.x509.subject.organization`** :   Lis
     : 3405 - 13: type: keyword
     : 3406 - 22: example: Example, Inc.
     : 3407 - 99: **`tls.client.x509.subject.organizational_unit`** 
     : 3408 - 13: type: keyword
     : 3409 - 97: **`tls.client.x509.subject.state_or_province`** : 
     : 3410 - 13: type: keyword
     : 3411 - 19: example: California
     : 3412 - 64: **`tls.client.x509.version_number`** :   Version o
     : 3413 - 13: type: keyword
     : 3414 - 10: example: 3
     : 3415 - 91: **`tls.curve`** :   String indicating the curve us
     : 3416 - 13: type: keyword
     : 3417 - 18: example: secp256r1
     : 3418 - 128: **`tls.established`** :   Boolean flag indicating 
     : 3419 - 13: type: boolean
     : 3420 - 256: **`tls.next_protocol`** :   String indicating the 
     : 3421 - 13: type: keyword
     : 3422 - 17: example: http/1.1
     : 3423 - 114: **`tls.resumed`** :   Boolean flag indicating if t
     : 3424 - 13: type: boolean
     : 3425 - 199: **`tls.server.certificate`** :   PEM-encoded stand
     : 3426 - 13: type: keyword
     : 3427 - 14: example: MII…​
     : 3428 - 252: **`tls.server.certificate_chain`** :   Array of PE
     : 3429 - 13: type: keyword
     : 3430 - 27: example: ["MII…​", "MII…​"]
     : 3431 - 228: **`tls.server.hash.md5`** :   Certificate fingerpr
     : 3432 - 13: type: keyword
     : 3433 - 41: example: 0F76C7F2C55BFD7D8E8B8F4BFBF0C9EC
     : 3434 - 230: **`tls.server.hash.sha1`** :   Certificate fingerp
     : 3435 - 13: type: keyword
     : 3436 - 49: example: 9E393D93138888D288266C2D915214D1D1CCEB2A
     : 3437 - 234: **`tls.server.hash.sha256`** :   Certificate finge
     : 3438 - 13: type: keyword
     : 3439 - 73: example: 0687F666A054EF17A08E2F2162EAB4CBC0D265E1D
     : 3440 - 99: **`tls.server.issuer`** :   Subject of the issuer 
     : 3441 - 13: type: keyword
     : 3442 - 71: example: CN=Example Root CA, OU=Infrastructure Tea
     : 3443 - 104: **`tls.server.ja3s`** :   A hash that identifies s
     : 3444 - 13: type: keyword
     : 3445 - 41: example: 394441ab65754e2207b1e1b457b3641d
     : 3446 - 106: **`tls.server.not_after`** :   Timestamp indicatin
     : 3447 - 10: type: date
     : 3448 - 33: example: 2021-01-01T00:00:00.000Z
     : 3449 - 103: **`tls.server.not_before`** :   Timestamp indicati
     : 3450 - 10: type: date
     : 3451 - 33: example: 1970-01-01T00:00:00.000Z
     : 3452 - 86: **`tls.server.subject`** :   Subject of the x.509 
     : 3453 - 13: type: keyword
     : 3454 - 71: example: CN=www.example.com, OU=Infrastructure Tea
     : 3455 - 229: **`tls.server.x509.alternative_names`** :   List o
     : 3456 - 13: type: keyword
     : 3457 - 21: example: *.elastic.co
     : 3458 - 103: **`tls.server.x509.issuer.common_name`** :   List 
     : 3459 - 13: type: keyword
     : 3460 - 46: example: Example SHA2 High Assurance Server CA
     : 3461 - 64: **`tls.server.x509.issuer.country`** :   List of c
     : 3462 - 13: type: keyword
     : 3463 - 11: example: US
     : 3464 - 109: **`tls.server.x509.issuer.distinguished_name`** : 
     : 3465 - 13: type: keyword
     : 3466 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 3467 - 68: **`tls.server.x509.issuer.locality`** :   List of 
     : 3468 - 13: type: keyword
     : 3469 - 22: example: Mountain View
     : 3470 - 105: **`tls.server.x509.issuer.organization`** :   List
     : 3471 - 13: type: keyword
     : 3472 - 20: example: Example Inc
     : 3473 - 120: **`tls.server.x509.issuer.organizational_unit`** :
     : 3474 - 13: type: keyword
     : 3475 - 24: example: www.example.com
     : 3476 - 96: **`tls.server.x509.issuer.state_or_province`** :  
     : 3477 - 13: type: keyword
     : 3478 - 19: example: California
     : 3479 - 96: **`tls.server.x509.not_after`** :   Time at which 
     : 3480 - 10: type: date
     : 3481 - 34: example: 2020-07-16 03:15:39+00:00
     : 3482 - 93: **`tls.server.x509.not_before`** :   Time at which
     : 3483 - 10: type: date
     : 3484 - 34: example: 2019-08-16 01:40:25+00:00
     : 3485 - 89: **`tls.server.x509.public_key_algorithm`** :   Alg
     : 3486 - 13: type: keyword
     : 3487 - 12: example: RSA
     : 3488 - 129: **`tls.server.x509.public_key_curve`** :   The cur
     : 3489 - 13: type: keyword
     : 3490 - 17: example: nistp521
     : 3491 - 113: **`tls.server.x509.public_key_exponent`** :   Expo
     : 3492 - 10: type: long
     : 3493 - 14: example: 65537
     : 3494 - 21: Field is not indexed.
     : 3495 - 83: **`tls.server.x509.public_key_size`** :   The size
     : 3496 - 10: type: long
     : 3497 - 13: example: 2048
     : 3498 - 209: **`tls.server.x509.serial_number`** :   Unique ser
     : 3499 - 13: type: keyword
     : 3500 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 3501 - 232: **`tls.server.x509.signature_algorithm`** :   Iden
     : 3502 - 13: type: keyword
     : 3503 - 19: example: SHA256-RSA
     : 3504 - 83: **`tls.server.x509.subject.common_name`** :   List
     : 3505 - 13: type: keyword
     : 3506 - 34: example: shared.global.example.net
     : 3507 - 64: **`tls.server.x509.subject.country`** :   List of 
     : 3508 - 13: type: keyword
     : 3509 - 11: example: US
     : 3510 - 111: **`tls.server.x509.subject.distinguished_name`** :
     : 3511 - 13: type: keyword
     : 3512 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 3513 - 69: **`tls.server.x509.subject.locality`** :   List of
     : 3514 - 13: type: keyword
     : 3515 - 22: example: San Francisco
     : 3516 - 84: **`tls.server.x509.subject.organization`** :   Lis
     : 3517 - 13: type: keyword
     : 3518 - 22: example: Example, Inc.
     : 3519 - 99: **`tls.server.x509.subject.organizational_unit`** 
     : 3520 - 13: type: keyword
     : 3521 - 97: **`tls.server.x509.subject.state_or_province`** : 
     : 3522 - 13: type: keyword
     : 3523 - 19: example: California
     : 3524 - 64: **`tls.server.x509.version_number`** :   Version o
     : 3525 - 13: type: keyword
     : 3526 - 10: example: 3
     : 3527 - 82: **`tls.version`** :   Numeric part of the version 
     : 3528 - 13: type: keyword
     : 3529 - 12: example: 1.2
     : 3530 - 94: **`tls.version_protocol`** :   Normalized lowercas
     : 3531 - 13: type: keyword
     : 3532 - 12: example: tls
     : 3533 - 190: **`span.id`** :   Unique identifier of the span wi
     : 3534 - 13: type: keyword
     : 3535 - 25: example: 3ff9a8981b7ccd5a
     : 3536 - 195: **`trace.id`** :   Unique identifier of the trace.
     : 3537 - 13: type: keyword
     : 3538 - 41: example: 4bf92f3577b34da6a3ce929d0e0e4736
     : 3539 - 193: **`transaction.id`** :   Unique identifier of the 
     : 3540 - 13: type: keyword
     : 3541 - 25: example: 00f067aa0ba902b7
   : 3542 - 4143: ## url [_url]  URL fields provide support for comp
     : 3543 - 13: ## url [_url]
     : 3544 - 125: URL fields provide support for complete or partial
     : 3545 - 368: **`url.domain`** :   Domain of the url, such as "w
     : 3546 - 13: type: keyword
     : 3547 - 23: example: www.elastic.co
     : 3548 - 424: **`url.extension`** :   The field contains the fil
     : 3549 - 13: type: keyword
     : 3550 - 12: example: png
     : 3551 - 109: **`url.fragment`** :   Portion of the url after th
     : 3552 - 13: type: keyword
     : 3553 - 169: **`url.full`** :   If full URLs are important to y
     : 3554 - 14: type: wildcard
     : 3555 - 62: example: https://www.elastic.co:443/search?q=elast
     : 3556 - 45: **`url.full.text`** :   type: match_only_text
     : 3557 - 291: **`url.original`** :   Unmodified original url as 
     : 3558 - 14: type: wildcard
     : 3559 - 89: example: https://www.elastic.co:443/search?q=elast
     : 3560 - 49: **`url.original.text`** :   type: match_only_text
     : 3561 - 47: **`url.password`** :   Password of the request.
     : 3562 - 13: type: keyword
     : 3563 - 58: **`url.path`** :   Path of the request, such as "/
     : 3564 - 14: type: wildcard
     : 3565 - 52: **`url.port`** :   Port of the request, such as 44
     : 3566 - 10: type: long
     : 3567 - 12: example: 443
     : 3568 - 14: format: string
     : 3569 - 348: **`url.query`** :   The query field describes the 
     : 3570 - 13: type: keyword
     : 3571 - 385: **`url.registered_domain`** :   The highest regist
     : 3572 - 13: type: keyword
     : 3573 - 20: example: example.com
     : 3574 - 101: **`url.scheme`** :   Scheme of the request, such a
     : 3575 - 13: type: keyword
     : 3576 - 14: example: https
     : 3577 - 554: **`url.subdomain`** :   The subdomain portion of a
     : 3578 - 13: type: keyword
     : 3579 - 13: example: east
     : 3580 - 421: **`url.top_level_domain`** :   The effective top l
     : 3581 - 13: type: keyword
     : 3582 - 14: example: co.uk
     : 3583 - 47: **`url.username`** :   Username of the request.
     : 3584 - 13: type: keyword
   : 3585 - 5476: ## user [_user_2]  The user fields describe inform
     : 3586 - 17: ## user [_user_2]
     : 3587 - 205: The user fields describe information about the use
     : 3588 - 130: **`user.changes.domain`** :   Name of the director
     : 3589 - 13: type: keyword
     : 3590 - 48: **`user.changes.email`** :   User email address.
     : 3591 - 13: type: keyword
     : 3592 - 64: **`user.changes.full_name`** :   User’s full name,
     : 3593 - 13: type: keyword
     : 3594 - 24: example: Albert Einstein
     : 3595 - 59: **`user.changes.full_name.text`** :   type: match_
     : 3596 - 137: **`user.changes.group.domain`** :   Name of the di
     : 3597 - 13: type: keyword
     : 3598 - 87: **`user.changes.group.id`** :   Unique identifier 
     : 3599 - 13: type: keyword
     : 3600 - 52: **`user.changes.group.name`** :   Name of the grou
     : 3601 - 13: type: keyword
     : 3602 - 188: **`user.changes.hash`** :   Unique user hash to co
     : 3603 - 13: type: keyword
     : 3604 - 56: **`user.changes.id`** :   Unique identifier of the
     : 3605 - 13: type: keyword
     : 3606 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 3607 - 60: **`user.changes.name`** :   Short name or login of
     : 3608 - 13: type: keyword
     : 3609 - 19: example: a.einstein
     : 3610 - 54: **`user.changes.name.text`** :   type: match_only_
     : 3611 - 74: **`user.changes.roles`** :   Array of user roles a
     : 3612 - 13: type: keyword
     : 3613 - 43: example: ["kibana_admin", "reporting_user"]
     : 3614 - 122: **`user.domain`** :   Name of the directory the us
     : 3615 - 13: type: keyword
     : 3616 - 132: **`user.effective.domain`** :   Name of the direct
     : 3617 - 13: type: keyword
     : 3618 - 50: **`user.effective.email`** :   User email address.
     : 3619 - 13: type: keyword
     : 3620 - 66: **`user.effective.full_name`** :   User’s full nam
     : 3621 - 13: type: keyword
     : 3622 - 24: example: Albert Einstein
     : 3623 - 61: **`user.effective.full_name.text`** :   type: matc
     : 3624 - 139: **`user.effective.group.domain`** :   Name of the 
     : 3625 - 13: type: keyword
     : 3626 - 89: **`user.effective.group.id`** :   Unique identifie
     : 3627 - 13: type: keyword
     : 3628 - 54: **`user.effective.group.name`** :   Name of the gr
     : 3629 - 13: type: keyword
     : 3630 - 190: **`user.effective.hash`** :   Unique user hash to 
     : 3631 - 13: type: keyword
     : 3632 - 58: **`user.effective.id`** :   Unique identifier of t
     : 3633 - 13: type: keyword
     : 3634 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 3635 - 62: **`user.effective.name`** :   Short name or login 
     : 3636 - 13: type: keyword
     : 3637 - 19: example: a.einstein
     : 3638 - 56: **`user.effective.name.text`** :   type: match_onl
     : 3639 - 76: **`user.effective.roles`** :   Array of user roles
     : 3640 - 13: type: keyword
     : 3641 - 43: example: ["kibana_admin", "reporting_user"]
     : 3642 - 40: **`user.email`** :   User email address.
     : 3643 - 13: type: keyword
     : 3644 - 56: **`user.full_name`** :   User’s full name, if avai
     : 3645 - 13: type: keyword
     : 3646 - 24: example: Albert Einstein
     : 3647 - 51: **`user.full_name.text`** :   type: match_only_tex
     : 3648 - 129: **`user.group.domain`** :   Name of the directory 
     : 3649 - 13: type: keyword
     : 3650 - 79: **`user.group.id`** :   Unique identifier for the 
     : 3651 - 13: type: keyword
     : 3652 - 44: **`user.group.name`** :   Name of the group.
     : 3653 - 13: type: keyword
     : 3654 - 180: **`user.hash`** :   Unique user hash to correlate 
     : 3655 - 13: type: keyword
     : 3656 - 48: **`user.id`** :   Unique identifier of the user.
     : 3657 - 13: type: keyword
     : 3658 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 3659 - 52: **`user.name`** :   Short name or login of the use
     : 3660 - 13: type: keyword
     : 3661 - 19: example: a.einstein
     : 3662 - 46: **`user.name.text`** :   type: match_only_text
     : 3663 - 66: **`user.roles`** :   Array of user roles at the ti
     : 3664 - 13: type: keyword
     : 3665 - 43: example: ["kibana_admin", "reporting_user"]
     : 3666 - 129: **`user.target.domain`** :   Name of the directory
     : 3667 - 13: type: keyword
     : 3668 - 47: **`user.target.email`** :   User email address.
     : 3669 - 13: type: keyword
     : 3670 - 63: **`user.target.full_name`** :   User’s full name, 
     : 3671 - 13: type: keyword
     : 3672 - 24: example: Albert Einstein
     : 3673 - 58: **`user.target.full_name.text`** :   type: match_o
     : 3674 - 136: **`user.target.group.domain`** :   Name of the dir
     : 3675 - 13: type: keyword
     : 3676 - 86: **`user.target.group.id`** :   Unique identifier f
     : 3677 - 13: type: keyword
     : 3678 - 51: **`user.target.group.name`** :   Name of the group
     : 3679 - 13: type: keyword
     : 3680 - 187: **`user.target.hash`** :   Unique user hash to cor
     : 3681 - 13: type: keyword
     : 3682 - 55: **`user.target.id`** :   Unique identifier of the 
     : 3683 - 13: type: keyword
     : 3684 - 57: example: S-1-5-21-202424912787-2692429404-23519567
     : 3685 - 59: **`user.target.name`** :   Short name or login of 
     : 3686 - 13: type: keyword
     : 3687 - 19: example: a.einstein
     : 3688 - 53: **`user.target.name.text`** :   type: match_only_t
     : 3689 - 73: **`user.target.roles`** :   Array of user roles at
     : 3690 - 13: type: keyword
     : 3691 - 43: example: ["kibana_admin", "reporting_user"]
   : 3692 - 1936: ## user_agent [_user_agent]  The user_agent fields
     : 3693 - 27: ## user_agent [_user_agent]
     : 3694 - 140: The user_agent fields normally come from a browser
     : 3695 - 52: **`user_agent.device.name`** :   Name of the devic
     : 3696 - 13: type: keyword
     : 3697 - 15: example: iPhone
     : 3698 - 49: **`user_agent.name`** :   Name of the user agent.
     : 3699 - 13: type: keyword
     : 3700 - 15: example: Safari
     : 3701 - 57: **`user_agent.original`** :   Unparsed user_agent 
     : 3702 - 13: type: keyword
     : 3703 - 144: example: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 l
     : 3704 - 56: **`user_agent.original.text`** :   type: match_onl
     : 3705 - 84: **`user_agent.os.family`** :   OS family (such as 
     : 3706 - 13: type: keyword
     : 3707 - 15: example: debian
     : 3708 - 87: **`user_agent.os.full`** :   Operating system name
     : 3709 - 13: type: keyword
     : 3710 - 22: example: Mac OS Mojave
     : 3711 - 55: **`user_agent.os.full.text`** :   type: match_only
     : 3712 - 79: **`user_agent.os.kernel`** :   Operating system ke
     : 3713 - 13: type: keyword
     : 3714 - 26: example: 4.4.0-112-generic
     : 3715 - 72: **`user_agent.os.name`** :   Operating system name
     : 3716 - 13: type: keyword
     : 3717 - 17: example: Mac OS X
     : 3718 - 55: **`user_agent.os.name.text`** :   type: match_only
     : 3719 - 90: **`user_agent.os.platform`** :   Operating system 
     : 3720 - 13: type: keyword
     : 3721 - 15: example: darwin
     : 3722 - 376: **`user_agent.os.type`** :   Use the `os.type` fie
     : 3723 - 13: type: keyword
     : 3724 - 14: example: macos
     : 3725 - 73: **`user_agent.os.version`** :   Operating system v
     : 3726 - 13: type: keyword
     : 3727 - 16: example: 10.14.1
     : 3728 - 55: **`user_agent.version`** :   Version of the user a
     : 3729 - 13: type: keyword
     : 3730 - 13: example: 12.0
   : 3731 - 1178: ## vlan [_vlan]  The VLAN fields are used to ident
     : 3732 - 15: ## vlan [_vlan]
     : 3733 - 975: The VLAN fields are used to identify 802.1q tag(s)
     : 3734 - 54: **`vlan.id`** :   VLAN ID as reported by the obser
     : 3735 - 13: type: keyword
     : 3736 - 11: example: 10
     : 3737 - 67: **`vlan.name`** :   Optional VLAN name as reported
     : 3738 - 13: type: keyword
     : 3739 - 16: example: outside
   : 3740 - 3648: ## vulnerability [_vulnerability]  The vulnerabili
     : 3741 - 33: ## vulnerability [_vulnerability]
     : 3742 - 97: The vulnerability fields describe information abou
     : 3743 - 285: **`vulnerability.category`** :   The type of syste
     : 3744 - 13: type: keyword
     : 3745 - 21: example: ["Firewall"]
     : 3746 - 138: **`vulnerability.classification`** :   The classif
     : 3747 - 13: type: keyword
     : 3748 - 13: example: CVSS
     : 3749 - 195: **`vulnerability.description`** :   The descriptio
     : 3750 - 13: type: keyword
     : 3751 - 70: example: In macOS before 2.12.6, there is a vulner
     : 3752 - 62: **`vulnerability.description.text`** :   type: mat
     : 3753 - 132: **`vulnerability.enumeration`** :   The type of id
     : 3754 - 13: type: keyword
     : 3755 - 12: example: CVE
     : 3756 - 223: **`vulnerability.id`** :   The identification (ID)
     : 3757 - 13: type: keyword
     : 3758 - 23: example: CVE-2019-00001
     : 3759 - 141: **`vulnerability.reference`** :   A resource that 
     : 3760 - 13: type: keyword
     : 3761 - 69: example: https://cve.mitre.org/cgi-bin/cvename.cgi
     : 3762 - 75: **`vulnerability.report_id`** :   The report or sc
     : 3763 - 13: type: keyword
     : 3764 - 22: example: 20191018.0001
     : 3765 - 84: **`vulnerability.scanner.vendor`** :   The name of
     : 3766 - 13: type: keyword
     : 3767 - 16: example: Tenable
     : 3768 - 364: **`vulnerability.score.base`** :   Scores can rang
     : 3769 - 11: type: float
     : 3770 - 12: example: 5.5
     : 3771 - 308: **`vulnerability.score.environmental`** :   Scores
     : 3772 - 11: type: float
     : 3773 - 12: example: 5.5
     : 3774 - 262: **`vulnerability.score.temporal`** :   Scores can 
     : 3775 - 11: type: float
     : 3776 - 513: **`vulnerability.score.version`** :   The National
     : 3777 - 13: type: keyword
     : 3778 - 12: example: 2.0
     : 3779 - 194: **`vulnerability.severity`** :   The severity of t
     : 3780 - 13: type: keyword
     : 3781 - 17: example: Critical
   : 3782 - 4075: ## x509 [_x509]  This implements the common core f
     : 3783 - 15: ## x509 [_x509]
     : 3784 - 609: This implements the common core fields for x509 ce
     : 3785 - 218: **`x509.alternative_names`** :   List of subject a
     : 3786 - 13: type: keyword
     : 3787 - 21: example: *.elastic.co
     : 3788 - 92: **`x509.issuer.common_name`** :   List of common n
     : 3789 - 13: type: keyword
     : 3790 - 46: example: Example SHA2 High Assurance Server CA
     : 3791 - 53: **`x509.issuer.country`** :   List of country © co
     : 3792 - 13: type: keyword
     : 3793 - 11: example: US
     : 3794 - 98: **`x509.issuer.distinguished_name`** :   Distingui
     : 3795 - 13: type: keyword
     : 3796 - 90: example: C=US, O=Example Inc, OU=www.example.com, 
     : 3797 - 57: **`x509.issuer.locality`** :   List of locality na
     : 3798 - 13: type: keyword
     : 3799 - 22: example: Mountain View
     : 3800 - 94: **`x509.issuer.organization`** :   List of organiz
     : 3801 - 13: type: keyword
     : 3802 - 20: example: Example Inc
     : 3803 - 109: **`x509.issuer.organizational_unit`** :   List of 
     : 3804 - 13: type: keyword
     : 3805 - 24: example: www.example.com
     : 3806 - 85: **`x509.issuer.state_or_province`** :   List of st
     : 3807 - 13: type: keyword
     : 3808 - 19: example: California
     : 3809 - 85: **`x509.not_after`** :   Time at which the certifi
     : 3810 - 10: type: date
     : 3811 - 34: example: 2020-07-16 03:15:39+00:00
     : 3812 - 82: **`x509.not_before`** :   Time at which the certif
     : 3813 - 10: type: date
     : 3814 - 34: example: 2019-08-16 01:40:25+00:00
     : 3815 - 78: **`x509.public_key_algorithm`** :   Algorithm used
     : 3816 - 13: type: keyword
     : 3817 - 12: example: RSA
     : 3818 - 118: **`x509.public_key_curve`** :   The curve used by 
     : 3819 - 13: type: keyword
     : 3820 - 17: example: nistp521
     : 3821 - 102: **`x509.public_key_exponent`** :   Exponent used t
     : 3822 - 10: type: long
     : 3823 - 14: example: 65537
     : 3824 - 21: Field is not indexed.
     : 3825 - 72: **`x509.public_key_size`** :   The size of the pub
     : 3826 - 10: type: long
     : 3827 - 13: example: 2048
     : 3828 - 198: **`x509.serial_number`** :   Unique serial number 
     : 3829 - 13: type: keyword
     : 3830 - 33: example: 55FBB9C7DEBF09809D12CCAA
     : 3831 - 221: **`x509.signature_algorithm`** :   Identifier for 
     : 3832 - 13: type: keyword
     : 3833 - 19: example: SHA256-RSA
     : 3834 - 72: **`x509.subject.common_name`** :   List of common 
     : 3835 - 13: type: keyword
     : 3836 - 34: example: shared.global.example.net
     : 3837 - 53: **`x509.subject.country`** :   List of country © c
     : 3838 - 13: type: keyword
     : 3839 - 11: example: US
     : 3840 - 100: **`x509.subject.distinguished_name`** :   Distingu
     : 3841 - 13: type: keyword
     : 3842 - 92: example: C=US, ST=California, L=San Francisco, O=E
     : 3843 - 58: **`x509.subject.locality`** :   List of locality n
     : 3844 - 13: type: keyword
     : 3845 - 22: example: San Francisco
     : 3846 - 73: **`x509.subject.organization`** :   List of organi
     : 3847 - 13: type: keyword
     : 3848 - 22: example: Example, Inc.
     : 3849 - 88: **`x509.subject.organizational_unit`** :   List of
     : 3850 - 13: type: keyword
     : 3851 - 86: **`x509.subject.state_or_province`** :   List of s
     : 3852 - 13: type: keyword
     : 3853 - 19: example: California
     : 3854 - 53: **`x509.version_number`** :   Version of x509 form
     : 3855 - 13: type: keyword
     : 3856 - 10: example: 3