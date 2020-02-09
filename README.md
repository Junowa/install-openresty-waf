# nginx-waf

## Description

This role installs an open-spource waf based on nginx and modsecurity.

This roles implements the following features:
* Install openresty reverse proxy
* Install modsecurity
* Install crs-3.0 security rules set
* Configure modsecurity
* Add virtual hosts configurations (OPTIONAL)
* Add modsecurity exceptions


## Requirements


### Usage

Add the role to your **requirements.yml** file:
```
src: git@gitlab.thalesdigital.io:shared-infra/ansible-roles/openresty-waf.git
scm: git
name: waf
version: 0.1.0
```

The version parameter is up to you.


Install or update:
```
ansible-galaxy -r requirements.yml -p roles/
```

Your custom virtual hosts MAY be present in **vhosts_templates/** playbook folder as follows:
```
{{ playbook_dir }}/vhosts_templates/vhost_{{ item.tool }}.conf.j2
```

In order to apply your custom virtual hosts you need to define `custom_vhosts_config` variable in your playbook. Example:
```
custom_vhosts_config:
  - { "tool": "waf", "servername" : "waf-dev.thalesdigital.io", "certificate_directory" : "/etc/nginx/cert" }
```

The custom_vhosts_config object's attributes are:

* item.**tool**: An alias for your tool, used to address a filename in your `{{ playbook_dir }}/vhosts_templates`
* item.**servername**: Actual hostname (or wildcard) that will be used in destination vhost filename & configuration logic
* item.**certificate_directory**: Certificate directory :)

Your custom virtual hosts certificates MAY be present in **certs/** playbook folder as follows:   
```
{{ playbook_dir }}/certs/{{ servername }}.crt
{{ playbook_dir }}/certs/{{ servername }}.key.vault
```
Note1: The private key MUST be vaulted.  
Note2: The certifcate and the private key must be named in accordance to servername.

## Role Variables

  Global:
  * **owasp_rules_version**: OWASP Core Ruleset version (default: 3.0.0)
  * **ssl_nginx_directory**: path to store nginx certificates on remote side (default: /etc/ssl/nginx)
  * **cert_directory**: path to store nginx certificats in the local (default: "{{ playbook_dir }}/certs")
  * **modsecurity_allowed_http_methods**: Allowed HTTP Methods (default is: "GET HEAD POST OPTIONS")
  * **modsecurity_allowed_content_types**: Allowed request content types (default is: "application/x-www-form-urlencoded|multipart/form-data|text/xml|application/xml|application/x-amf|application/json|text/plain")
  * **modsecurity_excluded_rule_files**: List of `.conf` files to be excluded (disabled). By default: none.
  * **modsecurity_default_exception_file**: modsecurity exception filename (default: RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf)
  * **modsecurity_excluded_rule_ids**: List of ruleId to be excluded. By default: none.
  * **modsecurity_auditengine**: Configures the audit logging engine (default: RelevantOnly)
  * **modsecurity_auditlogformat**: Select the output format of the AuditLogs (default: JSON)
  * **modsdecurity_auditlogrelevantstatus**: Configures which response status code is to be considered relevant for the purpose of audit logging (default: "^(?:5|4(?!04))")

**IMPORTANT NOTE: to create modsecurity exceptions, prefer the usage of modsecurity_excluded_rule_ids (more restrictive).**

  * **openresty_version**: openresty version (default: 1.13.12-1~xenial)
  * **openresty_modsec_version**: the nginx version on which modsec has been compiled (default: )
  * **repository_path**: "https://artifactory.thalesdigital.io/artifactory/list/generic-public/coreauto/openresty-modsecurity"


## Dependencies

  * [gitlab-ci-images/ansible 0.0.2](https://gitlab.thalesdigital.io/shared-infra/gitlab-ci-images/ansible/tree/0.0.2)

  * [gitlab-ci-images/role-standards:latest](https://gitlab.thalesdigital.io/shared-infra/gitlab-ci-images/role-standards.git)

  * [ansible-roles/apt](https://gitlab.thalesdigital.io/shared-infra/ansible-roles/apt)


## Privilege escalation

  Yes.

## Examples

### Playbook

    ---

    - hosts: waf
      roles:
         - openresty-waf

### Define custom virtual hosts

By default, the role only performs installation and modsecurity default configuration.  
Optionnaly, you can add your own custom virtual hosts configurations by following these steps:
1. Create your virtual host template
2. Set your virtual host variables
3. Add your virtual host certificates (optionnal)

#### Example 1: add a backend

Create **vhosts_templates/** directory in the playbook folder.  
In this directory, create **vhost_waf_oss_default.conf.j2** with the following content:
```
# {{ ansible_managed }}

upstream {{ item.backend_name }} {
  zone {{ item.backend_name }} 64k;
  {% for backend in item.backends %}
  server {{ backend }};
  {% endfor %}
}

server {
  listen 443 ssl;
  server_name {{ item.servername }}.*;

  modsecurity {{ "on" if item.activate_modsecurity else "off" }};
  modsecurity_rules_file /etc/nginx/modsec/main.conf;

  ssl on;
  ssl_certificate {{ item.certificate_directory }}/{{ item.servername }}.crt;
  ssl_certificate_key {{ item.certificate_directory }}/{{ item.servername }}.key;

  access_log /var/log/nginx/access_https_{{ item.servername }}.log combined;
  error_log  /var/log/nginx/error_https_{{ item.servername }}.log;

  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

  location / {
    proxy_pass http://{{ item.backend_name }};
    proxy_set_header Host $http_host;
  }
}
```
To configure a backend with one server (for example: 192.168.100.1:8080), add to your host variables the following lines:
```
custom_vhosts_config:
  - servername: web1.waf
    tool: waf_oss_default
    backend_name: app1-cluster
    backends:
      - "192.168.100.1:8080"
    activate_modsecurity: true
    certificate_directory: /etc/ssl/nginx
```
To configure nginx certificates, create **vhosts_templates/** directory in the playbook folder.  
In this directory, add the certificates and private key files in accordance to the following naming convention :
* web1.waf.crt
* web1.waf.key.vault

Note: Use PEM format.

#### Example 2: add a redirection

Create in the **vhosts_templates/** directory a file named **vhost_httpredirect.conf.j2** with the following content:
```
server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name _;
        return 301 https://$host$request_uri;
}
```
Then, add to your host variables the following lines:
```
- servername: httpredirect
    tool: httpredirect
    activate_modsecurity: false
```

## Testing

```
$ git clone git@gitlab.thalesdigital.io:shared-infra/ansible-roles/openresty-waf.git
$ cd openresty-waf
$ molecule test
```

## License

SpiderLabs/ModSecurity is licensed under the Apache License 2.0.  
NGINX open-source is under a 2-clause BSD-like license (https://github.com/nginx/nginx/blob/master/docs/text/LICENSE).
Openresty is under MIT Licence (https://openresty.org/download/Copyright-and-Licenses-for-3rd-Party-Open-Source-Projects.pdf)

Additional information can be found at:
* https://openresty.org/en/
* https://github.com/nginx/nginx
* https://github.com/SpiderLabs/ModSecurity-nginx
* https://modsecurity.org/crs/

## Issue tracker URL

  [Issue tracker](https://gitlab.thalesdigital.io/shared-infra/ansible-roles/openresty-waf/issues)

## Contributing

  Add unit tests and examples for any new or changed functionality.

  1. Fork it
  2. Create your feature branch (git checkout -b my-new-feature)
  3. Commit your changes (git commit -am 'Add new feature')
  4. Push to the branch (git push origin my-new-feature)
  5. Make sure your branch is up to date w.r.t. forked project (see [Syncing a fork](https://help.github.com/articles/syncing-a-fork/)) and prepare your PR to have a clean history (see [Getting solid at Git rebase vs. merge](
  https://medium.com/@porteneuve/getting-solid-at-git-rebase-vs-merge-4fa1a48c53aa) and [Git Interactive Rebase, Squash, Amend and Other Ways of Rewriting History](https://robots.thoughtbot.com/git-interactive-rebase-squash-amend-rewriting-history))
  6. Create new Pull Request
