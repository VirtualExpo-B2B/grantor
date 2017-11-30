# vim: set sw=4

# convert meta-hosts to an array of MySQL hosts
# folx on ndev1 -> [172.16.130.%]
def get_hosts_from_meta(envid, meta_host):
  # FIXME
  return ["%"]


# convert MySQL host to meta
def get_meta_from_host(host):
  map = {
        "%": "any",
        "10.80.30.%": "folx",
        "10.80.31.%": "dblx",
        "10.80.32.%": "wklx",
        "10.80.34.%": "solx",
        "10.80.35.%": "ssolx",
        "10.80.36.%": "rplx",
        "10.80.41.%": "admlx",
        "10.80.50.%": "applx", # bilx
        "10.80.0.0/255.255.0.0": "veso",
        "10.80.%.%": "veso",
        "127.0.0.1":  "localhost",
        "172.16.10.%": "net-priv",
        "172.16.11.%": "net-adm",
        "172.16.200.%": "net-vpn",
        "172.16.100.%": "net-vpn",
        "172.16.30.%":  "velo30",
        "172.16.40.%":  "velo40",
        "172.16.50.%":  "velo50",
        "::1":          "localhost",
        "localhost":    "localhost",
        "172.16.130.%": "folx",
        "172.16.131.%": "dblx",
        "172.16.132.%": "wklx",
        "172.16.133.%": "bolx",
        "172.16.134.%": "ssolx",
        "172.16.135.%": "rplx",
        "172.16.140.%": "folx",
        "172.16.141.%": "dblx",
        "172.16.142.%": "wklx",
        "172.16.143.%": "bolx",
        "172.16.144.%": "ssolx",
        "172.16.145.%": "rplx",
      }

  if host in map:
    return map[host]
  else:
    return False
