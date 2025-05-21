# ⚠️ Flaskdings (Archived)

![Status: Archived](https://img.shields.io/badge/status-archived-lightgrey)
[![New Project: stagedings](https://img.shields.io/badge/new%20project-stagedings-blue)](https://github.com/stefets/stagedings)

> ⚠️ **This project is archived and no longer maintained.**  
> It has been succeeded by **[stagedings](https://github.com/stefets/stagedings)** — actively developed and built with FastAPI, WebSockets, and modern UI support.

---

<details>
<summary>📖 View the original Flaskdings README</summary>

## Introduction

Flaskdings is a lightweight Python Flask web interface and REST API that interacts with the [mididings](https://github.com/mididings/mididings) MIDI router.  
It enables scene and subscene navigation via a web UI or API.

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
</details>
