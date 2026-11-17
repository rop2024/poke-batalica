# Mini Pokémon Battle Web Application

## Goal

Build a web application where friends can create accounts, invite each other into battle rooms, choose Pokémon, take turns, and watch the battle update in real time with images, animations, music, sound effects, health bars, and battle logs.

This guide describes a practical full-stack architecture rather than a Python-only script.

## Important Scope Decision

PokeAPI is excellent for Pokémon data, sprites, artwork, moves, types, abilities, and cries. It is not a multiplayer battle server and it does not provide complete battle rules, authentication, matchmaking, or room management.

Your application should:

1. Use PokeAPI as a data source.
2. Store a local copy of the data needed by your game.
3. Implement battle rules on your own backend.
4. Treat the backend as the authority for battle results.
5. Send battle events to both players in real time.

Do not trust the browser to decide damage, winners, or valid moves.

## Recommended Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS or plain CSS modules
- React Router
- Socket.IO client
- HTML5 `<audio>` and `<img>` elements

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy or SQLModel
- PostgreSQL
- Redis for temporary room state and Socket.IO scaling
- Python Socket.IO or a WebSocket implementation

### Development Tools

- Git and GitHub
- VS Code
- Docker Compose for PostgreSQL and Redis
- Pytest for backend tests
- Vitest and React Testing Library for frontend tests
- Playwright for browser-level tests

An alternative backend is Node.js with Express/NestJS, but FastAPI is a good choice if you want to continue using Python.

## High-Level Architecture

```text
React + TypeScript frontend
        |
        | HTTPS REST API
        | WebSocket / Socket.IO
        v
FastAPI backend
        |
        +-- Battle engine
        +-- Authentication
        +-- Room management
        +-- PokeAPI synchronization
        |
        +-- PostgreSQL
        +-- Redis
```

### Responsibilities

#### Frontend

- Display Pokémon images and animations.
- Play cries, music, and battle sound effects.
- Let users create or join rooms.
- Send player choices to the backend.
- Render server-generated battle events.
- Never calculate the official battle result.

#### Backend

- Authenticate users.
- Create and manage battle rooms.
- Validate Pokémon and moves.
- Calculate damage and turn order.
- Prevent illegal actions.
- Broadcast the official result to both players.
- Save battle history.

#### Database

Store:

- Users
- Battle rooms
- Battle participants
- Teams
- Battle results
- Battle events or replay data

#### Redis

Use Redis for:

- Active room state
- WebSocket presence
- Short-lived matchmaking queues
- Multi-instance WebSocket coordination

## Suggested Project Structure

```text
pokemon-battle/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── lobby/
│   │   │   └── battle/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── types/
│   │   └── main.tsx
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── battles/
│   │   ├── database/
│   │   ├── pokemon/
│   │   ├── websocket/
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── docker-compose.yml
└── README.md
```

## Phase 1: Define the First Version

Start with a small, playable version. Avoid trying to reproduce every official game mechanic.

### Recommended MVP Rules

- Two players per room.
- Each player selects one Pokémon.
- Each Pokémon has four moves.
- Each player submits one move per turn.
- The faster Pokémon attacks first.
- Damage is calculated on the server.
- A Pokémon is defeated when HP reaches zero.
- The battle ends when one Pokémon faints.
- Players can see sprites, HP bars, move names, and a battle log.

Add teams, switching, status effects, items, matchmaking, rankings, and replays after the MVP works.

## Phase 2: Create the Frontend

From the `frontend` directory:

```bash
npm create vite@latest . -- --template react-ts
npm install
npm install react-router-dom socket.io-client
```

Create these pages:

1. `HomePage`
2. `LoginPage`
3. `LobbyPage`
4. `RoomPage`
5. `BattlePage`
6. `ResultsPage`

Create these reusable components:

- `PokemonCard`
- `PokemonSearch`
- `TeamSelector`
- `BattleArena`
- `HealthBar`
- `MoveButton`
- `BattleLog`
- `ConnectionStatus`
- `SoundToggle`

### Frontend State

Keep separate state for:

- Current user
- Current room
- Selected team
- Current battle state
- Connection status
- Sound and music preferences

Use a state library only when the application becomes difficult to manage with React state and context.

## Phase 3: Create the Backend

From the `backend` directory, create a virtual environment and install:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn[standard] pydantic sqlalchemy psycopg[binary] redis httpx python-jose passlib[bcrypt]
```

Create a basic FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI(title="Pokémon Battle API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

Run it with:

```bash
uvicorn app.main:app --reload
```

## Phase 4: Design the REST API

Suggested endpoints:

```text
POST   /auth/register
POST   /auth/login
GET    /users/me

GET    /pokemon/search?name=pika
GET    /pokemon/{name}
GET    /moves/{name}

POST   /rooms
GET    /rooms/{room_id}
POST   /rooms/{room_id}/join
POST   /rooms/{room_id}/ready
DELETE /rooms/{room_id}/leave

POST   /teams
GET    /teams
POST   /battles/{battle_id}/forfeit
GET    /battles/{battle_id}/history
```

REST is useful for setup and persistent data. Use a WebSocket for live battle actions and events.

## Phase 5: Add Real-Time Multiplayer

Create a WebSocket endpoint such as:

```text
ws://localhost:8000/ws/rooms/{room_id}
```

The frontend sends messages like:

```json
{
  "type": "submit_move",
  "move_id": 85
}
```

The backend sends messages like:

```json
{
  "type": "turn_resolved",
  "turn": 3,
  "events": [
    {
      "type": "attack",
      "attacker": "pikachu",
      "move": "thunderbolt",
      "damage": 24
    },
    {
      "type": "faint",
      "pokemon": "squirtle"
    }
  ]
}
```

Other useful event types:

```text
player_joined
player_left
player_ready
battle_started
waiting_for_opponent
move_submitted
turn_resolved
status_changed
pokemon_fainted
battle_finished
error
```

### Server-Authoritative Turn Flow

1. Player A submits a move.
2. Player B submits a move.
3. The server validates both moves.
4. The server determines turn order.
5. The server calculates the first attack.
6. The server applies damage and status effects.
7. The server calculates the second attack if the battle has not ended.
8. The server stores the new state.
9. The server broadcasts events to both players.
10. The frontend animates the events in order.

If a player disconnects, preserve the room for a short period and allow reconnection.

## Phase 6: Synchronize Pokémon Data

Use PokeAPI during development to understand the data shape:

```text
https://pokeapi.co/api/v2/pokemon/pikachu
https://pokeapi.co/api/v2/move/thunderbolt
https://pokeapi.co/api/v2/type/electric
```

Do not request PokeAPI on every battle action. Instead:

1. Create a synchronization script.
2. Download the Pokémon and move data your game supports.
3. Store the required fields in PostgreSQL.
4. Cache frequently used records.
5. Serve data from your own backend.

Store fields such as:

```text
pokemon_id
name
types
base_hp
base_attack
base_defense
base_special_attack
base_special_defense
base_speed
sprite_url
official_artwork_url
cry_url
```

PokeAPI Pokémon records include useful media fields such as:

```python
data["sprites"]["front_default"]
data["sprites"]["front_shiny"]
data["sprites"]["other"]["official-artwork"]["front_default"]
data["cries"]["latest"]
```

Cache media URLs and provide a fallback image or silent mode if a media file is unavailable.

## Phase 7: Implement the Battle Engine

Keep the battle engine independent from FastAPI and WebSocket code. This makes it easier to test.

Suggested domain objects:

```text
Battle
BattleParticipant
BattlePokemon
Move
BattleTurn
BattleEvent
```

The engine should expose operations similar to:

```python
battle.submit_move(player_id, move_id)
battle.resolve_turn()
battle.is_finished()
battle.get_events()
```

### Validate Every Action

The server should verify:

- The player belongs to the room.
- The battle is still active.
- The player has not already submitted a move.
- The move belongs to the active Pokémon.
- The Pokémon is not fainted.
- The move is allowed by the current rules.

### Damage Calculation

Start with a simple transparent formula. For example:

```text
damage = (((2 * level / 5 + 2) * power * attack / defense) / 50) + 2
damage = damage * type_effectiveness
damage = damage * random_factor
```

Add critical hits, same-type attack bonus, accuracy, status effects, abilities, and items only after the simple formula is reliable.

Keep randomness on the server and record the random result in the battle event so that replays can be reproduced.

## Phase 8: Build the Battle Screen

The battle screen can contain:

```text
┌─────────────────────────────────────┐
│ Opponent name       Opponent HP bar  │
│                         Pokémon image│
│                                     │
│          Battle animation area       │
│                                     │
│ Your Pokémon image   Your HP bar     │
│                                     │
│ Move 1  Move 2  Move 3  Move 4       │
│ Battle log             Sound toggle  │
└─────────────────────────────────────┘
```

Recommended visual states:

- Idle
- Selecting a move
- Waiting for opponent
- Attacking
- Taking damage
- Fainted
- Victory
- Defeat
- Reconnecting

The frontend should render the current server state and play animations from the event list.

## Phase 9: Add Images, Cries, Music, and Sound Effects

### Pokémon Images

Use PokeAPI sprite or official artwork URLs for:

- Player Pokémon
- Opponent Pokémon
- Team selection cards
- Search results

Preload important images before the battle begins to avoid visible delays.

### Pokémon Cries

Use the cry URL returned by PokeAPI when:

- A Pokémon enters the battle.
- A Pokémon is selected.
- A battle begins.

Browsers may block autoplay. Start audio only after a user clicks a button such as `Enter Battle` or `Enable Sound`.

### Battle Sound Effects

Use your own legally usable audio files for:

- Button clicks
- Attack impact
- Super-effective attack
- Not-very-effective attack
- Critical hit
- Fainting
- Victory
- Defeat

Keep application audio in a folder such as:

```text
frontend/public/audio/
├── click.mp3
├── hit.mp3
├── critical-hit.mp3
├── victory.mp3
└── defeat.mp3
```

Use the Web Audio API or HTML audio elements. Add:

- Master volume
- Music volume
- Effects volume
- Mute button
- Reduced-motion option

Do not assume that every user wants audio. Make sound optional and remember the preference locally.

## Phase 10: Add Lobby and Friend Battles

The easiest first multiplayer experience is a private room code.

### Room Flow

1. Player clicks `Create Room`.
2. Backend generates a short room code.
3. Player shares the code with a friend.
4. Friend enters the code and joins.
5. Both players choose teams.
6. Both players click `Ready`.
7. Backend starts the battle.

Later, add:

- Friend lists
- Online presence
- Public matchmaking
- Rematches
- Spectator mode
- Ranked and casual queues

## Phase 11: Authentication and Security

For a private prototype, simple accounts are enough. For a public application:

- Hash passwords with a standard password hashing library.
- Use short-lived access tokens and secure refresh tokens.
- Validate all request bodies with Pydantic.
- Check room membership on every action.
- Rate-limit login and room creation.
- Never expose database credentials to the frontend.
- Never trust client-provided damage or HP values.
- Use HTTPS and secure WebSocket connections in production.
- Sanitize usernames and chat messages.

If you add chat, apply message length limits, abuse reporting, blocking, and moderation controls.

## Phase 12: Testing Plan

### Backend Unit Tests

Test:

- Damage calculation
- Type effectiveness
- Turn order
- Critical hits
- Fainting
- Invalid moves
- Duplicate move submissions
- Victory and defeat

### API Tests

Test:

- Creating a room
- Joining a room
- Rejecting a full room
- Marking players ready
- Authentication failures
- Reconnecting to a battle

### Frontend Tests

Test:

- Pokémon search results
- Move selection
- Disabled buttons while waiting
- HP bar updates
- Battle log rendering
- Sound toggle
- Reconnection message

### End-to-End Tests

Use two browser contexts to verify:

1. Two users join the same room.
2. Both select a Pokémon.
3. Both submit moves.
4. Both receive the same battle result.
5. One player wins.

## Phase 13: Deployment

A simple production setup can use:

- Frontend: Vercel, Netlify, or Cloudflare Pages
- Backend: Render, Railway, Fly.io, or a VPS
- Database: managed PostgreSQL
- Redis: managed Redis service

Configure:

```text
FRONTEND_API_URL
DATABASE_URL
REDIS_URL
JWT_SECRET
ALLOWED_ORIGINS
```

Never commit `.env` files containing secrets.

Before deployment:

- Enable HTTPS.
- Configure CORS for the frontend domain.
- Use secure WebSocket URLs.
- Run database migrations.
- Add health checks.
- Add structured server logging.
- Configure error monitoring.
- Test reconnect behavior.

## Suggested Milestones

### Milestone 1: Single-Player Prototype

- Search Pokémon.
- Display image and stats.
- Display four moves.
- Play a cry.
- Run a local battle against a basic computer opponent.

### Milestone 2: Backend Battle Engine

- Move validation.
- Damage calculation.
- Turn resolution.
- Battle events.
- Unit tests.

### Milestone 3: Private Friend Rooms

- User accounts.
- Create room.
- Join by code.
- Team selection.
- Ready state.

### Milestone 4: Real-Time Battles

- WebSocket connection.
- Move submission.
- Server-authoritative results.
- Reconnection support.
- Battle log.

### Milestone 5: Presentation

- Animated sprites.
- HP bar transitions.
- Pokémon cries.
- Attack sounds.
- Music.
- Victory and defeat screens.

### Milestone 6: Production Features

- Battle history.
- Rematch.
- Matchmaking.
- Rankings.
- Spectators.
- Mobile layout.

## Recommended First Implementation Order

1. Create the React frontend and FastAPI backend.
2. Build a Pokémon search page.
3. Display sprites, official artwork, stats, moves, and cries.
4. Write a standalone battle engine with tests.
5. Add a local single-player battle.
6. Add database-backed users and rooms.
7. Add WebSocket room communication.
8. Move all battle decisions to the backend.
9. Add animations and sound effects.
10. Test two-player battles in two browser windows.
11. Deploy a private beta for friends.

## Legal and Attribution Notes

This should be treated as a fan project. Review the current terms and attribution requirements for PokeAPI, Pokémon names, artwork, sprites, cries, and any third-party audio assets before publishing publicly or monetizing the application.

Use original or properly licensed battle sound effects and music. Do not copy music or game assets that you do not have permission to redistribute.

## Final Target

The finished application should provide this experience:

1. A player signs in.
2. The player creates a room and shares the code.
3. A friend joins from another browser.
4. Both players select Pokémon.
5. The battle begins with artwork, cries, music, and animations.
6. Each player selects a move.
7. The backend resolves the turn.
8. Both screens show the same attacks, damage, sounds, and battle log.
9. The winner sees a victory screen.
10. Both players can review the battle or start a rematch.
