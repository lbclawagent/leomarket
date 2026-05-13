These are three separate plugin failures in ClawX/openclaw, each with a different root cause. Let me break them down:

---

**1. `google` plugin — missing `@mariozechner/pi-ai`**

This is a missing npm dependency that the bundled plugin expects but isn't installed in the runtime deps folder.

```bash
cd ~/.openclaw/plugin-runtime-deps/openclaw-2026.4.23-33e586854062
npm install @mariozechner/pi-ai
```

If that package is private or doesn't exist on npm, this plugin may be broken in this version of openclaw and you'd need to wait for an update or disable it.

---

**2. `memory-core` plugin — missing `typebox`**

Same class of problem — a missing bundled dep.

```bash
cd ~/.openclaw/plugin-runtime-deps/openclaw-2026.4.23-33e586854062
npm install typebox
```

Note: the correct package name might be `@sinclair/typebox` (that's the standard one). Try that if plain `typebox` fails:

```bash
npm install @sinclair/typebox
```

---

**3. `context-mode` plugin — Node.js version mismatch (NODE_MODULE_VERSION 147 vs 143)**

This is the most common native module issue. The `better-sqlite3` binary was compiled for a different Node version than what openclaw is running.

Fix: rebuild the native module against the current Node version.

```bash
cd ~/.openclaw/extensions/context-mode
# or wherever the workspace copy lives:
cd ~/.openclaw/workspace/leopump/context-mode

npm rebuild better-sqlite3
# or
npm install better-sqlite3 --build-from-source
```

If `npm rebuild` doesn't work (e.g. wrong node-gyp config), try:

```bash
npx node-gyp rebuild --directory node_modules/better-sqlite3
```

---

**Root cause summary**

| Plugin | Error type | Fix |
|---|---|---|
| `google` | Missing npm dep | `npm install @mariozechner/pi-ai` in runtime-deps |
| `memory-core` | Missing npm dep | `npm install @sinclair/typebox` in runtime-deps |
| `context-mode` | Native module compiled for wrong Node | `npm rebuild better-sqlite3` in the plugin dir |

---

**If none of the above work**, the cleanest fix is often to just reinstall openclaw's plugin runtime entirely:

```bash
rm -rf ~/.openclaw/plugin-runtime-deps/openclaw-2026.4.23-33e586854062
# Then relaunch ClawX — it should re-download and reinstall bundled deps fresh
```

And for `context-mode` specifically, check which Node version openclaw bundles vs. your system Node:

```bash
node --version        # your system Node
# NODE_MODULE_VERSION 143 = Node ~22.x
# NODE_MODULE_VERSION 147 = Node ~23.x or 24.x
```

If there's a mismatch, the plugin was built against a newer Node than openclaw ships with. You may need to downgrade the plugin or wait for a compatible release.