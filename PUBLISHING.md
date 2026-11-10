# Survivor Runs 0.3.1 - GitHub and public Vercel release

## Live game and source

- **[Play Survivor Runs](https://survivor-runs.vercel.app)**.
- **[GitHub repository](https://github.com/Alexwatson-de/Survivor-runs)**, branch main.
- [Public software and asset credits](https://survivor-runs.vercel.app/assets/credits.txt).

The earlier network blocker is resolved. This is an actual public deployment of
0.3.1, including free exploration, supplied actors and the planted-player-motion
correction, not just a local build or a repository upload without hosting.

## Repository upload

The GitHub API confirmed the target repository was **public and empty**, with main
as its default branch, before uploading. Its visibility was preserved and there
was no existing remote history to overwrite. The local source history was pushed
normally, without force-pushing.

The application release commit is
[b683936c7ac08f6a535f28499ef7b33d8634bd4c](https://github.com/Alexwatson-de/Survivor-runs/commit/b683936c7ac08f6a535f28499ef7b33d8634bd4c).
A recursive remote Git-tree comparison matched all **368 files** in that upload
against the local commit's blob IDs. Later main-branch documentation/verification
commits preserve the same application build and record the hosted results here.

The repository includes game source, current runtime models/textures, editable
Blender workshops, authoring helpers, tests, attribution and selected review media.
Dependency caches, local provider state, environment credentials, auto-save
backups and bulk old release/capture archives are excluded. No file reaches the
100 MiB GitHub file limit. GitHub reports **zero Actions workflows**, so no workflow
was added merely to consume account minutes.

## Hosting and deployment connection

- Vercel scope: the owner's existing **Dhruv / dhruv-820e** team, **Hobby** plan.
- Separate project: **survivor-runs**, created for this request only.
- Project ID: prj_Rm1drGdn6FEwQkt9rnN3KDdZ2wIh.
- Framework: Vite; install npm ci; build npm run build; output dist.
- GitHub repository connection succeeded. The main-branch upload automatically
  created a **Ready / Production** deployment; future main pushes use that link.
- Initial verified production deployment: dpl_21ir6Vupbq8bXoBBTuc8TcVSAivX,
  [immutable deployment URL](https://survivor-runs-bln8fnhmf-dhruv-820e.vercel.app).
- Public primary alias: https://survivor-runs.vercel.app . The same project also
  has https://survivor-runs-dhruv-820e.vercel.app .

This is a static browser application. No database, multiplayer server, paid API,
new player account system, analytics service or billing/plan upgrade was added.
Other applications and Vercel projects were not modified. Hobby plan terms and
resource quotas still apply; this is not an unlimited/free-forever guarantee.

## Fresh release verification

- Production build passes and **all 132 unit/asset checks pass** again.
- The previous 16 local Chrome/WebKit world/motion workflows remain documented in
  [the motion report](PLAYER_MOTION_0.3.1.md); they are not counted again as new
  hosted tests.
- **4 fresh public browser workflows pass**, two each in actual Chromium/Chrome
  and Safari-based WebKit:
  - Normal launch without a QA hook, default rendering, idle/stop, forward and
    backward travel, lateral movement, jump, slide, short-tap fire, manual reload,
    map, RMB camera look, pause/resume and accessible public credits.
  - 390 x 844 phone emulation, responsive HUD/no horizontal overflow, two-axis
    movement, camera input, fire, release-to-stop, map and actual new motion-asset
    identity/clip names. This labelled variant uses the opt-in client QA hook for
    position/asset assertions. Chrome uses concurrent CDP touch points; WebKit's
    public automation interface uses active-pointer/RMB fallback plus a touch tap,
    not a claim of physical iPhone multitouch acceptance.
- No browser page errors or failed asset responses were observed in those journeys.
- **188 public files / 52003553 bytes** match the local tested build exactly by
  SHA-256, including HTML, JS, CSS, both zombie designs, current player GLB, textures,
  UI images, particle texture, manifest and credits. Public manifest is revision
  0.3.1, forcedForwardMotion=false and playerMotion.distanceDriven=true.
- Configured nosniff, frame DENY and strict-origin-when-cross-origin response
  headers are present. Actual /.env, /.env.local, /.git/config and
  /.vercel/project.json requests return **404**, not credentials/source state.
- Default desktop and mobile-emulated rendered screenshots were visually inspected.

Evidence:
- [Local build](artifacts/publishing/build.log), [132 checks](artifacts/publishing/tests.log).
- [Hosted browser log](artifacts/publishing/hosted-browser.log) and
  [structured results](artifacts/publishing/hosted-results.json).
- [All hosted file hashes / exposure checks](artifacts/publishing/hosted-asset-parity.json).
- [Chrome desktop](artifacts/publishing/hosted-chrome-desktop.png),
  [Chrome phone emulation](artifacts/publishing/hosted-chrome-mobile.png),
  [WebKit desktop](artifacts/publishing/hosted-webkit-desktop.png),
  [WebKit phone emulation](artifacts/publishing/hosted-webkit-mobile.png).
- [Staged-source credential/size preflight](artifacts/publishing/staged-preflight.json).

## Authentication and asset permission

The owner explicitly confirmed **personal/non-commercial use and permission to
publicly redistribute the supplied cowboy model/derivative GLBs**, including with
the public game/source repository, on 2026-11-10. This release relies on that owner
confirmation. The cowboy's publisher license is not independently verified or
invented. Both zombie packages retain their embedded CC BY 4.0 authors, source links,
license and modification notices. See [asset sources](blender/open-world/SOURCES.md)
and [third-party notices](THIRD_PARTY_NOTICES.md).

The supplied GitHub token was used through temporary process authentication only;
it was not saved in Git configuration, a remote URL, source files or build assets.
Git's credential helper was not used to persist it. Vercel used the existing CLI
login. The CLI-generated short-lived project OIDC environment file and provider
settings remain local, ignored and excluded from both Git and deployed output.
Staged source and the built/public files were scanned before release.

**Revoke the chat-shared GitHub token now.** Future local pushes should use secure
Git credential-manager/CLI authentication; Vercel's connected GitHub integration
does not require leaving that token in this repository.

## Limits

Browser progress is per-origin/device. Old localhost saves remain intact but do
not automatically transfer to the new HTTPS site. The map is finite, level-ground
focused and single-player. Physical phones, broad hardware/FPS/thermal behavior,
human input/animation/audio acceptance and long-soak balance remain separate gates;
no AAA or universal 60 FPS claim is made.
