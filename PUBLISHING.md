# Survivor Runs 0.3.1 - publishing status

Requested target: https://github.com/Alexwatson-de/Survivor-runs and a separate
Vercel website for this browser game. Existing applications and deployments must
remain unchanged. No paid plan or billing upgrade is authorized or required by
this static-game design.

## Current state: prepared locally, NOT uploaded or deployed

- Added Git ignore rules for credentials, provider state, dependencies, caches,
  auto-save backups and generated release archives.
- Added a Vercel ignore file so Blender workshops, recordings, tests, archives and
  local credential/config files are not sent as deployment build inputs.
- Added a static Vite Vercel configuration: npm ci, npm run build, output dist,
  nosniff/referrer/frame headers and revalidation for game assets.
- No GitHub credential is saved in these files or Git configuration.
- No public site URL, remote commit or successful upload is claimed.
- Fresh local build and **all 132 unit/asset checks pass**. A credential-pattern
  scan of 347 candidate source/artwork files found no matching credentials, and
  no candidate file meets or exceeds 100 MiB. This is a local preflight, not a
  claim that a GitHub push or public acceptance test succeeded.
  [Preflight inventory](artifacts/publishing/preflight.json),
  [build log](artifacts/publishing/build.log), [tests](artifacts/publishing/tests.log).

## Network blocker

On the publishing attempt, HTTPS to api.github.com and github.com failed before
GitHub could validate the supplied authentication. The Vercel CLI's read-only
whoami/teams requests also failed with network-unreachable diagnostics. Ordinary
IPv4 checks did not resolve this. One unauthenticated curl request to the Vercel
API root succeeded, but authenticated CLI requests remained unavailable; that
alone is not evidence that deployment works or that an account is authenticated.

Restore normal connectivity to the official GitHub and Vercel endpoints before
retrying. Do not weaken TLS verification, change account billing, introduce a
third-party proxy or overwrite remote history to work around this blocker.

The supplied chat token should be revoked because it was shared in chat. Future
authentication should use a secure Git credential manager/CLI login rather than
committing a token, putting one in a remote URL, or uploading it with the game.
The failed network request does not establish whether that token is valid.

## Public-release confirmations received

On 2026-11-10 the owner explicitly selected **Personal use; redistribution rights
confirmed**, confirming both personal/non-commercial use and permission to publish
the current cowboy model/derivatives, including downloadable GLBs with the game.
These confirmations resolve the pending owner-authorization questions. No paid
plan upgrade is authorized. Network access and provider authentication still need
verification before the upload/deployment can complete.

The source GLB has no embedded license. Research identified the apparent original
publisher page, [GA Free_451_Rugged Cowboy - High Poly by Galaxy Abundant](https://sketchfab.com/3d-models/ga-free-451-rugged-cowboy-high-poly-7a8b66096bdd454ebc5aa99e6ff388ce),
but search extraction did not provide a verifiable applicable license. The direct
public API request also timed out from this host. This means permission remains
**not independently verified**; release now relies on the owner's explicit
redistribution-rights confirmation, not an invented publisher license.
The word Free in a model title is not itself a redistribution license.

The zombie models' embedded CC BY 4.0 metadata, credit links and modifications are
recorded in [asset sources](blender/open-world/SOURCES.md); old CC0 artwork and
software notices remain in [third-party notices](THIRD_PARTY_NOTICES.md).

## Resume checklist

- Verify the target repository's actual visibility, default branch, existing files,
  commit history and write permission before integrating or pushing. Preserve its
  visibility and history; never force-push over unknown remote contents.
- Owner confirmation of public model rights and personal/non-commercial use is
  received; retain the attribution/permission record with the project.
- Rebuild and run the project tests. Scan staged source and built assets for
  credentials, and check GitHub's per-file limits.
- Upload this project only, not sibling workspace applications or local caches.
- Use the owner's existing Vercel login, inspect the project/scope first, and create
  or link only the Survivor Runs project. Do not change other sites or billing.
- Test the actual public website in desktop/mobile-emulated Chrome/WebKit, including
  GLB/texture responses, free movement, jump/slide/fire/reload and model-byte parity.
- Only then record the real commit and verified production URL here.
