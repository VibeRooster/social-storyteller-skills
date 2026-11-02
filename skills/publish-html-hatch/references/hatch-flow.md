# Hatch flow reference

| Need | Tool | Notes |
|---|---|---|
| Who am I / paired? | `whoami` | Don't call mid-pairing |
| Pair a workspace | `get_pairing_code`, `poll_pairing` | Human approves the code; store the grant privately |
| Find existing site | `list`, `lookup` | Always before creating |
| Create site | `hatch` | `html` or `manifest`; `tier`; `preferredSlug`; `apex`. Returns hatch id + URL |
| Update files | `upload` | Manifest → presigned PUT URLs → `curl -T file URL` |
| Rename / domain / listing | `convert` | |
| Password | `auth` | |
| Guest link | `share` | Signed, expiring |
| Human review | `await_decision`, `poll_decision`, `continue_decision` | |
| Paid tier | `catalog`, `checkout`, `poll_checkout` | Explicit approval only |

Free-tier sites expire (default ~48h, configurable within limits). Check the server's tool schemas for current parameters.
