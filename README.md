![Status: Archived](https://img.shields.io/badge/status-archived-lightgrey)
[![New Project: stagedings](https://img.shields.io/badge/new%20project-stagedings-blue)](https://github.com/stefets/stagedings)

# ⚠️ Flaskdings (Archived)

**Flaskdings** is now **archived** and no longer maintained.

---

### 📦 New Project: [stagedings](https://github.com/stefets/stagedings)

Flaskdings has been refactored, renamed, and rebuilt using **FastAPI** under a new project: **stagedings**.

👉 Please use [stagedings](https://github.com/stefets/stagedings) for all future development, bug reports, and feature requests.

---

### 📚 Historical Context

Flaskdings was my original backend for scene and subscene navigation in **mididings**. It served as a simple, effective API built with Flask.

We’ve since transitioned to **stagedings**, offering:
- A modern async backend (FastAPI)
- An UI for scene and subscene navigation
- Improved WebSocket support
- Future-ready design and modularity
- Active development and support

---

### 🪦 Status

This repository is archived and read-only. No further updates will be made here.


---

# FlaskDings
## An UI and API for mididings, the community version
* It allows direct navigation through scenes and subscenes and the others commands supported by the mididings's OSC feature

# Backend
* Flask
* A mididings.LiveOSC server instance
* Flask Socket IO, allow multiple clients and realtime refresh when navigation change.
* Expose standard REST endpoints

# REST API specification
* It allows direct navigation through scenes and subscenes with REST API calls. Convenient to create your own UI

# Dependencies
* mididings community version >= 20230114 (For previous version, use the Flaskdings TAG mididings-legacy)
* Flask
* PyLiblo
* liblo
* Flask SocketIO


# Support FlaskDings
* Contributors, suggestions and PR are welcome to improve FlaskDings and mididings

# Mididings community version ressources
* https://www.github.com/mididings/mididings
* https://mididings.github.io/mididings/
* https://groups.google.com/g/mididings

# License
All files in this repository are released under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

For more details, please read the LICENSE file.