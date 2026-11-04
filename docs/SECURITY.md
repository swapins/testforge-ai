# Security model

The MVP is designed for local, synthetic demonstrations.

- Accounts are bootstrapped from operator-supplied passwords and stored using
  PBKDF2-SHA256 hashes. Passwords and session tokens are never committed.
- Backend role checks protect developer and QA reviewer actions; frontend state
  is not an authorization boundary. Saritha S is the developer account and
  Swapin Vidya is the QA reviewer account.
- Generated cases begin as `draft`, must be submitted, and can only be decided
  by the authenticated QA reviewer. Approved revisions are immutable.
- Export is a fixed template renderer. User or model text cannot add imports,
  commands, URLs, or file paths.
- Execution is allowlisted to the bundled synthetic Maven demo and disabled by
  default. It accepts no user shell command and does not mount the Docker socket.

The MVP is not a production identity provider or hardened multi-tenant service.
Use HTTPS, secret management, a restricted execution worker, and a production
database before deployment beyond local authorized demonstrations.
